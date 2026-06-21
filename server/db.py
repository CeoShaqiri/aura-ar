"""
Aura Monolith DB — Async database layer using asyncpg + SQLAlchemy Core.

All external code should use the functions in this module — never
import asyncpg or the engine directly from main.py.

Connection pool is initialised once at FastAPI startup (lifespan).
The database is only reachable on the internal Docker network (host "db"),
never exposed to the public internet.
"""

import hashlib
import hmac
import os
import uuid
from datetime import date, datetime
from typing import Optional

import asyncpg

# ─────────────────────────────────────────────────────────────────────────────
# Config — provided by docker-compose environment
# ─────────────────────────────────────────────────────────────────────────────
DB_DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://aura:aura_secret@db:5432/aura",
)

# HMAC salt — override via env in production for extra security
_HMAC_SALT = os.environ.get("AURA_HMAC_SALT", "aura-salt").encode()

# Tier export limits (exports per month)
TIER_LIMITS = {
    "legacy_grant": 25,
    "pro":          500,
    "agency":       2_000,
    "sovereign":    999_999,
}

# ─────────────────────────────────────────────────────────────────────────────
# Connection pool — managed by lifespan
# ─────────────────────────────────────────────────────────────────────────────
_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> None:
    """Create the asyncpg connection pool. Called once at app startup."""
    global _pool
    _pool = await asyncpg.create_pool(
        dsn=DB_DSN,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )


async def close_pool() -> None:
    """Gracefully close all connections. Called at app shutdown."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def _pool_required() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool not initialised — did startup run?")
    return _pool


# ─────────────────────────────────────────────────────────────────────────────
# Key hashing
# ─────────────────────────────────────────────────────────────────────────────

def hash_api_key(api_key: str) -> str:
    """HMAC-SHA256 of the raw key. Raw key is NEVER stored."""
    return hmac.new(_HMAC_SALT, api_key.encode(), hashlib.sha256).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────

async def get_user_by_key_hash(key_hash: str) -> Optional[asyncpg.Record]:
    pool = _pool_required()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE api_key_hash = $1", key_hash
        )


async def upsert_user(
    email: str,
    full_name: str,
    api_key: str,
    verified_status: str = "active",
) -> asyncpg.Record:
    """Insert or update a user row; returns the full row."""
    pool     = _pool_required()
    key_hash = hash_api_key(api_key)
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO users (email, full_name, api_key_hash, verified_status)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (api_key_hash) DO UPDATE
                SET full_name       = EXCLUDED.full_name,
                    email           = EXCLUDED.email,
                    verified_status = EXCLUDED.verified_status
            RETURNING *
            """,
            email, full_name, key_hash, verified_status,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Subscriptions
# ─────────────────────────────────────────────────────────────────────────────

async def get_subscription(user_id: str) -> Optional[asyncpg.Record]:
    pool = _pool_required()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM subscriptions WHERE user_id = $1", uuid.UUID(user_id)
        )


