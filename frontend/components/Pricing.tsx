"use client";

import { useState } from "react";

// ── Payment badge helper ────────────────────────────────────────────────────
function PayBadge({ label, icon }: { label: string; icon: string }) {
  return (
    <span
      title={label}
      aria-label={label}
      className="inline-flex items-center justify-center rounded-md px-2.5 py-1.5 bg-white/[0.06] border border-white/[0.08] text-white/50 text-[10px] tracking-wide select-none"
    >
      {icon}
    </span>
  );
}

const PAYMENT_BADGES = [
  { label: "Visa", icon: "VISA" },
  { label: "Mastercard", icon: "MC" },
  { label: "Apple Pay", icon: "⌘ Pay" },
  { label: "Google Pay", icon: "G Pay" },
  { label: "Klarna", icon: "Klarna" },
  { label: "Affirm", icon: "Affirm" },
  { label: "Afterpay", icon: "Afterpay" },
  { label: "SEPA", icon: "SEPA" },
  { label: "Wire", icon: "Wire" },
  { label: "Bitcoin", icon: "₿" },
  { label: "USDC", icon: "USDC" },
  { label: "Link", icon: "Link" },
];

async function startCheckout(
  tier: string,
  setLoading: (t: string | null) => void,
) {
  setLoading(tier);
  try {
    const res = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tier }),
    });
    const data = await res.json();
    if (data.url) {
      window.location.href = data.url;
    } else {
      alert(
        data.error ??
          "Checkout unavailable — contact hello@theaurastandard.com",
      );
    }
  } catch {
    alert(
      "Network error — please try again or contact hello@theaurastandard.com",
    );
  } finally {
    setLoading(null);
  }
}

const TIERS = [
  {
    id: "pro-monthly",
    name: "The Aura Standard Pro",
    price: "$499",
    period: "/mo",
    tagline:
      "For Elite Creators. Your 1:1 Live-Link access to the Aura Logic Core.",
    badge: null as string | null,
    features: [
      "1-click Blender → AR (world's first)",
      "No app install ever needed",
      "No cloud — your own Aura Monolith node",
      "Unlimited GLB deployments",
      "Permanent AR links — never expire",
      "Auto-optimize: decimate + UV unwrap",
      "Auto texture resize to AR-safe limits",
      "500 GB private model vault",
      "WebXR — Safari, Chrome, any device",
      "48h SLA support",
    ],
    unavailable: ["White-label portals", "Custom domain", "Multi-seat"],
    cta: "Start with Pro",
    highlight: false,
  },
  {
    id: "agency-monthly",
    name: "The Aura Standard Agency",
    price: "$1,999",
    period: "/mo",
    tagline:
      "For Digital Agencies. High-volume exports with priority Monolith throughput.",
    badge: "Most Popular" as string | null,
    features: [
      "Everything in Pro",
      "5 Addon seats (team members)",
      "Custom domain overlay on AR links",
      "5 client sub-accounts",
      "5 TB model vault",
      "12h SLA support",
      "Priority onboarding call",
    ],
    unavailable: ["White-label portals"],
    cta: "Join as Agency",
    highlight: true,
  },
  {
    id: "sovereign-monthly",
    name: "The Aura Standard Sovereign",
    price: "$4,999",
    period: "/mo",
    tagline:
      "Full White-Label Infrastructure. Your IP. Your brand. Zero public cloud.",
    badge: null as string | null,
    features: [
      "Everything in Agency",
      "Unlimited Addon seats",
      "Full white-label client portals",
      "Unlimited client sub-accounts",
      "Unlimited model vault",
      "Dedicated hardware — not shared",
      "On-prem deploy option",
      "2h SLA + named Aura engineer",
    ],
    unavailable: [],
    cta: "Request Sovereign",
    highlight: false,
  },
];

