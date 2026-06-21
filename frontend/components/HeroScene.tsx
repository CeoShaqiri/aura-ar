"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

// ── 3-D maths (minimal, no deps) ────────────────────────────────────────────
type Vec3 = [number, number, number];

function rotY(v: Vec3, a: number): Vec3 {
  return [
    v[0] * Math.cos(a) + v[2] * Math.sin(a),
    v[1],
    -v[0] * Math.sin(a) + v[2] * Math.cos(a),
  ];
}
function rotX(v: Vec3, a: number): Vec3 {
  return [
    v[0],
    v[1] * Math.cos(a) - v[2] * Math.sin(a),
    v[1] * Math.sin(a) + v[2] * Math.cos(a),
  ];
}
function project(v: Vec3, fov: number, cx: number, cy: number, scale: number) {
  const z = v[2] + fov;
  return { x: (v[0] / z) * scale + cx, y: (v[1] / z) * scale + cy, depth: z };
}

// Octahedron
const VERTS: Vec3[] = [
  [0, -1, 0],
  [0, 1, 0],
  [1, 0, 0],
  [-1, 0, 0],
  [0, 0, 1],
  [0, 0, -1],
];
const EDGES: [number, number][] = [
  [0, 2],
  [0, 3],
  [0, 4],
  [0, 5],
  [1, 2],
  [1, 3],
  [1, 4],
  [1, 5],
  [2, 4],
  [4, 3],
  [3, 5],
  [5, 2],
];

// Outer cage (scaled-up second octahedron at 45° Y offset)
const VERTS2: Vec3[] = VERTS.map(([x, y, z]) => {
  const s = 1.7;
  const r = rotY([x * s, y * s, z * s], Math.PI / 4);
  return rotX(r, Math.PI / 6);
});

// Particles
const PARTICLES = Array.from({ length: 55 }, () => ({
  v: [
    (Math.random() - 0.5) * 3.2,
    (Math.random() - 0.5) * 3.2,
    (Math.random() - 0.5) * 3.2,
  ] as Vec3,
  size: Math.random() * 1.8 + 0.4,
  phase: Math.random() * Math.PI * 2,
  speed: Math.random() * 0.4 + 0.2,
}));

