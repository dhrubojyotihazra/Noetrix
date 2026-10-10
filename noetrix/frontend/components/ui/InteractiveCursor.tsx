"use client";

import { useEffect, useState } from "react";

export default function InteractiveCursor() {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [isVisible, setIsVisible] = useState(false);
  const [hoverText, setHoverText] = useState<string | null>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });
      if (!isVisible) setIsVisible(true);

      // Check if hovering over an interactive card or button
      const target = e.target as HTMLElement | null;
      if (target?.closest("a, button, [data-interactive]")) {
        const customLabel = target.closest("[data-cursor-text]")?.getAttribute("data-cursor-text");
        setHoverText(customLabel || "Click");
      } else {
        setHoverText(null);
      }
    };

    const handleMouseLeave = () => setIsVisible(false);

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    document.documentElement.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.documentElement.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div
      className="fixed pointer-events-none z-50 transition-transform duration-75 ease-out -translate-x-1/2 -translate-y-1/2"
      style={{
        left: `${pos.x}px`,
        top: `${pos.y}px`,
      }}
    >
      {/* Outer Glow Ring / Follower */}
      <div
        className={`rounded-full transition-all duration-200 border border-ink flex items-center justify-center ${
          hoverText
            ? "w-16 h-16 bg-accent-yellow/90 scale-100 shadow-lg"
            : "w-8 h-8 bg-accent-lilac/30 scale-75"
        }`}
      >
        {hoverText ? (
          <span className="font-sans text-[10px] font-bold text-ink uppercase tracking-wider select-none">
            {hoverText}
          </span>
        ) : (
          <div className="w-2 h-2 rounded-full bg-ink" />
        )}
      </div>
    </div>
  );
}
