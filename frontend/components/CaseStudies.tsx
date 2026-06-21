"use client";

import Image from "next/image";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const CASES = [
  {
    id: "fashion",
    label: "Fashion & Retail",
    headline:
      "A €1,400 sneaker. On a marble pedestal. In your customer's bedroom.",
    description:
      "Scan → place → purchase. Aura AR collapses the gap between browsing and buying. No app. No friction. One link.",
    /** ⬇ Swap: drop hero-watch.png into frontend/public/images/ */
    image: "/images/hero-watch.png",
    imagePlaceholder:
      "bg-gradient-to-br from-[#472830] via-[#58383E] to-[#664F42]",
    tag: "E-Commerce · Fashion",
  },
  {
    id: "furniture",
    label: "Interior & Furniture",
    headline:
      "A €12,000 designer chair visualized in any penthouse — before the order ships.",
    description:
      "Clients see true scale, true material, true light. Returns drop. Confidence soars. Close rates double.",
    /** ⬇ Swap: drop hero-chair.png into frontend/public/images/ */
    image: "/images/hero-chair.png",
    imagePlaceholder:
      "bg-gradient-to-br from-[#35444B] via-[#472830] to-[#58383E]",
    tag: "Interior Design · Luxury",
  },
  {
    id: "biotech",
    label: "Bio-Tech & Science",
    headline:
      "A protein strand at 1:1 scale. Inspected in the lab without a microscope.",
    description:
      "Researchers, surgeons, and engineers overlay molecular structures into physical space. The future of spatial science.",
    /** ⬇ Swap: drop hero-biotech.png into frontend/public/images/ */
    image: "/images/hero-biotech.png",
    imagePlaceholder:
      "bg-gradient-to-br from-[#35444B] via-[#472830] to-[#35444B]",
    tag: "Bio-Tech · Research",
  },
];

export default function CaseStudies() {
  const sectionRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const gridRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Header slide in
      gsap.fromTo(
        headerRef.current,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.85,
          ease: "power3.out",
          scrollTrigger: {
            trigger: headerRef.current,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );

      // Cards stagger in
      const cards = gridRef.current?.children ?? [];
      gsap.fromTo(
        Array.from(cards),
        { opacity: 0, y: 60, scale: 0.95 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.75,
          stagger: 0.14,
          ease: "power3.out",
          scrollTrigger: {
            trigger: gridRef.current,
            start: "top 82%",
            toggleActions: "play none none none",
          },
        },
      );
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  const handleCardEnter = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, {
      y: -8,
      scale: 1.02,
      boxShadow:
        "0 0 0 1px rgba(242,141,82,0.4), 0 28px 70px rgba(242,141,82,0.12)",
      duration: 0.35,
      ease: "power2.out",
    });
  };
  const handleCardLeave = (e: React.MouseEvent<HTMLDivElement>) => {
    gsap.to(e.currentTarget, {
      y: 0,
      scale: 1,
      boxShadow:
        "0 0 0 1px rgba(255,255,255,0.06), 0 24px 60px rgba(0,0,0,0.5)",
      duration: 0.5,
      ease: "power2.inOut",
    });
  };

  return (
    <section ref={sectionRef} id="cases" className="relative py-32 px-6">
      {/* Section header */}
      <div
        ref={headerRef}
        style={{ opacity: 0 }}
        className="max-w-4xl mx-auto text-center mb-20"
      >
        <p className="text-gold text-xs tracking-[0.4em] uppercase mb-4">
          Professional Case Studies
        </p>
        <h2 className="text-4xl md:text-5xl font-light text-white leading-tight">
          Every industry.
          <br />
          <span className="text-white/40">One engine.</span>
        </h2>
      </div>

      {/* Cards */}
      <div
        ref={gridRef}
        className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {CASES.map((c) => (
          <div
            key={c.id}
            className="glass noise rounded-2xl overflow-hidden flex flex-col group cursor-default"
            style={{
              boxShadow:
                "0 0 0 1px rgba(255,255,255,0.06), 0 24px 60px rgba(0,0,0,0.5)",
            }}
            onMouseEnter={handleCardEnter}
            onMouseLeave={handleCardLeave}
          >
            {/* Image area — swap /images/*.jpg with Gen-AI renders */}
            <div
              className={`relative w-full aspect-[4/3] ${c.imagePlaceholder} overflow-hidden`}
            >
              <Image
                src={c.image}
                alt={c.label}
                fill
                className="object-cover opacity-0 group-hover:opacity-100 transition-opacity duration-700"
                onError={() => {}} // silently stays on placeholder gradient until image exists
              />
              {/* Overlay gradient */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

              {/* Tag */}
              <span className="absolute top-4 left-4 text-[10px] tracking-widest uppercase text-white/40 bg-black/40 backdrop-blur-sm px-3 py-1 rounded-full border border-white/10">
                {c.tag}
              </span>
            </div>

            {/* Text */}
            <div className="p-6 flex flex-col gap-3 flex-1">
              <p className="text-gold text-[10px] tracking-[0.35em] uppercase">
                {c.label}
              </p>
              <h3 className="text-white text-lg font-light leading-snug">
                {c.headline}
              </h3>
              <p className="text-white/40 text-sm leading-relaxed mt-auto">
                {c.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
