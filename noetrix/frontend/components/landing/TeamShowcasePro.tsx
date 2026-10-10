"use client";

import React, {
  useState,
  useRef,
  useEffect,
  useLayoutEffect,
  useCallback,
  useMemo,
} from "react";

export interface TeamMember {
  name: string;
  role: string;
  bio: string;
  imageUrl?: string;
  image?: string;
  linkOneLabel?: string;
  linkOneUrl?: string;
  linkTwoLabel?: string;
  linkTwoUrl?: string;
  email?: string;
}

export interface TeamShowcaseProProps {
  members?: TeamMember[];
  eyebrow?: string;
  heading?: string;
  portraitShare?: number;
  stageMax?: number;
  radius?: number;
  pad?: number;
  stackBelow?: number;
  dockSize?: number;
  dockGrow?: number;
  dockGap?: number;
  flight?: boolean;
  autoplay?: boolean;
  every?: number;
  pauseOnHover?: boolean;
  resumeAfter?: number;
  showPlayPause?: boolean;
  navSize?: number;
  navPreview?: boolean;
  bg?: string;
  well?: string;
  tray?: string;
  ink?: string;
  soft?: string;
  rule?: string;
  accent?: string;
  tipBg?: string;
  tipInk?: string;
}

export const DEFAULT_NOETRIX_TEAM: TeamMember[] = [
  {
    name: "Dhrubojyoti Hazra",
    role: "SCORING ENGINE · TEAM LEADER",
    bio: "Architect of the 6-part deterministic scoring engine, placement-weighted keyword algorithms, and TF-IDF matching core. Focuses on zero-black-box auditability.",
    imageUrl: "/team/dhrubojyoti.jpg",
    linkOneLabel: "LinkedIn",
    linkOneUrl: "https://www.linkedin.com/in/dhrubojyoti-hazra-a71a9a325/",
  },
  {
    name: "Adhiraj Das",
    role: "PARSING & BATCHES · TEAM LEADER",
    bio: "Built the high-throughput resume parsing pipeline, multi-format extraction (PDF, DOCX, TXT), ephemeral in-memory sessions, and recruiter batch processing.",
    imageUrl: "/team/adhiraj.jpg",
    linkOneLabel: "LinkedIn",
    linkOneUrl: "https://www.linkedin.com/in/adhiraj-das-b924283b3/",
  },
  {
    name: "Isheeka Mukhopadhyay",
    role: "MEANING MATCH & AI EDITOR",
    bio: "Developed sentence-transformer MiniLM semantic embeddings, 50-point soft knockout caps for missing must-haves, and the live before-and-after candidate bullet tailor.",
    imageUrl: "/team/isheeka.jpg",
    linkOneLabel: "LinkedIn",
    linkOneUrl: "https://www.linkedin.com/in/isheeka-mukhopadhyay-6910aa326/",
  },
  {
    name: "Samprikta De",
    role: "DESIGN & EDITOR UI",
    bio: "Crafted the Seamful editorial interface, candidate experience editor, interactive metric breakdown displays, and recruiter batch screening workflow.",
    imageUrl: "/team/samprikta.jpg",
    linkOneLabel: "LinkedIn",
    linkOneUrl: "https://www.linkedin.com/in/samprikta-de-141a46288/",
  },
  {
    name: "Tiyasha Baidya",
    role: "FAIRNESS & EXPLAINABILITY",
    bio: "Researched scoring fairness that ignores school pedigree, formulated strict impact regex validation, and designed committee-ready recruiter explainability.",
    imageUrl: "/team/tiyasha.jpg",
    linkOneLabel: "LinkedIn",
    linkOneUrl: "https://www.linkedin.com/in/tiyasha-baidya-2a6ab6283/",
  },
];

function getInitials(name?: string) {
  return String(name || "")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join("");
}

function safeMod(n: number, m: number) {
  return m > 0 ? ((n % m) + m) % m : 0;
}