async def check_and_increment_export(user_id: str) -> dict:
    """
    Thread-safe: reset monthly count if needed, check limit, then increment.

    Returns:
      {"allowed": True,  "export_count": N, "export_limit": M}
      {"allowed": False, "export_count": N, "export_limit": M, "reason": "..."}
    """
    pool = _pool_required()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT * FROM subscriptions WHERE user_id = $1 FOR UPDATE",
                uuid.UUID(user_id),
            )
            if row is None:
                return {"allowed": False, "export_count": 0, "export_limit": 0,
                        "reason": "No active subscription found."}

            # ── Monthly reset ──────────────────────────────────────────
            today      = date.today()
            last_reset = row["last_reset"]
            new_count  = row["export_count"]
            if last_reset.year != today.year or last_reset.month != today.month:
                new_count = 0
                await conn.execute(
                    "UPDATE subscriptions SET export_count=0, last_reset=$1 WHERE user_id=$2",
                    today, uuid.UUID(user_id),
                )

            # ── Contract expiry check ──────────────────────────────────
            contract_end = row["contract_end_date"]
            if contract_end and contract_end < today:
                await conn.execute(
                    "UPDATE users SET verified_status='expired' WHERE id=$1",
                    uuid.UUID(user_id),
                )
                return {"allowed": False, "export_count": new_count,
                        "export_limit": row["export_limit"],
                        "reason": "Your subscription has expired."}

            # ── Export limit check ─────────────────────────────────────
            if new_count >= row["export_limit"]:
                return {"allowed": False, "export_count": new_count,
                        "export_limit": row["export_limit"],
                        "reason": f"Monthly export limit of {row['export_limit']} reached. "
                                  "Resets on the 1st of next month."}

            # ── Increment ──────────────────────────────────────────────
            await conn.execute(
                "UPDATE subscriptions SET export_count = export_count + 1 WHERE user_id = $1",
                uuid.UUID(user_id),
            )
            return {
                "allowed":       True,
                "export_count":  new_count + 1,
                "export_limit":  row["export_limit"],
            }


async def upsert_subscription(
    user_id: str,
    tier: str = "legacy_grant",
    contract_end_date: Optional[date] = None,
    stripe_sub_id: Optional[str] = None,
) -> asyncpg.Record:
    pool  = _pool_required()
    limit = TIER_LIMITS.get(tier, 25)
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO subscriptions (user_id, tier, export_limit, contract_end_date, stripe_sub_id)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE
                SET tier              = EXCLUDED.tier,
                    export_limit      = EXCLUDED.export_limit,
                    contract_end_date = EXCLUDED.contract_end_date,
                    stripe_sub_id     = COALESCE(EXCLUDED.stripe_sub_id, subscriptions.stripe_sub_id)
            RETURNING *
            """,
            uuid.UUID(user_id), tier, limit, contract_end_date, stripe_sub_id,
        )


# unique constraint needed for upsert_subscription ON CONFLICT (user_id)
# Add this to migrations if not present:
#   ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_id_unique UNIQUE (user_id);


# ─────────────────────────────────────────────────────────────────────────────
# Assets
# ─────────────────────────────────────────────────────────────────────────────

async def insert_asset(
    user_id: str,
    scene_name: str,
    glb_path: str,
    viewer_url: str,
    file_size: int,
    draco_enabled: bool = False,
) -> asyncpg.Record:
    """Record a new uploaded asset. Returns the created row."""
    pool = _pool_required()
    qr_url = viewer_url  # QR code will deep-link to the viewer URL
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO assets
                (user_id, scene_name, glb_path, qr_code_url, viewer_url, file_size, draco_enabled)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
            """,
            uuid.UUID(user_id), scene_name, glb_path, qr_url,
            viewer_url, file_size, draco_enabled,
        )


async def get_user_assets(user_id: str, limit: int = 50) -> list[asyncpg.Record]:
    pool = _pool_required()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM assets WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2",
            uuid.UUID(user_id), limit,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Legacy Grant Applications
# ─────────────────────────────────────────────────────────────────────────────

async def insert_legacy_grant_application(
    full_name: str,
    email: str,
    billing_name: str,
    country: str,
    reason: str,
    ocr_result: str,
    identity_match: bool,
    status: str = "pending",
) -> asyncpg.Record:
    pool = _pool_required()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO legacy_grant_applications
                (full_name, email, billing_name, country, reason,
                 ocr_result, identity_match, status)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            RETURNING *
            """,
            full_name, email, billing_name, country, reason,
            ocr_result, identity_match, status,
        )


async def update_legacy_grant_status(
    application_id: str,
    status: str,
    stripe_link: str = "",
) -> None:
    pool = _pool_required()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE legacy_grant_applications SET status=$1, stripe_link=$2 WHERE id=$3",
            status, stripe_link, uuid.UUID(application_id),
        )
