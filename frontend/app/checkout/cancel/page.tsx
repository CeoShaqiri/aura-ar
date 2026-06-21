"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function CancelContent() {
  const params = useSearchParams();
  const tier = params.get("tier") ?? "";

  return (
    <main className="relative min-h-screen bg-black flex items-center justify-center px-6">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 40% at 50% 50%, rgba(201,168,76,0.04), transparent)",
        }}
        aria-hidden
      />

      <div
        className="relative z-10 max-w-lg w-full text-center glass rounded-3xl p-12"
        style={{
          boxShadow:
            "0 0 0 1px rgba(255,255,255,0.06), 0 40px 100px rgba(0,0,0,0.7)",
        }}
      >
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          className="mx-auto mb-6 opacity-50"
          aria-hidden
        >
          <polygon
            points="24,3 45,24 24,45 3,24"
            stroke="#AC7B78"
            strokeWidth="1.5"
            fill="none"
          />
        </svg>

        <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
          Payment cancelled
        </p>
        <h1 className="text-3xl font-extralight text-white mb-4">
          No charge was made.
        </h1>
        <p className="text-white/40 text-base leading-relaxed mb-8">
          You can return to the pricing page and try again whenever you are
          ready. If you ran into an issue, reach out and we will sort it.
        </p>

        <div className="flex flex-col gap-3">
          <a
            href={`/#pricing`}
            className="py-3.5 rounded-full text-sm tracking-widest uppercase font-light text-[#472830] transition-all duration-300"
            style={{
              background: "linear-gradient(135deg, #AC7B78, #C4948F, #AC7B78)",
            }}
          >
            Back to Pricing
          </a>
          <a
            href="mailto:hello@aura-intelligence.ch"
            className="py-3.5 rounded-full text-sm tracking-widest uppercase font-light text-white/40 hover:text-white transition-colors"
            style={{ border: "1px solid rgba(255,255,255,0.08)" }}
          >
            Get Help
          </a>
        </div>
      </div>
    </main>
  );
}

export default function CheckoutCancel() {
  return (
    <Suspense>
      <CancelContent />
    </Suspense>
  );
}
