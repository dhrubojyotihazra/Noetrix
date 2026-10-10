"use client";

import { useEffect, useRef, useState } from "react";

export default function SeamfulOrb() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [coords, setCoords] = useState({ px: 0, py: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      // Calculate normalized delta (-1.0 to 1.0)
      const maxDistanceX = window.innerWidth / 2;
      const maxDistanceY = window.innerHeight / 2;

      const px = Math.max(-1.5, Math.min(1.5, (e.clientX - centerX) / maxDistanceX));
      const py = Math.max(-1.5, Math.min(1.5, (e.clientY - centerY) / maxDistanceY));

      setCoords({ px, py });
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative w-[270px] h-[270px] sm:w-[285px] sm:h-[285px] select-none pointer-events-none"
      aria-hidden="true"
    >
      <div
        className="seamful-orb relative w-full h-full"
        style={
          {
            "--px": coords.px.toFixed(3),
            "--py": coords.py.toFixed(3),
          } as React.CSSProperties
        }
      >
        {/* Layer 1: Pastel Lavender Disc (depth 7px) - Soft borderless */}
        <div
          className="o-layer"
          style={{ "--depth": "7px" } as React.CSSProperties}
        >
          <span
            className="o-disc absolute inset-0 rounded-full"
            style={{
              backgroundColor: "#dbacf0",
              opacity: 0.85,
            }}
          />
        </div>

        {/* Layer 2: Electric Yellow Morphing Organic Blob (depth 17px) - Soft borderless */}
        <div
          className="o-layer"
          style={{ "--depth": "17px" } as React.CSSProperties}
        >
          <span
            className="o-blob absolute left-3 top-8 w-48 h-48 sm:left-4 sm:top-9 sm:w-52 sm:h-52 shadow-xs"
            style={{
              borderRadius: "38% 62% 48% 52% / 50% 45% 55% 50%",
              backgroundColor: "#fae425",
              transform: "rotate(6deg)",
            }}
          />
        </div>

        {/* Layer 3: Favicon PNG Owl floating in 3D Parallax (depth 28px) */}
        <div
          className="o-layer pointer-events-none"
          style={{ "--depth": "28px" } as React.CSSProperties}
        >
          <div className="absolute left-3 top-8 w-48 h-48 sm:left-4 sm:top-9 sm:w-52 sm:h-52 grid place-items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/favicon.png"
              alt="Noetrix Favicon Owl"
              className="w-[118px] h-[118px] sm:w-[124px] sm:h-[124px] object-contain drop-shadow-md select-none transition-transform duration-200"
              style={{
                transform: `rotate(${coords.px * 10}deg)`,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
