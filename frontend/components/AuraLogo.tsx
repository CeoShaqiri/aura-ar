"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

/**
 * AuraLogo — GSAP-animated identity mark shown when no model is loaded.
 * Entrance: scale+fade in. Outer ring: GSAP rotation. Diamond: GSAP pulse.
 */
export default function AuraLogo() {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const outerRingRef = useRef<SVGSVGElement>(null);
  const diamondRef = useRef<HTMLDivElement>(null);
  const wordmarkRef = useRef<HTMLDivElement>(null);
  const captionRef = useRef<HTMLParagraphElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Entrance cascade
      const tl = gsap.timeline();
      tl.fromTo(
        wrapperRef.current,
        { opacity: 0, scale: 0.75 },
        { opacity: 1, scale: 1, duration: 0.9, ease: "back.out(1.4)" },
      )
        .fromTo(
          wordmarkRef.current,
          { opacity: 0, y: 12 },
          { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
          "-=0.3",
        )
        .fromTo(
          captionRef.current,
          { opacity: 0 },
          { opacity: 1, duration: 0.5 },
          "-=0.2",
        );

      // Outer ring — continuous GSAP rotation (replaces CSS animate-spin-slow)
      gsap.to(outerRingRef.current, {
        rotation: 360,
        transformOrigin: "50% 50%",
        duration: 18,
        ease: "none",
        repeat: -1,
      });

      // Inner diamond — breathe pulse
      gsap.to(diamondRef.current, {
        scale: 1.12,
        opacity: 0.7,
        duration: 1.8,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });

      // Middle ring — slow counter-rotate
      gsap.to(".aura-mid-ring", {
        rotation: -360,
        transformOrigin: "50% 50%",
        duration: 28,
        ease: "none",
        repeat: -1,
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <div
      ref={wrapperRef}
      style={{ opacity: 0 }}
      className="flex flex-col items-center justify-center gap-6 select-none"
    >
      {/* Rings */}
      <div className="relative w-28 h-28 flex items-center justify-center">
        {/* Outer spinning ring — GSAP controlled */}
        <svg
          ref={outerRingRef}
          className="absolute inset-0"
          viewBox="0 0 112 112"
          fill="none"
        >
          <circle
            cx="56"
            cy="56"
            r="52"
            stroke="url(#gold-ring)"
            strokeWidth="1"
            strokeDasharray="8 6"
          />
          <defs>
            <linearGradient
              id="gold-ring"
              x1="0"
              y1="0"
              x2="112"
              y2="112"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stopColor="#F28D52" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#BDD9F2" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#F28D52" stopOpacity="0.9" />
            </linearGradient>
          </defs>
        </svg>

        {/* Middle ring — GSAP counter-rotate */}
        <svg
          className="aura-mid-ring absolute inset-0 opacity-30"
          viewBox="0 0 112 112"
          fill="none"
        >
          <circle cx="56" cy="56" r="40" stroke="#BDD9F2" strokeWidth="0.5" />
        </svg>

        {/* Inner diamond — GSAP pulse */}
        <div ref={diamondRef}>
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <polygon
              points="20,2 38,20 20,38 2,20"
              stroke="url(#rose-diamond)"
              strokeWidth="1.5"
              fill="rgba(242,141,82,0.1)"
            />
            <polygon
              points="20,8 32,20 20,32 8,20"
              stroke="#F28D52"
              strokeWidth="0.5"
              fill="rgba(242,141,82,0.06)"
              opacity="0.5"
            />
            <defs>
              <linearGradient
                id="rose-diamond"
                x1="0"
                y1="0"
                x2="40"
                y2="40"
                gradientUnits="userSpaceOnUse"
              >
                <stop offset="0%" stopColor="#BDD9F2" />
                <stop offset="100%" stopColor="#F28D52" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>

      {/* Wordmark */}
      <div
        ref={wordmarkRef}
        style={{ opacity: 0 }}
        className="flex flex-col items-center gap-1"
      >
        <span className="brand-wordmark text-gold">The Aura Standard</span>
      </div>

      <p
        ref={captionRef}
        style={{ opacity: 0 }}
        className="text-white/20 text-xs tracking-widest uppercase"
      >
        No model loaded
      </p>
    </div>
  );
}