// ── Component ─────────────────────────────────────────────────────────────────
export default function HeroScene() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Fixed logical resolution — CSS stretches it
    const W = 580;
    const H = 520;
    canvas.width = W;
    canvas.height = H;

    const CX = W * 0.5;
    const CY = H * 0.44;
    const SCALE = Math.min(W, H) * 0.26;
    const FOV = 3.8;
    const TILT = Math.PI * 0.12;

    let angle = 0;
    let rafId = 0;

    function draw() {
      ctx!.clearRect(0, 0, W, H);
      angle += 0.003;
      const t = Date.now() * 0.001;

      // ── Ground grid (AR plane) ─────────────────────────────────────────
      const GRID = 5;
      const GY = 1.15; // sits below the shape
      for (let i = -GRID; i <= GRID; i++) {
        const step = 0.38;
        // horizontal
        const L = project(
          rotX(rotY([-GRID * step, GY, i * step], angle * 0.15), TILT),
          FOV,
          CX,
          CY,
          SCALE,
        );
        const R = project(
          rotX(rotY([GRID * step, GY, i * step], angle * 0.15), TILT),
          FOV,
          CX,
          CY,
          SCALE,
        );
        // vertical
        const T = project(
          rotX(rotY([i * step, GY, -GRID * step], angle * 0.15), TILT),
          FOV,
          CX,
          CY,
          SCALE,
        );
        const B = project(
          rotX(rotY([i * step, GY, GRID * step], angle * 0.15), TILT),
          FOV,
          CX,
          CY,
          SCALE,
        );

        const dist = Math.abs(i) / GRID;
        const alpha = (1 - dist * 0.9) * 0.09;
        ctx!.strokeStyle = `rgba(172,123,120,${alpha.toFixed(3)})`;
        ctx!.lineWidth = 0.6;

        ctx!.beginPath();
        ctx!.moveTo(L.x, L.y);
        ctx!.lineTo(R.x, R.y);
        ctx!.stroke();
        ctx!.beginPath();
        ctx!.moveTo(T.x, T.y);
        ctx!.lineTo(B.x, B.y);
        ctx!.stroke();
      }

      // ── Outer cage ────────────────────────────────────────────────────
      const cage = VERTS2.map((v) => {
        const r = rotX(rotY(v, -angle * 0.4), TILT * 0.6);
        return project(r, FOV, CX, CY, SCALE);
      });
      EDGES.forEach(([a, b]) => {
        const depth = (cage[a].depth + cage[b].depth) * 0.5;
        const alpha = Math.min(0.13, Math.max(0.03, (depth - 2) * 0.04));
        ctx!.strokeStyle = `rgba(189,217,242,${alpha.toFixed(3)})`;
        ctx!.lineWidth = 0.8;
        ctx!.beginPath();
        ctx!.moveTo(cage[a].x, cage[a].y);
        ctx!.lineTo(cage[b].x, cage[b].y);
        ctx!.stroke();
      });

      // ── Inner octahedron ──────────────────────────────────────────────
      const proj = VERTS.map((v) => {
        const r = rotX(rotY(v, angle), TILT);
        return project(r, FOV, CX, CY, SCALE);
      });

      // Back edges first (depth sorting)
      const sortedEdges = [...EDGES].sort((e1, e2) => {
        const d1 = proj[e1[0]].depth + proj[e1[1]].depth;
        const d2 = proj[e2[0]].depth + proj[e2[1]].depth;
        return d2 - d1;
      });

      sortedEdges.forEach(([a, b]) => {
        const depth = (proj[a].depth + proj[b].depth) * 0.5;
        const alpha = Math.min(0.75, Math.max(0.08, (depth - 2.2) / 2.8));
        ctx!.strokeStyle = `rgba(242,141,82,${alpha.toFixed(3)})`;
        ctx!.lineWidth = 1.1;
        ctx!.beginPath();
        ctx!.moveTo(proj[a].x, proj[a].y);
        ctx!.lineTo(proj[b].x, proj[b].y);
        ctx!.stroke();
      });

      // Vertices
      proj.forEach((p) => {
        const alpha = Math.min(1, Math.max(0.1, (p.depth - 2.2) / 2.2));
        ctx!.fillStyle = `rgba(242,141,82,${alpha.toFixed(3)})`;
        ctx!.beginPath();
        ctx!.arc(p.x, p.y, 2.8, 0, Math.PI * 2);
        ctx!.fill();
      });

      // Center glow
      const grd = ctx!.createRadialGradient(CX, CY, 0, CX, CY, SCALE * 0.6);
      grd.addColorStop(0, "rgba(242,141,82,0.06)");
      grd.addColorStop(1, "rgba(242,141,82,0)");
      ctx!.fillStyle = grd;
      ctx!.fillRect(0, 0, W, H);

      // ── Particles ─────────────────────────────────────────────────────
      PARTICLES.forEach((p) => {
        const floatY = Math.sin(t * p.speed + p.phase) * 0.06;
        const rv = rotX(
          rotY([p.v[0], p.v[1] + floatY, p.v[2]], angle * 0.25 + p.phase * 0.1),
          TILT,
        );
        const pp = project(rv, FOV, CX, CY, SCALE);
        const alpha = Math.min(0.45, Math.max(0.04, (pp.depth - 1.8) / 5));
        ctx!.fillStyle = `rgba(189,217,242,${alpha.toFixed(3)})`;
        ctx!.beginPath();
        ctx!.arc(pp.x, pp.y, p.size, 0, Math.PI * 2);
        ctx!.fill();
      });

      rafId = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(rafId);
  }, []);

  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!wrapperRef.current) return;
    gsap.fromTo(
      wrapperRef.current,
      { opacity: 0, scale: 0.9, rotateY: -15 },
      {
        opacity: 1,
        scale: 1,
        rotateY: 0,
        duration: 1.3,
        delay: 0.6,
        ease: "power3.out",
      },
    );
  }, []);

  return (
    <div
      ref={wrapperRef}
      style={{ opacity: 0 }}
      className="relative flex flex-col items-center justify-center w-full h-full select-none"
    >
      {/* Ambient glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 55% at 50% 45%, rgba(242,141,82,0.14) 0%, transparent 70%)",
        }}
        aria-hidden
      />

      <canvas
        ref={canvasRef}
        className="w-full max-w-[580px] h-auto"
        style={{ imageRendering: "crisp-edges" }}
        aria-hidden
      />

      {/* Brand caption */}
      <p className="mt-2 text-[10px] tracking-[0.45em] uppercase text-white/20 font-light">
        any room &nbsp;·&nbsp; any phone &nbsp;·&nbsp; no headset
      </p>
    </div>
  );
}
