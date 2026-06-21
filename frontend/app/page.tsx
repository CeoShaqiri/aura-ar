"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { TextPlugin } from "gsap/TextPlugin";
import DemoViewer from "@/components/DemoViewer";
import CaseStudies from "@/components/CaseStudies";
import Pricing from "@/components/Pricing";
import HeroScene from "@/components/HeroScene";
import { useScrollReveal } from "@/hooks/useScrollReveal";

gsap.registerPlugin(ScrollTrigger, TextPlugin);

/**
 * ↓ Swap: paste a live /view/<uuid> URL to activate the hero viewer.
 * Leave undefined to show the animated Aura logo.
 */
const HERO_VIEWER_URL: string | undefined = undefined;

// ── Feature grid data ────────────────────────────────────────────────────────
const FEATURES = [
  {
    icon: "◉",
    title: "One Click. That's It.",
    body: "Select your mesh in Blender. Press LAUNCH. Your model is live in AR in under 90 seconds. No export dialog. No format conversion. No re-import. One button.",
    highlight: true,
  },
  {
    icon: "◐",
    title: "No App Required",
    body: "A single URL opens full AR in Safari or Chrome — directly on the camera. Your client never visits an app store. No install friction. No QR-code hunting.",
    highlight: false,
  },
  {
    icon: "⬡",
    title: "No Cloud Services",
    body: "Your model runs on your dedicated Aura Monolith node — not AWS, not GCP, not Azure. Nothing touches shared infrastructure. Your IP stays yours.",
    highlight: false,
  },
  {
    icon: "◆",
    title: "Direct from Blender",
    body: "The Aura Core Addon lives inside Blender's sidebar. No third-party platform. No browser upload. No pipeline config. It sends directly from the scene you're working in.",
    highlight: false,
  },
  {
    icon: "◈",
    title: "Permanent AR Links",
    body: "Every model gets a UUID-based URL that never expires. Send it in an email, embed it on a website, paste it in a pitch deck. The AR opens instantly every time.",
    highlight: false,
  },
  {
    icon: "◎",
    title: "White-Label Ready",
    body: "Your brand, your domain, your client-facing AR portal. Aura is invisible. On Sovereign tier your studio is the only name the client ever sees.",
    highlight: false,
  },
];

const STATS = [
  { value: 30, suffix: "s", label: "Blender → live AR" },
  { value: 0, suffix: "", label: "App installs needed" },
  { value: 0, suffix: "", label: "Cloud services" },
  { value: "∞", suffix: "", label: "Rooms it works in" },
];

