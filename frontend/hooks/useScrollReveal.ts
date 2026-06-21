"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * useScrollReveal — GSAP ScrollTrigger-powered reveal for all
 * [data-reveal] and [data-reveal-group] elements.
 * Call once at the page level.
 */
export function useScrollReveal() {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    // Single elements — fade + slide up
    const singles = gsap.utils.toArray<HTMLElement>("[data-reveal]");
    singles.forEach((el) => {
      const dir = el.dataset.revealDir;
      const xFrom = dir === "left" ? -48 : dir === "right" ? 48 : 0;
      const yFrom = dir ? 0 : 32;

      gsap.fromTo(
        el,
        { opacity: 0, y: yFrom, x: xFrom },
        {
          opacity: 1,
          y: 0,
          x: 0,
          duration: 0.9,
          ease: "power3.out",
          scrollTrigger: {
            trigger: el,
            start: "top 88%",
            toggleActions: "play none none none",
          },
        },
      );
    });

    // Group elements — stagger children
    const groups = gsap.utils.toArray<HTMLElement>("[data-reveal-group]");
    groups.forEach((group) => {
      const children = gsap.utils.toArray<HTMLElement>(
        group.children as unknown as HTMLElement[],
      );
      gsap.fromTo(
        children,
        { opacity: 0, y: 40 },
        {
          opacity: 1,
          y: 0,
          duration: 0.75,
          ease: "power3.out",
          stagger: 0.1,
          scrollTrigger: {
            trigger: group,
            start: "top 85%",
            toggleActions: "play none none none",
          },
        },
      );
    });

    return () => {
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);
}

/**
 * useParallax — GSAP ScrollTrigger parallax on a ref element.
 * @param speed  fractional scroll speed (default 0.2)
 */
export function useParallax<T extends HTMLElement>(speed = 0.2) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const st = ScrollTrigger.create({
      trigger: el,
      start: "top bottom",
      end: "bottom top",
      onUpdate: (self) => {
        gsap.set(el, { y: self.progress * speed * -120 });
      },
    });

    return () => st.kill();
  }, [speed]);

  return ref;
}

/**
 * useGsapFadeIn — simple one-shot fade+slide for a single ref element.
 * @param delay  seconds delay (default 0)
 */
export function useGsapFadeIn<T extends HTMLElement>(delay = 0) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    gsap.fromTo(
      el,
      { opacity: 0, y: 28 },
      { opacity: 1, y: 0, duration: 0.9, delay, ease: "power3.out" },
    );
  }, [delay]);

  return ref;
}