export default function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);
  return (
    <section id="pricing" className="relative py-32 px-6 overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[600px] rounded-full opacity-10 blur-[120px] pointer-events-none"
        style={{ background: "radial-gradient(ellipse, #AC7B78, transparent)" }}
        aria-hidden
      />

      {/* Header */}
      <div className="max-w-3xl mx-auto text-center mb-6" data-reveal>
        <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-5">
          World&apos;s First Blender-to-AR Pipeline
        </p>
        <h2 className="text-4xl md:text-5xl font-extralight text-white leading-tight">
          The World&apos;s First Vertically Integrated
          <br />
          <span className="text-gold">AR Pipeline.</span>
          <br />
          <span className="text-white/30">Pick your tier.</span>
        </h2>
        <p className="mt-6 text-white/35 text-lg font-light leading-relaxed">
          One button in Blender. Your model lives in AR on any phone in 90
          seconds. No export dialog. No cloud subscription. No app install.
          Ever.
        </p>
      </div>

      {/* Payment badges */}
      <div
        className="max-w-3xl mx-auto flex flex-wrap justify-center gap-2 mb-16"
        data-reveal
      >
        {PAYMENT_BADGES.map((b) => (
          <PayBadge key={b.label} label={b.label} icon={b.icon} />
        ))}
      </div>

      {/* Tier cards */}
      <div
        className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6"
        data-reveal-group
      >
        {TIERS.map((tier) => (
          <div
            key={tier.id}
            className="glass noise rounded-3xl p-8 flex flex-col relative overflow-hidden"
            style={{
              boxShadow: tier.highlight
                ? "0 0 0 1px rgba(172,123,120,0.4), 0 32px 80px rgba(30,12,20,0.7), inset 0 1px 0 rgba(172,123,120,0.12)"
                : "0 0 0 1px rgba(172,123,120,0.1), 0 24px 60px rgba(30,12,20,0.5)",
            }}
          >
            {tier.highlight && (
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#AC7B78] to-transparent" />
            )}
            {tier.highlight && (
              <span className="absolute top-4 right-4 text-[9px] tracking-widest uppercase text-[#472830] bg-[#AC7B78] px-3 py-1 rounded-full font-medium">
                Most Popular
              </span>
            )}

            <p className="text-gold text-[10px] tracking-[0.4em] uppercase mb-3">
              {tier.name}
            </p>
            <div className="flex items-end gap-1 mb-2">
              <span className="text-white text-4xl font-extralight">
                {tier.price}
              </span>
              <span className="text-white/30 text-sm mb-1">{tier.period}</span>
            </div>
            <p className="text-white/40 text-sm mb-8 leading-relaxed">
              {tier.tagline}
            </p>

            {/* Divider */}
            <div className="h-px bg-white/[0.06] mb-6" />

            {/* Features */}
            <ul className="space-y-2.5 flex-1 mb-6">
              {tier.features.map((f) => (
                <li
                  key={f}
                  className="flex items-start gap-2.5 text-sm text-white/60"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 14 14"
                    fill="none"
                    className="mt-0.5 shrink-0"
                    aria-hidden
                  >
                    <polygon
                      points="7,1 13,7 7,13 1,7"
                      stroke="#AC7B78"
                      strokeWidth="1"
                      fill="rgba(172,123,120,0.15)"
                    />
                  </svg>
                  {f}
                </li>
              ))}
              {tier.unavailable.map((f) => (
                <li
                  key={f}
                  className="flex items-start gap-2.5 text-sm text-white/20 line-through"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 14 14"
                    fill="none"
                    className="mt-0.5 shrink-0 opacity-30"
                    aria-hidden
                  >
                    <line
                      x1="3"
                      y1="3"
                      x2="11"
                      y2="11"
                      stroke="white"
                      strokeWidth="1.2"
                    />
                    <line
                      x1="11"
                      y1="3"
                      x2="3"
                      y2="11"
                      stroke="white"
                      strokeWidth="1.2"
                    />
                  </svg>
                  {f}
                </li>
              ))}
            </ul>

            <button
              onClick={() => startCheckout(tier.id, setLoading)}
              disabled={loading === tier.id}
              className="w-full text-center py-3.5 rounded-full text-sm tracking-widest uppercase font-light transition-all duration-300 disabled:opacity-60 disabled:cursor-wait"
              style={
                tier.highlight
                  ? {
                      background:
                        "linear-gradient(135deg, #AC7B78, #C4948F, #AC7B78)",
                      color: "#472830",
                    }
                  : {
                      border: "1px solid rgba(172,123,120,0.35)",
                      color: "#AC7B78",
                    }
              }
            >
              {loading === tier.id ? "Redirecting…" : tier.cta}
            </button>
            <p className="mt-3 text-center text-white/20 text-[10px]">
              Card · Apple Pay · Google Pay · Klarna · Link
            </p>
          </div>
        ))}
      </div>

      {/* ── Founders Pass — Annual / Installment ───────────────────────── */}
      <div className="max-w-3xl mx-auto mt-20" data-reveal>
        <div
          className="glass noise rounded-3xl p-10 relative overflow-hidden"
          style={{
            boxShadow:
              "0 0 0 1px rgba(172,123,120,0.22), 0 40px 100px rgba(30,12,20,0.8), inset 0 1px 0 rgba(255,255,255,0.04)",
          }}
        >
          {/* Top accent line */}
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#AC7B78] to-transparent" />

          {/* Glow */}
          <div
            className="absolute -top-16 left-1/2 -translate-x-1/2 w-72 h-72 rounded-full opacity-15 blur-3xl pointer-events-none"
            style={{
              background: "radial-gradient(circle, #AC7B78, transparent)",
            }}
            aria-hidden
          />

          <div className="relative text-center">
            <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
              The Aura Standard Sovereign Annual Pass — Full White-Label
            </p>
            <h3 className="text-3xl md:text-4xl font-extralight text-white mb-2">
              The Founders Guild.
              <br />
              Lock in Total Sovereignty.
            </h3>
            <p className="text-white/35 text-base mb-8 leading-relaxed">
              Pre-pay annually and save ~$4,000/yr. Or split across three
              payments — no interest, no approval. Immediate Monolith
              provisioning on payment one.
            </p>

            {/* Price comparison */}
            <div className="flex justify-center gap-10 mb-10">
              <div className="text-center">
                <p className="text-white/20 text-sm line-through">
                  $59,988/yr at monthly rate
                </p>
                <p className="text-white text-2xl font-extralight mt-1">
                  $19,990
                </p>
                <p className="text-white/40 text-xs tracking-widest uppercase mt-1">
                  Annual Pre-Pay · Save ~$40k
                </p>
              </div>
              <div className="h-12 w-px bg-white/10 self-center" />
              <div className="text-center">
                <p className="text-white/20 text-sm">3 × installments</p>
                <p className="text-white text-2xl font-extralight mt-1">
                  $6,999
                </p>
                <p className="text-white/40 text-xs tracking-widest uppercase mt-1">
                  Today · then 2 × $6,999
                </p>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => startCheckout("sovereign-annual", setLoading)}
                disabled={loading === "sovereign-annual"}
                className="px-8 py-4 rounded-full text-sm tracking-widest uppercase font-light text-[#472830] transition-all duration-300 hover:shadow-[0_0_40px_rgba(172,123,120,0.45)] disabled:opacity-60 disabled:cursor-wait"
                style={{
                  background:
                    "linear-gradient(135deg, #AC7B78, #C4948F, #AC7B78)",
                }}
              >
                {loading === "sovereign-annual"
                  ? "Redirecting…"
                  : "$19,990 — Annual Pre-Pay"}
              </button>
              <button
                onClick={() =>
                  startCheckout("sovereign-installment-1", setLoading)
                }
                disabled={loading === "sovereign-installment-1"}
                className="px-8 py-4 rounded-full text-sm tracking-widest uppercase font-light transition-all duration-300 disabled:opacity-60 disabled:cursor-wait"
                style={{
                  border: "1px solid rgba(172,123,120,0.4)",
                  color: "#AC7B78",
                }}
              >
                {loading === "sovereign-installment-1"
                  ? "Redirecting…"
                  : "$6,999 Today (3-Part Plan)"}
              </button>
            </div>

            <div className="mt-8 pt-8 border-t border-white/[0.06]">
              <p className="text-white/25 text-xs mb-3 tracking-widest uppercase">
                Accepted payment methods
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {PAYMENT_BADGES.map((b) => (
                  <PayBadge key={b.label} label={b.label} icon={b.icon} />
                ))}
              </div>
              <p className="mt-4 text-white/15 text-xs">
                Powered by Stripe · 256-bit SSL · PCI DSS compliant · Apple Pay
                &amp; Google Pay available in supported browsers
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
