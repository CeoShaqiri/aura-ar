import type { Metadata } from "next";
import VerifyForm from "@/components/VerifyForm";

export const metadata: Metadata = {
  title: "The Aura Standard Legacy Grant — For Students & Low-Income Creators",
  description:
    "25 Secure AR Exports/month for $49/mo on a 24-month plan. Identity-verified. The same Aura Standard infrastructure — accessible to everyone.",
};

const GRANT_DETAILS = [
  {
    icon: "◉",
    title: "25 Exports / Month",
    body: "Full GLB deployments to your dedicated Aura node. Same pipeline, same AR quality as any paid tier.",
  },
  {
    icon: "◐",
    title: "$49 / Month · 24 Months",
    body: "No hidden fees. No upsells. Cancel at month 24 or upgrade to a full tier.",
  },
  {
    icon: "⬡",
    title: "Identity Verified",
    body: "Adobe-style OCR verification. The name on your ID must match your billing name 1:1.",
  },
  {
    icon: "◆",
    title: "No Cloud. No App.",
    body: "Same The Aura Standard infrastructure. Your models never touch public cloud servers.",
  },
];

export default function LegacyGrantPage() {
  return (
    <main className="relative min-h-screen bg-plum overflow-x-hidden">
      {/* Grid */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.025]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(172,123,120,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(172,123,120,0.12) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
        aria-hidden
      />

      {/* ── Nav ─────────────────────────────────────────────────────────── */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-5 glass border-b"
        style={{ borderColor: "rgba(172,123,120,0.12)" }}
      >
        <a href="/" className="flex items-center gap-3">
          <svg
            width="18"
            height="18"
            viewBox="0 0 40 40"
            fill="none"
            aria-hidden
          >
            <polygon
              points="20,2 38,20 20,38 2,20"
              stroke="#AC7B78"
              strokeWidth="1.5"
              fill="rgba(172,123,120,0.1)"
            />
          </svg>
          <span className="brand-wordmark text-gold">The Aura Standard</span>
        </a>

        <a
          href="/#pricing"
          className="text-xs tracking-widest uppercase px-5 py-2.5 rounded-full transition-all duration-300 hover:bg-[rgba(172,123,120,0.12)] text-white/35 hover:text-white"
          style={{ border: "1px solid rgba(172,123,120,0.2)" }}
        >
          Back to Pricing
        </a>
      </nav>

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section className="relative pt-36 pb-20 px-8 max-w-5xl mx-auto">
        {/* Glow */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] rounded-full opacity-15 blur-[120px] pointer-events-none"
          style={{
            background: "radial-gradient(ellipse, #AC7B78, transparent)",
          }}
          aria-hidden
        />

        <div className="relative text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-3 mb-8">
            <div className="h-px w-10 bg-gradient-to-r from-transparent to-[#AC7B78]" />
            <span className="text-gold text-[10px] tracking-[0.5em] uppercase">
              The Aura Standard Legacy Grant
            </span>
            <div className="h-px w-10 bg-gradient-to-l from-transparent to-[#AC7B78]" />
          </div>

          <h1 className="text-4xl md:text-6xl font-extralight text-white leading-[1.05] tracking-tight mb-6">
            The World&apos;s First AR Pipeline.
            <br />
            <span className="text-gold">For Everyone.</span>
          </h1>

          <p className="text-white/40 text-lg leading-relaxed mb-4">
            Students and low-income creators deserve the same tools as elite
            studios. The Aura Legacy Grant gives you access to the full Aura
            Monolith pipeline — identity-verified, no compromise on quality.
          </p>

          <div className="flex flex-wrap justify-center gap-10 mt-8">
            {[
              { value: "25", label: "Exports / month" },
              { value: "$49", label: "Per month" },
              { value: "24mo", label: "Grant period" },
              { value: "0", label: "App installs needed" },
            ].map((s) => (
              <div key={s.label} className="flex flex-col items-center gap-1">
                <span className="text-gold text-2xl font-light">{s.value}</span>
                <span className="text-white/25 text-[10px] tracking-widest uppercase">
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Feature grid ────────────────────────────────────────────────── */}
      <section className="pb-20 px-8">
        <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4">
          {GRANT_DETAILS.map((item) => (
            <div
              key={item.title}
              className="glass noise rounded-2xl p-6 flex flex-col gap-3"
              style={{ boxShadow: "0 0 0 1px rgba(172,123,120,0.1)" }}
            >
              <span className="text-gold text-2xl leading-none">
                {item.icon}
              </span>
              <h3 className="text-white text-base font-light">{item.title}</h3>
              <p className="text-white/35 text-sm leading-relaxed">
                {item.body}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Verification process explainer ──────────────────────────────── */}
      <section className="pb-20 px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
              How It Works
            </p>
            <h2 className="text-3xl font-extralight text-white">
              Adobe-Style Identity Lock
            </h2>
            <p className="text-white/30 text-sm mt-3 max-w-xl mx-auto leading-relaxed">
              We use OCR to extract the name from your government ID and match
              it 1:1 against the billing name you provide. Mismatch = instant
              auto-rejection. No human reviews needed. No bias. No exceptions.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              {
                step: "01",
                title: "Upload Your ID",
                body: "Government-issued photo ID — passport, national card, or driver's licence. PDF or image.",
              },
              {
                step: "02",
                title: "OCR Extracts Your Name",
                body: "Our server reads the name field from your document. The file is deleted within 48 hours.",
              },
              {
                step: "03",
                title: "Identity Lock Check",
                body: "Extracted name must match your billing name exactly. Approved? You get a Stripe link in < 24h.",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="glass noise rounded-2xl p-7 flex flex-col gap-3"
                style={{ boxShadow: "0 0 0 1px rgba(172,123,120,0.1)" }}
              >
                <span className="text-gold/30 text-4xl font-extralight leading-none">
                  {item.step}
                </span>
                <h3 className="text-white text-base font-light">
                  {item.title}
                </h3>
                <p className="text-white/35 text-sm leading-relaxed">
                  {item.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Application Form ─────────────────────────────────────────────── */}
      <section className="pb-32 px-8" id="apply">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-10">
            <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-3">
              Apply Now
            </p>
            <h2 className="text-3xl font-extralight text-white mb-3">
              The Application
            </h2>
            <p className="text-white/30 text-sm leading-relaxed max-w-md mx-auto">
              Complete all fields and upload both documents. We typically review
              within 24 hours during business days.
            </p>
          </div>

          <VerifyForm />
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer
        className="border-t py-10 px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-white/15 text-xs tracking-widest uppercase"
        style={{ borderColor: "rgba(172,123,120,0.1)" }}
      >
        <div className="flex items-center gap-2">
          <svg
            width="14"
            height="14"
            viewBox="0 0 40 40"
            fill="none"
            aria-hidden
          >
            <polygon
              points="20,2 38,20 20,38 2,20"
              stroke="#AC7B78"
              strokeWidth="1.5"
              fill="none"
            />
          </svg>
          <span className="text-gold/50">Aura Intelligence</span>
        </div>
        <span>© {new Date().getFullYear()} · All rights reserved</span>
        <a
          href="mailto:hello@aura-intelligence.ch"
          className="hover:text-white/60 transition-colors"
        >
          hello@aura-intelligence.ch
        </a>
      </footer>
    </main>
  );
}