export default function Home() {
  useScrollReveal();

  const navRef = useRef<HTMLElement>(null);
  const heroEyebrowRef = useRef<HTMLDivElement>(null);
  const heroH1Ref = useRef<HTMLHeadingElement>(null);
  const heroParaRef = useRef<HTMLParagraphElement>(null);
  const heroCTARef = useRef<HTMLDivElement>(null);
  const heroStatsRef = useRef<HTMLDivElement>(null);
  const heroSceneRef = useRef<HTMLDivElement>(null);
  const cursorGlowRef = useRef<HTMLDivElement>(null);

  /* ── Hero entrance timeline ──────────────────────────────────────── */
  useEffect(() => {
    const ctx = gsap.context(() => {
      // Nav slides down from above
      gsap.fromTo(
        navRef.current,
        { y: -80, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.9, ease: "power3.out", delay: 0.1 },
      );

      // Hero content — staggered cascade
      const tl = gsap.timeline({ delay: 0.3 });
      tl.fromTo(
        heroEyebrowRef.current,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" },
      )
        .fromTo(
          heroH1Ref.current,
          { opacity: 0, y: 36 },
          { opacity: 1, y: 0, duration: 0.85, ease: "power3.out" },
          "-=0.4",
        )
        .fromTo(
          heroParaRef.current,
          { opacity: 0, y: 24 },
          { opacity: 1, y: 0, duration: 0.7, ease: "power3.out" },
          "-=0.45",
        )
        .fromTo(
          heroCTARef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.65, ease: "power3.out" },
          "-=0.4",
        )
        .fromTo(
          heroStatsRef.current,
          { opacity: 0, y: 16 },
          { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
          "-=0.35",
        )
        .fromTo(
          heroSceneRef.current,
          { opacity: 0, scale: 0.88, rotateY: -12 },
          {
            opacity: 1,
            scale: 1,
            rotateY: 0,
            duration: 1.1,
            ease: "power3.out",
          },
          "<-=0.5",
        );

      // Stat counters
      heroStatsRef.current
        ?.querySelectorAll<HTMLSpanElement>("[data-count]")
        .forEach((el) => {
          const target = Number(el.dataset.count);
          if (!isNaN(target) && target > 0) {
            const proxy = { val: 0 };
            gsap.to(proxy, {
              val: target,
              duration: 1.4,
              delay: 1.2,
              ease: "power2.out",
              onUpdate: () => {
                el.textContent = Math.round(proxy.val).toString();
              },
            });
          }
        });

      // Nav link hover glow
      navRef.current?.querySelectorAll<HTMLAnchorElement>("a").forEach((a) => {
        a.addEventListener("mouseenter", () =>
          gsap.to(a, {
            color: "rgba(255,255,255,0.9)",
            duration: 0.25,
            ease: "power1.out",
          }),
        );
        a.addEventListener("mouseleave", () =>
          gsap.to(a, {
            color: "",
            duration: 0.35,
            ease: "power1.inOut",
          }),
        );
      });

      // Floating section dividers — slow parallax on scroll
      gsap.utils.toArray<HTMLElement>(".hero-glow").forEach((el) => {
        gsap.to(el, {
          y: -80,
          ease: "none",
          scrollTrigger: {
            trigger: el,
            start: "top bottom",
            end: "bottom top",
            scrub: 2,
          },
        });
      });
    });

    return () => ctx.revert();
  }, []);

  /* ── Cursor glow tracking ────────────────────────────────────────── */
  useEffect(() => {
    const glow = cursorGlowRef.current;
    if (!glow) return;
    const move = (e: MouseEvent) => {
      gsap.to(glow, {
        x: e.clientX - 200,
        y: e.clientY - 200,
        duration: 0.6,
        ease: "power2.out",
      });
    };
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);

  /* ── Magnetic CTA buttons ────────────────────────────────────────── */
  useEffect(() => {
    const btns =
      heroCTARef.current?.querySelectorAll<HTMLAnchorElement>("a") ?? [];
    btns.forEach((btn) => {
      btn.addEventListener("mousemove", (e) => {
        const r = btn.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        gsap.to(btn, {
          x: dx * 0.22,
          y: dy * 0.22,
          duration: 0.3,
          ease: "power2.out",
        });
      });
      btn.addEventListener("mouseleave", () =>
        gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: "elastic.out(1,0.5)" }),
      );
    });
  }, []);

  return (
    <main className="relative min-h-screen bg-plum overflow-x-hidden">
      {/* ── Cursor glow ──────────────────────────────────────────────── */}
      <div
        ref={cursorGlowRef}
        className="pointer-events-none fixed z-0 w-[400px] h-[400px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(242,141,82,0.07) 0%, transparent 70%)",
        }}
        aria-hidden
      />

      {/* ── Background grid ─────────────────────────────────────────────── */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.025]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(242,141,82,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(242,141,82,0.12) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
        }}
        aria-hidden
      />

      {/* ── NAV ──────────────────────────────────────────────────────────── */}
      <nav
        ref={navRef}
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 py-5 glass border-b"
        style={{ borderColor: "rgba(242,141,82,0.12)", opacity: 0 }}
      >
        <div className="flex items-center gap-3">
          <svg
            width="18"
            height="18"
            viewBox="0 0 40 40"
            fill="none"
            aria-hidden
          >
            <polygon
              points="20,2 38,20 20,38 2,20"
              stroke="#F28D52"
              strokeWidth="1.5"
              fill="rgba(242,141,82,0.1)"
            />
          </svg>
          <span className="brand-wordmark text-gold">The Aura Standard</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-white/35 text-xs tracking-widest uppercase">
          <a
            href="#how-it-works"
            className="hover:text-white transition-colors"
          >
            How It Works
          </a>
          <a href="#cases" className="hover:text-white transition-colors">
            Use Cases
          </a>
          <a href="#pricing" className="hover:text-white transition-colors">
            Pricing
          </a>
          <a
            href="/legacy-grant"
            className="hover:text-[#F28D52] transition-colors"
          >
            Legacy Grant
          </a>
        </div>

        <a
          href="#pricing"
          className="text-xs tracking-widest uppercase px-5 py-2.5 rounded-full transition-all duration-300 hover:bg-[rgba(242,141,82,0.12)]"
          style={{ border: "1px solid rgba(242,141,82,0.4)", color: "#F28D52" }}
        >
          Get Early Access
        </a>
      </nav>

      {/* ── HERO ─────────────────────────────────────────────────────────── */}
      <section
        id="hero"
        className="relative min-h-screen flex flex-col lg:flex-row items-center justify-center gap-16 px-8 pt-28 pb-20 max-w-7xl mx-auto"
      >
        <div
          className="hero-glow top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 opacity-60"
          aria-hidden
        />

        {/* Left — copy */}
        <div className="relative z-10 flex-1 flex flex-col gap-8">
          <div
            ref={heroEyebrowRef}
            style={{ opacity: 0 }}
            className="flex items-center gap-3"
          >
            <div className="h-px w-10 bg-gradient-to-r from-transparent to-[#F28D52]" />
            <span className="text-gold text-[10px] tracking-[0.5em] uppercase">
              World&apos;s First · Blender to AR · One Click
            </span>
          </div>

          <h1 ref={heroH1Ref} style={{ opacity: 0 }}>
            <span className="block text-[10px] tracking-[0.5em] uppercase text-gold mb-5">
              The Aura Standard · World&apos;s First
            </span>
            <span className="block text-4xl md:text-6xl font-extralight text-white leading-[1.05] tracking-tight">
              Blender to Augmented Reality.
            </span>
            <span className="block text-4xl md:text-6xl font-extralight text-gold leading-[1.05] tracking-tight">
              One click.
            </span>
            <span className="block text-2xl md:text-3xl font-extralight text-white/30 leading-snug mt-4">
              Your creation. In your room.
              <br />
              In your client&apos;s room. In a stranger&apos;s room.
              <br />
              <span className="text-white/50">
                Live in AR in under 30 seconds.
              </span>
            </span>
          </h1>

          <p
            ref={heroParaRef}
            style={{ opacity: 0 }}
            className="text-white/40 text-base leading-relaxed max-w-lg"
          >
            Finish a model in Blender, press LAUNCH — and in under 30 seconds
            anyone on the planet can hold it in their room through their phone
            camera. No app download. No QR hunt. No cloud account. Just send the
            link.
          </p>

          <div
            ref={heroCTARef}
            style={{ opacity: 0 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <a
              href="#pricing"
              className="px-8 py-4 rounded-full text-sm tracking-widest uppercase font-light transition-all duration-300 hover:shadow-[0_0_40px_rgba(242,141,82,0.5)]"
              style={{
                background:
                  "linear-gradient(135deg, #F28D52, #BDD9F2, #F28D52)",
                color: "#071526",
              }}
            >
              Get Early Access
            </a>
            <a
              href="#how-it-works"
              className="px-8 py-4 rounded-full text-sm tracking-widest uppercase font-light text-white/40 hover:text-white transition-colors glass"
              style={{ border: "1px solid rgba(242,141,82,0.2)" }}
            >
              See How It Works
            </a>
          </div>

          <div
            ref={heroStatsRef}
            style={{ opacity: 0 }}
            className="flex gap-10 pt-2"
          >
            {STATS.map((s) => (
              <div key={s.label} className="flex flex-col gap-1">
                <span className="text-gold text-xl font-light">
                  {typeof s.value === "number" && s.value > 0 ? (
                    <>
                      <span data-count={s.value}>0</span>
                      {s.suffix}
                    </>
                  ) : (
                    <>
                      {s.value}
                      {s.suffix}
                    </>
                  )}
                </span>
                <span className="text-white/25 text-[10px] tracking-widest uppercase">
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right — live 3D scene */}
        <div
          ref={heroSceneRef}
          style={{ opacity: 0 }}
          className="relative flex-1 flex items-center justify-center min-h-[480px]"
        >
          <HeroScene />
        </div>
      </section>

      {/* ── WHAT MAKES IT DIFFERENT ──────────────────────────────────────── */}
      <section id="how-it-works" className="py-32 px-8">
        <div className="max-w-5xl mx-auto">
          <div className="max-w-2xl mb-20" data-reveal data-reveal-dir="left">
            <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-4">
              Why The Aura Standard Exists
            </p>
            <h2 className="text-4xl md:text-5xl font-extralight text-white leading-tight">
              The 3-hour export pipeline
              <br />
              <span className="text-white/25">is over.</span>
            </h2>
            <p className="mt-6 text-white/40 text-base leading-relaxed">
              Every 3D artist knows the pain. You finish a model in Blender,
              then spend hours exporting, converting formats, re-rigging for a
              third-party AR platform, uploading to a cloud service that owns
              your file — only for the client to ask for a tweak.
              <br />
              <br />
              Aura Core Addon lives inside Blender's sidebar. One button sends
              your model directly to a live AR link. Your files never leave your
              own infrastructure. No middleman. No pipeline. Done in 90 seconds.
            </p>
          </div>

          {/* Feature grid */}
          <div
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
            data-reveal-group
          >
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="glass noise rounded-2xl p-7 flex flex-col gap-4 relative overflow-hidden group transition-all duration-500 cursor-default"
                style={{
                  boxShadow: f.highlight
                    ? "0 0 0 1px rgba(242,141,82,0.35), inset 0 1px 0 rgba(242,141,82,0.1)"
                    : "0 0 0 1px rgba(242,141,82,0.1)",
                }}
                onMouseEnter={(e) => {
                  gsap.to(e.currentTarget, {
                    y: -6,
                    boxShadow:
                      "0 0 0 1px rgba(242,141,82,0.45), 0 20px 60px rgba(242,141,82,0.12)",
                    duration: 0.35,
                    ease: "power2.out",
                  });
                }}
                onMouseLeave={(e) => {
                  gsap.to(e.currentTarget, {
                    y: 0,
                    boxShadow: f.highlight
                      ? "0 0 0 1px rgba(242,141,82,0.35), inset 0 1px 0 rgba(242,141,82,0.1)"
                      : "0 0 0 1px rgba(242,141,82,0.1)",
                    duration: 0.5,
                    ease: "power2.inOut",
                  });
                }}
              >
                {f.highlight && (
                  <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#F28D52] to-transparent" />
                )}
                <span className="text-gold text-2xl leading-none">
                  {f.icon}
                </span>
                <h3 className="text-white text-base font-light">{f.title}</h3>
                <p className="text-white/35 text-sm leading-relaxed">
                  {f.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CASE STUDIES ─────────────────────────────────────────────────── */}
      <CaseStudies />

      {/* ── HOW IT WORKS ─────────────────────────────────────────────────── */}
      <section className="py-32 px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-20" data-reveal>
            <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-4">
              How it works
            </p>
            <h2 className="text-4xl md:text-5xl font-extralight text-white">
              Select. Launch. Share.
              <br />
              <span className="text-white/25">
                That&apos;s the whole pipeline.
              </span>
            </h2>
          </div>

          <div
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
            data-reveal-group
          >
            {[
              {
                step: "01",
                title: "Select in Blender",
                body: "Open any scene. Click your mesh. Press LAUNCH in the Aura Core Addon sidebar — that's it. No export dialog, no format selection, no file picker.",
              },
              {
                step: "02",
                title: "Aura Deploys It",
                body: "Your model is compressed, verified against your API key, and routed to your dedicated Aura node in seconds. Nothing touches public cloud infrastructure.",
              },
              {
                step: "03",
                title: "Share One URL",
                body: "A permanent link appears in the Blender sidebar. Send it anywhere. Recipients tap it — AR opens directly in their camera. No app. No LiDAR. No friction.",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="glass noise rounded-2xl p-8 flex flex-col gap-4 cursor-default"
                style={{ boxShadow: "0 0 0 1px rgba(242,141,82,0.1)" }}
                onMouseEnter={(e) =>
                  gsap.to(e.currentTarget, {
                    y: -5,
                    boxShadow:
                      "0 0 0 1px rgba(242,141,82,0.4), 0 16px 50px rgba(242,141,82,0.1)",
                    duration: 0.3,
                    ease: "power2.out",
                  })
                }
                onMouseLeave={(e) =>
                  gsap.to(e.currentTarget, {
                    y: 0,
                    boxShadow: "0 0 0 1px rgba(242,141,82,0.1)",
                    duration: 0.45,
                    ease: "power2.inOut",
                  })
                }
              >
                <span className="text-gold/30 text-5xl font-extralight leading-none">
                  {item.step}
                </span>
                <h3 className="text-white text-lg font-light">{item.title}</h3>
                <p className="text-white/35 text-sm leading-relaxed">
                  {item.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── LIVE DEMO VIEWER ─────────────────────────────────────────────── */}
      <section className="py-16 px-8" data-reveal>
        <div className="max-w-3xl mx-auto text-center mb-12">
          <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-4">
            From Blender to This
          </p>
          <h2 className="text-3xl font-extralight text-white">
            {HERO_VIEWER_URL
              ? "Live AR Model — Tap to Open on Any Phone"
              : "This is what your clients see. No app. Just a link."}
          </h2>
        </div>
        <DemoViewer src={HERO_VIEWER_URL} />
      </section>

      {/* ── PRICING ──────────────────────────────────────────────────────── */}
      <Pricing />

      {/* ── LEGACY GRANT TEASER ──────────────────────────────────────────── */}
      <section className="py-24 px-8" data-reveal>
        <div
          className="max-w-3xl mx-auto glass noise rounded-3xl p-10 relative overflow-hidden text-center"
          style={{
            boxShadow:
              "0 0 0 1px rgba(242,141,82,0.18), 0 32px 80px rgba(7,21,38,0.7)",
          }}
        >
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#F28D52]/50 to-transparent" />
          <p className="text-gold text-[10px] tracking-[0.5em] uppercase mb-4">
            The Aura Legacy Grant
          </p>
          <h2 className="text-3xl font-extralight text-white mb-3">
            For Students & Low-Income Creators
          </h2>
          <p className="text-white/35 text-base leading-relaxed mb-6 max-w-xl mx-auto">
            25 Secure Exports / month for $49 / mo on a 24-month plan.
            Identity-verified. No upsell. No compromise on quality. The same
            Aura Monolith infrastructure — accessible to everyone.
          </p>
          <a
            href="/legacy-grant"
            className="inline-block px-8 py-3.5 rounded-full text-sm tracking-widest uppercase font-light transition-all duration-300"
            style={{
              border: "1px solid rgba(242,141,82,0.45)",
              color: "#F28D52",
            }}
            onMouseEnter={(e) =>
              gsap.to(e.currentTarget, {
                boxShadow: "0 0 28px rgba(242,141,82,0.3)",
                scale: 1.04,
                duration: 0.3,
                ease: "power2.out",
              })
            }
            onMouseLeave={(e) =>
              gsap.to(e.currentTarget, {
                boxShadow: "none",
                scale: 1,
                duration: 0.4,
                ease: "power2.inOut",
              })
            }
          >
            Apply for the Grant
          </a>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────────────────── */}
      <footer
        className="border-t py-12 px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-white/15 text-xs tracking-widest uppercase"
        style={{ borderColor: "rgba(242,141,82,0.1)" }}
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
              stroke="#F28D52"
              strokeWidth="1.5"
              fill="none"
            />
          </svg>
          <span className="brand-wordmark text-gold/50">The Aura Standard</span>
        </div>
        <span>© {new Date().getFullYear()} · All rights reserved</span>
        <div className="flex gap-6">
          <a
            href="https://ceo-of-aura.cloud"
            className="hover:text-white/60 transition-colors"
          >
            ceo-of-aura.cloud
          </a>
          <a
            href="https://aura-intelligence.ch"
            className="hover:text-white/60 transition-colors"
          >
            aura-intelligence.ch
          </a>
        </div>
      </footer>
    </main>
  );
}
