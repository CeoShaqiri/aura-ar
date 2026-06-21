"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

const TIER_NAMES: Record<string, string> = {
  "pro-monthly": "Aura Pro",
  "agency-monthly": "Aura Agency",
  "sovereign-monthly": "Aura Sovereign",
  "sovereign-annual": "Aura Sovereign Annual",
  "sovereign-installment-1": "Aura Sovereign 3-Part Plan",
};

function SuccessContent() {
  const params = useSearchParams();
  const tier = params.get("tier") ?? "";
  const name = TIER_NAMES[tier] ?? "Aura AR";

  return (
    <main className="relative min-h-screen bg-black flex items-center justify-center px-6">
      {/* Glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(201,168,76,0.06), transparent)",
        }}
        aria-hidden
      />

      <div
        className="relative z-10 max-w-lg w-full text-center glass rounded-3xl p-12"
        style={{
          boxShadow:
            "0 0 0 1px rgba(172,123,120,0.22), 0 40px 100px rgba(30,12,20,0.7)",
        }}
      >
        {/* Top accent */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#AC7B78] to-transparent rounded-t-3xl" />

        {/* Diamond icon */}
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          className="mx-auto mb-6"
          aria-hidden
        >
          <polygon
            points="24,3 45,24 24,45 3,24"
            stroke="#AC7B78"
            strokeWidth="1.5"
            fill="rgba(172,123,120,0.1)"
          />
          <polyline
            points="16,24 21,29 32,18"
            stroke="#AC7B78"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        </svg>

        <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
          Payment confirmed
        </p>
        <h1 className="text-3xl font-extralight text-white mb-4">
          Welcome to {name}.
        </h1>
        <p className="text-white/40 text-base leading-relaxed mb-8">
          Your API key and Monolith node will be provisioned within 24 hours.
          Check your inbox for onboarding instructions.
        </p>

        <div className="flex flex-col gap-3">
          <a
            href="/"
            className="py-3.5 rounded-full text-sm tracking-widest uppercase font-light text-[#472830] transition-all duration-300"
            style={{
              background: "linear-gradient(135deg, #AC7B78, #C4948F, #AC7B78)",
            }}
          >
            Back to Aura
          </a>
          <a
            href="mailto:hello@aura-intelligence.ch"
            className="py-3.5 rounded-full text-sm tracking-widest uppercase font-light text-white/40 hover:text-white transition-colors"
            style={{ border: "1px solid rgba(255,255,255,0.08)" }}
          >
            Contact Onboarding
          </a>
        </div>
      </div>
    </main>
  );
}

export default function CheckoutSuccess() {
  return (
    <Suspense>
      <SuccessContent />
    </Suspense>
  );
}
