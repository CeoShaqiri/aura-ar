-- ============================================================================
-- Aura Monolith DB  —  Migration 001: Initial Schema
-- Run once against the Postgres container:
--   docker exec -i server-db-1 psql -U aura -d aura < migrations/001_init.sql
-- ============================================================================

-- Enable uuid generation extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────────────
-- USERS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT        NOT NULL UNIQUE,
    full_name       TEXT        NOT NULL DEFAULT '',
    -- api_key_hash: HMAC-SHA256 of the raw API key — raw key never stored
    api_key_hash    TEXT        NOT NULL UNIQUE,
    verified_status TEXT        NOT NULL DEFAULT 'pending'
                                CHECK (verified_status IN ('pending','active','suspended','expired')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_api_key_hash ON users(api_key_hash);
CREATE INDEX IF NOT EXISTS idx_users_email        ON users(email);

-- ─────────────────────────────────────────────────────────────────────────────
-- SUBSCRIPTIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS subscriptions (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier              TEXT        NOT NULL DEFAULT 'free'
                                  CHECK (tier IN ('legacy_grant','pro','agency','sovereign')),
    start_date        DATE        NOT NULL DEFAULT CURRENT_DATE,
    contract_end_date DATE,                         -- NULL = rolling monthly
    export_count      INTEGER     NOT NULL DEFAULT 0,
    export_limit      INTEGER     NOT NULL DEFAULT 25, -- Legacy Grant: 25/mo; Pro: 500; etc.
    -- Resets on the 1st of each month; last_reset tracks when
    last_reset        DATE        NOT NULL DEFAULT CURRENT_DATE,
    stripe_sub_id     TEXT,                          -- Stripe subscription ID for auto-renewal
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subs_user_id ON subscriptions(user_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- ASSETS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS assets (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scene_name    TEXT        NOT NULL DEFAULT 'Untitled',
    glb_path      TEXT        NOT NULL,              -- absolute path on server disk
    qr_code_url   TEXT        NOT NULL DEFAULT '',   -- public URL for QR deep-link
    viewer_url    TEXT        NOT NULL DEFAULT '',   -- public viewer URL
    file_size     BIGINT      NOT NULL DEFAULT 0,    -- bytes
    draco_enabled BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_user_id    ON assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_created_at ON assets(created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- LEGACY GRANT APPLICATIONS
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS legacy_grant_applications (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          UUID        REFERENCES users(id) ON DELETE SET NULL,
    full_name        TEXT        NOT NULL,
    email            TEXT        NOT NULL,
    billing_name     TEXT        NOT NULL,
    country          TEXT        NOT NULL DEFAULT '',
    reason           TEXT        NOT NULL DEFAULT '',
    ocr_result       TEXT        NOT NULL DEFAULT '',  -- raw extracted name
    identity_match   BOOLEAN     NOT NULL DEFAULT FALSE,
    status           TEXT        NOT NULL DEFAULT 'pending'
                                 CHECK (status IN ('pending','approved','rejected')),
    stripe_link      TEXT        NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────────────────────
-- HELPER: auto-update updated_at on users + subscriptions
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION _set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_users_updated_at        ON users;
DROP TRIGGER IF EXISTS trg_subscriptions_updated_at ON subscriptions;

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION _set_updated_at();

CREATE TRIGGER trg_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION _set_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- HELPER: reset export_count on the 1st of each month
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION reset_monthly_export_counts()
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE subscriptions
    SET    export_count = 0,
           last_reset   = CURRENT_DATE
    WHERE  last_reset < DATE_TRUNC('month', CURRENT_DATE);
END;
$$;