export default function TeamShowcasePro({
  members = DEFAULT_NOETRIX_TEAM,
  eyebrow = "The team",
  heading = "Say hello to",
  portraitShare = 0.245,
  stageMax = 1232,
  radius = 24,
  pad = 0,
  stackBelow = 768,
  dockSize = 46,
  dockGrow = 20,
  dockGap = 12,
  flight = true,
  autoplay = true,
  every = 5,
  pauseOnHover = true,
  resumeAfter = 6,
  showPlayPause = true,
  navSize = 42,
  navPreview = true,
  bg = "transparent",
  well = "#ffffff",
  tray = "#ffffff",
  ink = "#0C0F17",
  soft = "rgba(12, 15, 23, 0.65)",
  rule = "#0C0F17",
  accent = "#0C0F17",
  tipBg = "#0C0F17",
  tipInk = "#ffffff",
}: TeamShowcaseProProps) {
  const teamList = useMemo(() => (Array.isArray(members) ? members.filter(Boolean) : []), [members]);
  const total = teamList.length;

  const rootRef = useRef<HTMLDivElement>(null);
  const stagePhotoRef = useRef<HTMLDivElement>(null);
  const flightContainerRef = useRef<HTMLDivElement>(null);
  const flightImgRef = useRef<HTMLImageElement>(null);
  const dockRowRef = useRef<HTMLDivElement>(null);
  const dockBtnRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const rafRef = useRef<number>(0);

  // Preload all team member images once on mount to eliminate image flicker
  useEffect(() => {
    teamList.forEach((m) => {
      const src = m.imageUrl || m.image;
      if (src) {
        const i = new Image();
        i.src = src;
      }
    });
  }, [teamList]);

  // Navigation state
  const [slideState, setSlideState] = useState({ now: 0, was: -1, n: 0, landed: true });
  const slideStateRef = useRef(slideState);
  slideStateRef.current = slideState;

  const [isHovered, setIsHovered] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isResting, setIsResting] = useState(false);
  const [hoveredDockIndex, setHoveredDockIndex] = useState(-1);
  const [containerWidth, setContainerWidth] = useState(1200);
  const [isVisible, setIsVisible] = useState(true);
  const [isForeground, setIsForeground] = useState(true);
  const [hasFinePointer, setHasFinePointer] = useState(true);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  // Responsive breakpoints
  const isStacked = containerWidth > 0 && containerWidth < stackBelow;

  // Responsive padding and dock sizing
  const currentDockSize = isStacked ? Math.round(dockSize * 0.84) : dockSize;
  const currentDockGap = isStacked ? Math.min(dockGap, 8) : dockGap;
  const dockRowContentWidth = total * currentDockSize + (total - 1) * currentDockGap + 20;
  const navButtonsWidth = (total > 1 ? navSize * 2 + 24 : 0) + (autoplay && showPlayPause ? navSize + 12 : 0);
  const availableDockSpace = (containerWidth || 1200) - 32 - (isStacked ? 120 : navButtonsWidth);
  const canMagnify = hasFinePointer && !isStacked && !prefersReducedMotion && dockRowContentWidth + dockGrow * 2 < availableDockSpace;
  const needScroll = !canMagnify && dockRowContentWidth > availableDockSpace;

  const activeIndex = safeMod(slideState.now, total);

  // Jump to slide
  const goToSlide = useCallback(
    (index: number) => {
      if (!total) return;
      const target = safeMod(index, total);
      const curr = slideStateRef.current;
      if (target !== curr.now) {
        setSlideState({
          now: target,
          was: curr.now,
          n: curr.n + 1,
          landed: false,
        });
      }
    },
    [total]
  );

  const handleUserNav = useCallback(
    (index: number) => {
      goToSlide(index);
      if (autoplay && resumeAfter > 0) {
        setIsResting(true);
      }
    },
    [goToSlide, autoplay, resumeAfter]
  );

  // Autoplay rest timer
  useEffect(() => {
    if (!isResting || !isVisible || !isForeground) return;
    const timer = setTimeout(() => setIsResting(false), Math.max(0.5, resumeAfter) * 1000);
    return () => clearTimeout(timer);
  }, [isResting, isVisible, isForeground, resumeAfter, slideState.n]);

  // Viewport & capability detection
  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const cleanups: (() => void)[] = [];

    if (typeof IntersectionObserver !== "undefined") {
      const observer = new IntersectionObserver(
        (entries) => {
          setIsVisible(entries.some((entry) => entry.isIntersecting));
        },
        { threshold: 0.1 }
      );
      observer.observe(el);
      cleanups.push(() => observer.disconnect());
    }

    const updateWidth = () => setContainerWidth(Math.round(el.clientWidth));
    updateWidth();

    if (typeof ResizeObserver !== "undefined") {
      const resizeObs = new ResizeObserver(updateWidth);
      resizeObs.observe(el);
      cleanups.push(() => resizeObs.disconnect());
    } else {
      window.addEventListener("resize", updateWidth);
      cleanups.push(() => window.removeEventListener("resize", updateWidth));
    }

    const updateVisibility = () => setIsForeground(!document.hidden);
    updateVisibility();
    document.addEventListener("visibilitychange", updateVisibility);
    cleanups.push(() => document.removeEventListener("visibilitychange", updateVisibility));

    if (window.matchMedia) {
      const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
      setPrefersReducedMotion(motionQuery.matches);
      const onMotion = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
      motionQuery.addEventListener ? motionQuery.addEventListener("change", onMotion) : motionQuery.addListener(onMotion);
      cleanups.push(() => (motionQuery.removeEventListener ? motionQuery.removeEventListener("change", onMotion) : motionQuery.removeListener(onMotion)));

      const pointerQuery = window.matchMedia("(hover: hover) and (pointer: fine)");
      setHasFinePointer(pointerQuery.matches);
      const onPointer = (e: MediaQueryListEvent) => setHasFinePointer(e.matches);
      pointerQuery.addEventListener ? pointerQuery.addEventListener("change", onPointer) : pointerQuery.addListener(onPointer);
      cleanups.push(() => (pointerQuery.removeEventListener ? pointerQuery.removeEventListener("change", onPointer) : pointerQuery.removeListener(onPointer)));
    }

    return () => cleanups.forEach((c) => c());
  }, []);

  // Auto-scroll dock if needed
  useEffect(() => {
    if (!needScroll) return;
    const dockRow = dockRowRef.current;
    const activeBtn = dockBtnRefs.current[activeIndex];
    if (!dockRow || !activeBtn) return;
    const targetLeft = activeBtn.offsetLeft - dockRow.clientWidth / 2 + activeBtn.offsetWidth / 2;
    if (typeof dockRow.scrollTo === "function") {
      dockRow.scrollTo({ left: targetLeft, behavior: prefersReducedMotion ? "auto" : "smooth" });
    }
  }, [activeIndex, needScroll, prefersReducedMotion]);

  // Flight Animation with double-rAF painted-swap (eliminates blink)
  useLayoutEffect(() => {
    if (slideState.landed) return;
    const root = rootRef.current;
    const stage = stagePhotoRef.current;
    const flightEl = flightContainerRef.current;
    const sourceBtn = dockBtnRefs.current[activeIndex];

    const markLanded = () => {
      setSlideState((prev) => (prev.n === slideState.n ? { ...prev, landed: true } : prev));
    };

    if (!flight || prefersReducedMotion || !root || !stage || !flightEl || !sourceBtn) {
      markLanded();
      return;
    }

    const rootBox = root.getBoundingClientRect();
    const sourceBox = sourceBtn.getBoundingClientRect();
    const stageBox = stage.getBoundingClientRect();
    const winWidth = typeof window !== "undefined" ? window.innerWidth : 0;

    if (sourceBox.right < 0 || sourceBox.left > winWidth || sourceBox.width < 4 || typeof flightEl.animate !== "function") {
      markLanded();
      return;
    }

    const currentMember = teamList[activeIndex];
    const imgSrc = currentMember?.imageUrl || currentMember?.image;
    const flightImg = flightImgRef.current;
    if (flightImg) {
      if (imgSrc) {
        flightImg.src = imgSrc;
        flightImg.style.display = "block";
      } else {
        flightImg.style.display = "none";
      }
    }

    flightEl.style.display = "block";

    const startPos = {
      left: `${sourceBox.left - rootBox.left}px`,
      top: `${sourceBox.top - rootBox.top}px`,
      width: `${sourceBox.width}px`,
      height: `${sourceBox.height}px`,
      borderRadius: `${sourceBox.width / 2}px`,
    };

    const endPos = {
      left: `${stageBox.left - rootBox.left}px`,
      top: `${stageBox.top - rootBox.top}px`,
      width: `${stageBox.width}px`,
      height: `${stageBox.height}px`,
      borderRadius: `${isStacked ? Math.min(radius, 20) : radius}px`,
    };

    const anim = flightEl.animate([startPos, endPos], {
      duration: 680,
      easing: "cubic-bezier(0.65, 0, 0.2, 1)",
      fill: "forwards",
    });

    let finished = false;
    anim.onfinish = () => {
      if (finished) return;
      finished = true;
      markLanded(); // React switches opacity: 1 on real portrait
      requestAnimationFrame(() =>
        requestAnimationFrame(() => {
          flightEl.style.display = "none"; // Hide clone only after portrait has painted
          anim.cancel();
        })
      );
    };
    anim.oncancel = () => {
      if (!finished) {
        finished = true;
        flightEl.style.display = "none";
      }
    };

    return () => {
      if (!finished) {
        finished = true;
        anim.cancel();
        flightEl.style.display = "none";
      }
    };
  }, [slideState.n, activeIndex, flight, prefersReducedMotion, teamList, radius, isStacked]);

  // Throttled Dock magnification effect using read-then-write phase
  const handleDockPointerMove = (e: React.PointerEvent) => {
    if (!canMagnify) return;
    const x = e.clientX;
    cancelAnimationFrame(rafRef.current);
    rafRef.current = requestAnimationFrame(() => {
      const btns = dockBtnRefs.current.filter(Boolean) as HTMLButtonElement[];
      // Read phase: calculate all center points at once
      const centers = btns.map((b) => {
        const r = b.getBoundingClientRect();
        return r.left + r.width / 2;
      });
      const influence = currentDockSize * 3.2;
      // Write phase: update styles without CSS transition interference
      btns.forEach((btn, i) => {
        const d = Math.abs(x - centers[i]);
        const k = d < influence ? Math.cos((d / influence) * (Math.PI / 2)) : 0;
        const s = currentDockSize + dockGrow * k * k;
        btn.style.transition = "none";
        btn.style.width = btn.style.height = `${s.toFixed(1)}px`;
      });
    });
  };

  const resetDockMagnification = () => {
    cancelAnimationFrame(rafRef.current);
    dockBtnRefs.current.forEach((btn) => {
      if (!btn) return;
      btn.style.transition = "width 220ms ease-out, height 220ms ease-out";
      btn.style.width = btn.style.height = `${currentDockSize}px`;
    });
  };

  useEffect(() => {
    resetDockMagnification();
    return () => {
      cancelAnimationFrame(rafRef.current);
    };
  }, [currentDockSize, canMagnify]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      handleUserNav(activeIndex + 1);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      handleUserNav(activeIndex - 1);
    } else if ((e.key === " " || e.key === "k") && e.target === e.currentTarget && autoplay) {
      e.preventDefault();
      setIsPaused((p) => !p);
    }
  };

  // Touch Swipe Gesture
  const touchStartRef = useRef<{ x: number; y: number } | null>(null);
  const handleTouchStart = (e: React.TouchEvent) => {
    const t = e.touches && e.touches[0];
    touchStartRef.current = t ? { x: t.clientX, y: t.clientY } : null;
  };
  const handleTouchEnd = (e: React.TouchEvent) => {
    const start = touchStartRef.current;
    const end = e.changedTouches && e.changedTouches[0];
    touchStartRef.current = null;
    if (!start || !end) return;
    const dx = end.clientX - start.x;
    const dy = end.clientY - start.y;
    if (Math.abs(dx) > 44 && Math.abs(dx) > Math.abs(dy) * 1.2) {
      handleUserNav(activeIndex + (dx < 0 ? 1 : -1));
    }
  };

  const isAutoplayActive = !!autoplay && total > 1 && !prefersReducedMotion;
  const isRingRunning =
    isAutoplayActive && !isPaused && !isResting && isVisible && isForeground && !(pauseOnHover && isHovered) && slideState.landed;

  const currentMember = teamList[activeIndex] || {};
  const previousMember = slideState.was >= 0 && slideState.was < total ? teamList[slideState.was] : null;

  const currentImg = currentMember.imageUrl || currentMember.image;
  const previousImg = previousMember ? previousMember.imageUrl || previousMember.image : null;

  const prevPeekMember = teamList[safeMod(activeIndex - 1, total)] || {};
  const nextPeekMember = teamList[safeMod(activeIndex + 1, total)] || {};

  const links = useMemo(() => {
    const res: { label: string; href: string }[] = [];
    if (currentMember.linkOneUrl) {
      res.push({ label: currentMember.linkOneLabel || "Profile", href: currentMember.linkOneUrl });
    }
    if (currentMember.linkTwoUrl) {
      res.push({ label: currentMember.linkTwoLabel || "Portfolio", href: currentMember.linkTwoUrl });
    }
    if (currentMember.email) {
      res.push({ label: "Email", href: `mailto:${currentMember.email}` });
    }
    return res;
  }, [currentMember]);

  if (!total) {
    return null;
  }

  return (
    <div
      ref={rootRef}
      role="region"
      aria-roledescription="carousel"
      aria-label="Noetrix Core Team"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        position: "relative",
        background: bg,
        padding: isStacked ? "16px 0" : `${pad}px 0`,
        boxSizing: "border-box",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: isStacked ? 18 : 24,
        color: ink,
        outline: "none",
        width: "100%",
      }}
    >
      <style>{`
        @keyframes noetrix-in {
          from { opacity: 0; transform: translate3d(0, 14px, 0); }
          to { opacity: 1; transform: none; }
        }
        @keyframes noetrix-ring {
          from { stroke-dashoffset: 100; }
          to { stroke-dashoffset: 0; }
        }
        .noetrix-nav {
          transition: transform 220ms cubic-bezier(0.2, 0.8, 0.2, 1), background-color 200ms, color 200ms, box-shadow 220ms;
        }
        .noetrix-nav:hover {
          background: #0C0F17 !important;
          color: #FAE425 !important;
          transform: translateY(-2px);
          box-shadow: 0 10px 24px rgba(12, 15, 23, 0.16) !important;
        }
        .noetrix-nav:active {
          transform: scale(0.94);
        }
        .noetrix-nav:focus-visible {
          outline: 2px solid #0C0F17;
          outline-offset: 3px;
        }
        .noetrix-peek {
          opacity: 0;
          transform: translate(-50%, 6px);
          transition: opacity 180ms, transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        .noetrix-nav:hover .noetrix-peek,
        .noetrix-nav:focus-visible .noetrix-peek {
          opacity: 1;
          transform: translate(-50%, 0);
        }
        .noetrix-dock-btn:focus-visible {
          outline: 2px solid #0C0F17;
          outline-offset: 3px;
        }
        .noetrix-link-btn {
          transition: background-color 200ms, color 200ms, border-color 200ms, transform 200ms;
        }
        .noetrix-link-btn:hover {
          background: #0C0F17 !important;
          color: #ffffff !important;
          border-color: #0C0F17 !important;
          transform: translateY(-1px);
        }
        .noetrix-dock-row {
          scrollbar-width: none;
        }
        .noetrix-dock-row::-webkit-scrollbar {
          display: none;
        }
      `}</style>

      {/* Top Header: Eyebrow + Tabular Index Counter */}
      <div
        style={{
          alignSelf: "stretch",
          maxWidth: stageMax,
          width: "100%",
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: 13,
          color: soft,
          flex: "0 0 auto",
          fontWeight: 600,
          letterSpacing: "0.08em",
          textTransform: "uppercase",
        }}
      >
        <span className="font-sans font-bold text-ink/75">{eyebrow}</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }} className="font-mono text-sm">
          <span style={{ color: ink, fontWeight: 700 }}>
            {String(activeIndex + 1).padStart(2, "0")}
          </span>{" "}
          / {String(total).padStart(2, "0")}
        </span>
      </div>

      {/* Main Stage: Portrait Image + Member Details */}
      <div
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        style={{
          width: "100%",
          maxWidth: stageMax,
          margin: "0 auto",
          flex: "0 0 auto",
          minHeight: 0,
          display: "flex",
          flexDirection: isStacked ? "column" : "row",
          alignItems: isStacked ? "stretch" : "center",
          gap: isStacked ? 20 : 40,
        }}
      >
        {/* Left Column: Portrait Stage */}
        <div
          ref={stagePhotoRef}
          style={{
            position: "relative",
            borderRadius: isStacked ? 20 : radius,
            overflow: "hidden",
            background: well,
            boxShadow: "0 16px 48px -12px rgba(12, 15, 23, 0.12)",
            border: `2px solid ${rule}`,
            ...(isStacked
              ? { width: "100%", aspectRatio: "1 / 1", flex: "0 0 auto", maxHeight: 380 }
              : { flex: `0 0 ${portraitShare * 100}%`, minHeight: 0, aspectRatio: "4 / 5" }),
          }}
        >
          {/* Previous image layer: stays fully visible (opacity 1, transform none) until swap */}
          {!slideState.landed && previousImg && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                transform: "none",
                opacity: 1,
                borderRadius: isStacked ? 20 : radius,
                overflow: "hidden",
              }}
            >
              <img
                src={previousImg}
                alt=""
                style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
              />
            </div>
          )}

          {/* Current portrait image layer: direct visibility swap without fading to avoid flash */}
          <div
            key={`face-${slideState.n}`}
            style={{
              position: "absolute",
              inset: 0,
              opacity: slideState.landed ? 1 : 0,
            }}
          >
            {currentImg ? (
              <img
                src={currentImg}
                alt={currentMember.name}
                draggable={false}
                style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
              />
            ) : (
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 72,
                  fontWeight: 700,
                  color: ink,
                  opacity: 0.2,
                }}
              >
                {getInitials(currentMember.name)}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Member Details (Title, Name, Role, Bio, Links) */}
        <div
          aria-live="polite"
          key={`txt-${slideState.n}`}
          style={{
            flex: "1 1 0",
            minWidth: 0,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          {/* Kicker */}
          {heading ? (
            <div
              style={{
                fontSize: 14,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                color: soft,
                marginBottom: isStacked ? 10 : 16,
                animation: slideState.n > 0 && !prefersReducedMotion ? "noetrix-in 500ms cubic-bezier(0.2, 0.8, 0.2, 1) 250ms both" : undefined,
              }}
            >
              {heading}
            </div>
          ) : null}

          {/* Display Name (250ms + 60ms = 310ms delay to sync with flight arrival) */}
          <h3
            className="font-display tracking-tight text-ink uppercase"
            style={{
              fontSize: isStacked ? 36 : 56,
              lineHeight: 0.94,
              margin: 0,
              animation: slideState.n > 0 && !prefersReducedMotion ? "noetrix-in 560ms cubic-bezier(0.2, 0.8, 0.2, 1) 310ms both" : undefined,
            }}
          >
            {currentMember.name}
          </h3>

          {/* Role Pill / Accent Dot (370ms delay) */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginTop: 14,
              animation: slideState.n > 0 && !prefersReducedMotion ? "noetrix-in 580ms cubic-bezier(0.2, 0.8, 0.2, 1) 370ms both" : undefined,
            }}
          >
            <span
              style={{
                width: 9,
                height: 9,
                borderRadius: "50%",
                background: accent,
                display: "inline-block",
                boxShadow: "0 0 0 3px rgba(12, 15, 23, 0.15)",
              }}
            />
            <span
              className="font-sans font-bold text-xs sm:text-sm uppercase tracking-wider text-ink"
            >
              {currentMember.role}
            </span>
          </div>

          {/* Bio Description (430ms delay) */}
          {currentMember.bio && (
            <p
              className="font-sans text-sm sm:text-[15px] text-ink leading-relaxed font-normal"
              style={{
                marginTop: isStacked ? 12 : 16,
                maxWidth: 620,
                animation: slideState.n > 0 && !prefersReducedMotion ? "noetrix-in 600ms cubic-bezier(0.2, 0.8, 0.2, 1) 430ms both" : undefined,
              }}
            >
              {currentMember.bio}
            </p>
          )}

          {/* External Links (LinkedIn button) (490ms delay) */}
          {links.length > 0 && (
            <div
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: 10,
                marginTop: isStacked ? 20 : 28,
                animation: slideState.n > 0 && !prefersReducedMotion ? "noetrix-in 620ms cubic-bezier(0.2, 0.8, 0.2, 1) 490ms both" : undefined,
              }}
            >
              {links.map((link, idx) => (
                <a
                  key={`link-${idx}`}
                  href={link.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="noetrix-link-btn font-sans"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 7,
                    height: 40,
                    padding: "0 18px",
                    borderRadius: 40,
                    background: "#ffffff",
                    border: `1.5px solid #0C0F17`,
                    color: ink,
                    fontSize: 13,
                    fontWeight: 700,
                    textDecoration: "none",
                    boxShadow: "0 2px 6px rgba(12, 15, 23, 0.06)",
                  }}
                >
                  <span>{link.label}</span>
                  <span aria-hidden="true" style={{ fontSize: 14 }}>↗</span>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation Dock */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: isStacked ? 8 : 14,
          maxWidth: "100%",
          width: "100%",
          justifyContent: "center",
          flex: "0 0 auto",
          marginTop: 0,
        }}
      >
        {/* Previous Button */}
        {total > 1 && (
          <button
            type="button"
            aria-label={`Previous: ${prevPeekMember.name || ""}`}
            className="noetrix-nav"
            onClick={() => handleUserNav(activeIndex - 1)}
            style={{
              position: "relative",
              width: navSize,
              height: navSize,
              borderRadius: navSize,
              border: `2px solid #0C0F17`,
              background: "#ffffff",
              color: ink,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 0,
              flex: "0 0 auto",
              boxShadow: "0 2px 8px rgba(12, 15, 23, 0.08)",
              marginBottom: Math.max(0, Math.round((currentDockSize + 20 - navSize) / 2)),
            }}
          >
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
              <path d="M13 8H3M7 4 3 8l4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>

            {/* Hover Peek Tooltip */}
            {navPreview && hasFinePointer && prevPeekMember.name && (
              <span
                aria-hidden="true"
                className="noetrix-peek font-sans"
                style={{
                  position: "absolute",
                  left: "50%",
                  bottom: "100%",
                  marginBottom: 12,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "5px 12px 5px 5px",
                  borderRadius: 999,
                  background: tipBg,
                  color: tipInk,
                  whiteSpace: "nowrap",
                  pointerEvents: "none",
                  textAlign: "left",
                  boxShadow: "0 10px 24px rgba(0, 0, 0, 0.2)",
                  border: "1px solid rgba(255,255,255,0.15)",
                }}
              >
                <span
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    overflow: "hidden",
                    background: well,
                    flex: "0 0 auto",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 10,
                    fontWeight: 700,
                    color: ink,
                  }}
                >
                  {prevPeekMember.imageUrl ? (
                    <img src={prevPeekMember.imageUrl} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    getInitials(prevPeekMember.name)
                  )}
                </span>
                <span style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
                  <span style={{ fontSize: 9, opacity: 0.6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Previous</span>
                  <span style={{ fontSize: 12, fontWeight: 600 }}>{prevPeekMember.name}</span>
                </span>
              </span>
            )}
          </button>
        )}

        {/* Center Pill Dock Container */}
        <div
          style={{
            position: "relative",
            minWidth: 0,
            flex: isStacked ? "1 1 auto" : "0 1 auto",
            height: currentDockSize + 20 + (canMagnify ? dockGrow : 0),
            display: "flex",
            alignItems: "flex-end",
          }}
        >
          {/* Dock Pill Background */}
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              bottom: 0,
              height: currentDockSize + 20,
              borderRadius: currentDockSize + 20,
              background: tray,
              border: `2px solid #0C0F17`,
              boxShadow: "0 6px 24px rgba(12, 15, 23, 0.08)",
              overflow: "hidden",
            }}
          />

          {/* Row of Avatar Buttons */}
          <div
            ref={dockRowRef}
            role="tablist"
            aria-label="Team members"
            className="noetrix-dock-row"
            onPointerMove={handleDockPointerMove}
            onPointerLeave={() => {
              resetDockMagnification();
              setHoveredDockIndex(-1);
            }}
            style={{
              position: "relative",
              display: "flex",
              alignItems: "flex-end",
              gap: currentDockGap,
              padding: `${canMagnify ? dockGrow : 0}px 10px 10px`,
              overflowX: needScroll ? "auto" : "visible",
              overflowY: needScroll ? "hidden" : "visible",
              maxWidth: "100%",
              boxSizing: "border-box",
            }}
          >
            {teamList.map((member, idx) => {
              const isSelected = idx === activeIndex;
              const avatarImg = member.imageUrl || member.image;

              return (
                <button
                  key={`dock-member-${idx}`}
                  ref={(el) => {
                    dockBtnRefs.current[idx] = el;
                  }}
                  type="button"
                  role="tab"
                  aria-selected={isSelected}
                  aria-label={member.name || `Member ${idx + 1}`}
                  className="noetrix-dock-btn"
                  onClick={() => handleUserNav(idx)}
                  onPointerEnter={() => canMagnify && setHoveredDockIndex(idx)}
                  onFocus={() => setHoveredDockIndex(idx)}
                  onBlur={() => setHoveredDockIndex(-1)}
                  style={{
                    position: "relative",
                    width: currentDockSize,
                    height: currentDockSize,
                    flex: "0 0 auto",
                    padding: 0,
                    border: "none",
                    borderRadius: "50%",
                    background: well,
                    cursor: "pointer",
                    boxShadow: isSelected && !isAutoplayActive ? `0 0 0 2px ${tray}, 0 0 0 4.5px #0C0F17` : "none",
                  }}
                >
                  {/* Member Avatar Thumbnail */}
                  <span
                    style={{
                      position: "absolute",
                      inset: 0,
                      borderRadius: "50%",
                      overflow: "hidden",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 13,
                      fontWeight: 700,
                      color: ink,
                      opacity: isSelected && !slideState.landed ? 0.3 : 1,
                      transition: "opacity 300ms",
                    }}
                  >
                    {avatarImg ? (
                      <img
                        src={avatarImg}
                        alt=""
                        draggable={false}
                        style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
                      />
                    ) : (
                      getInitials(member.name)
                    )}
                  </span>

                  {/* Animated Countdown Progress Ring when Autoplay is active */}
                  {isSelected && isAutoplayActive ? (
                    <svg
                      aria-hidden="true"
                      viewBox="0 0 100 100"
                      style={{
                        position: "absolute",
                        left: -5,
                        top: -5,
                        width: "calc(100% + 10px)",
                        height: "calc(100% + 10px)",
                        transform: "rotate(-90deg)",
                        overflow: "visible",
                        pointerEvents: "none",
                      }}
                    >
                      <circle cx="50" cy="50" r="48" fill="none" stroke="rgba(12, 15, 23, 0.15)" strokeWidth="2.5" />
                      <circle
                        cx="50"
                        cy="50"
                        r="48"
                        fill="none"
                        stroke="#0C0F17"
                        strokeWidth="3.2"
                        strokeLinecap="round"
                        pathLength={100}
                        strokeDasharray="100"
                        strokeDashoffset="100"
                        onAnimationEnd={() => goToSlide(activeIndex + 1)}
                        style={{
                          animation: `noetrix-ring ${Math.max(2, every)}s linear forwards`,
                          animationPlayState: isRingRunning ? "running" : "paused",
                        }}
                        key={`ring-${slideState.n}`}
                      />
                    </svg>
                  ) : null}

                  {/* Avatar Name Tooltip */}
                  {hoveredDockIndex === idx && member.name && (
                    <span
                      role="tooltip"
                      className="font-sans"
                      style={{
                        position: "absolute",
                        left: "50%",
                        bottom: "100%",
                        marginBottom: 12,
                        transform: "translateX(-50%)",
                        padding: "6px 12px",
                        borderRadius: 8,
                        background: tipBg,
                        color: tipInk,
                        fontSize: 12,
                        fontWeight: 600,
                        whiteSpace: "nowrap",
                        pointerEvents: "none",
                        boxShadow: "0 6px 16px rgba(0, 0, 0, 0.2)",
                        zIndex: 30,
                        border: "1px solid rgba(255,255,255,0.15)",
                      }}
                    >
                      {member.name}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Next Button */}
        {total > 1 && (
          <button
            type="button"
            aria-label={`Next: ${nextPeekMember.name || ""}`}
            className="noetrix-nav"
            onClick={() => handleUserNav(activeIndex + 1)}
            style={{
              position: "relative",
              width: navSize,
              height: navSize,
              borderRadius: navSize,
              border: `2px solid #0C0F17`,
              background: "#ffffff",
              color: ink,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 0,
              flex: "0 0 auto",
              boxShadow: "0 2px 8px rgba(12, 15, 23, 0.08)",
              marginBottom: Math.max(0, Math.round((currentDockSize + 20 - navSize) / 2)),
            }}
          >
            <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>

            {/* Hover Peek Tooltip */}
            {navPreview && hasFinePointer && nextPeekMember.name && (
              <span
                aria-hidden="true"
                className="noetrix-peek font-sans"
                style={{
                  position: "absolute",
                  left: "50%",
                  bottom: "100%",
                  marginBottom: 12,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "5px 12px 5px 5px",
                  borderRadius: 999,
                  background: tipBg,
                  color: tipInk,
                  whiteSpace: "nowrap",
                  pointerEvents: "none",
                  textAlign: "left",
                  boxShadow: "0 10px 24px rgba(0, 0, 0, 0.2)",
                  border: "1px solid rgba(255,255,255,0.15)",
                }}
              >
                <span
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: "50%",
                    overflow: "hidden",
                    background: well,
                    flex: "0 0 auto",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 10,
                    fontWeight: 700,
                    color: ink,
                  }}
                >
                  {nextPeekMember.imageUrl ? (
                    <img src={nextPeekMember.imageUrl} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    getInitials(nextPeekMember.name)
                  )}
                </span>
                <span style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
                  <span style={{ fontSize: 9, opacity: 0.6, textTransform: "uppercase", letterSpacing: "0.06em" }}>Next</span>
                  <span style={{ fontSize: 12, fontWeight: 600 }}>{nextPeekMember.name}</span>
                </span>
              </span>
            )}
          </button>
        )}

        {/* Play / Pause Autoplay Button */}
        {isAutoplayActive && showPlayPause && (
          <button
            type="button"
            aria-label={isPaused ? "Resume autoplay" : "Pause autoplay"}
            aria-pressed={isPaused}
            className="noetrix-nav"
            onClick={() => {
              setIsPaused((p) => !p);
              setIsResting(false);
            }}
            style={{
              position: "relative",
              width: Math.round(navSize * 0.84),
              height: Math.round(navSize * 0.84),
              borderRadius: navSize,
              border: `2px solid #0C0F17`,
              background: "#ffffff",
              color: ink,
              cursor: "pointer",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              padding: 0,
              flex: "0 0 auto",
              boxShadow: "0 2px 6px rgba(12, 15, 23, 0.06)",
              marginBottom: Math.max(0, Math.round((currentDockSize + 20 - Math.round(navSize * 0.84)) / 2)),
            }}
          >
            {isPaused ? (
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                <path d="M3 1.8v8.4L10 6z" />
              </svg>
            ) : (
              <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                <rect x="2.4" y="1.8" width="2.6" height="8.4" rx="0.8" />
                <rect x="7" y="1.8" width="2.6" height="8.4" rx="0.8" />
              </svg>
            )}
          </button>
        )}
      </div>

      {/* Flight Clone Container (animates when an avatar flies into the main portrait) */}
      <div
        ref={flightContainerRef}
        aria-hidden="true"
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 0,
          height: 0,
          overflow: "hidden",
          background: well,
          zIndex: 40,
          pointerEvents: "none",
          display: "none",
          boxShadow: "0 24px 64px rgba(12, 15, 23, 0.2)",
          border: `2px solid #0C0F17`,
        }}
      >
        <img
          ref={flightImgRef}
          alt=""
          draggable={false}
          style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
        />
      </div>
    </div>
  );
}
