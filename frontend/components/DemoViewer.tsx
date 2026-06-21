"use client";

import AuraLogo from "./AuraLogo";

interface DemoViewerProps {
  /** Pass a live ceo.aura-intelligence.ch view URL to embed the AR viewer */
  src?: string;
}

/**
 * DemoViewer — glass-morphism AR preview card.
 * Shows the AuraLogo animation when no model URL is provided.
 * Shows an iframe embed of the live viewer when src is set.
 */
export default function DemoViewer({ src }: DemoViewerProps) {
  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* Ambient glow behind card */}
      <div
        className="absolute -inset-4 rounded-3xl opacity-40 blur-3xl"
        style={{
          background:
            "radial-gradient(ellipse, rgba(201,168,76,0.2) 0%, transparent 70%)",
        }}
        aria-hidden
      />

      {/* Main card */}
      <div
        className="glass noise relative rounded-2xl overflow-hidden"
        style={{
          boxShadow:
            "0 0 0 1px rgba(201,168,76,0.15), 0 32px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06)",
          minHeight: "480px",
        }}
      >
        {/* Top bar */}
        <div
          className="flex items-center gap-2 px-4 py-3 border-b"
          style={{ borderColor: "rgba(255,255,255,0.06)" }}
        >
          <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
          <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
          <span className="w-2.5 h-2.5 rounded-full bg-white/10" />
          <span className="ml-4 text-white/20 text-xs tracking-widest uppercase font-light">
            Aura AR Viewer
          </span>
          {src && (
            <span className="ml-auto flex items-center gap-1.5 text-xs text-emerald-400/80">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live
            </span>
          )}
        </div>

        {/* Content */}
        <div
          className="flex items-center justify-center"
          style={{ minHeight: "420px" }}
        >
          {src ? (
            <iframe
              src={src}
              className="w-full h-full rounded-b-2xl"
              style={{ minHeight: "420px", border: "none" }}
              allow="xr-spatial-tracking; camera; microphone"
              title="Aura AR Viewer"
            />
          ) : (
            <AuraLogo />
          )}
        </div>
      </div>

      {/* Corner accent lines */}
      <svg
        className="absolute top-0 left-0 w-16 h-16 pointer-events-none"
        viewBox="0 0 64 64"
        fill="none"
        aria-hidden
      >
        <path
          d="M2 30 L2 2 L30 2"
          stroke="#AC7B78"
          strokeWidth="0.75"
          strokeOpacity="0.5"
        />
      </svg>
      <svg
        className="absolute bottom-0 right-0 w-16 h-16 pointer-events-none"
        viewBox="0 0 64 64"
        fill="none"
        aria-hidden
      >
        <path
          d="M62 34 L62 62 L34 62"
          stroke="#AC7B78"
          strokeWidth="0.75"
          strokeOpacity="0.5"
        />
      </svg>
    </div>
  );
}
