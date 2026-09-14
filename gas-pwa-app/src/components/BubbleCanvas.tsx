import React, { useEffect, useRef, useState } from 'react';
import type { BubbleData, Stage, GasItem } from '../types/game';

type Props = {
  stage: Stage;
  activeGases: GasItem[];
  shakeTarget: string | null;
  onBubbleTap: (gas: GasItem, tapX: number, tapY: number) => void;
};

// Array shuffle helper
function shuffleArray<T>(array: T[]): T[] {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

export const BubbleCanvas: React.FC<Props> = ({
  stage,
  activeGases,
  shakeTarget,
  onBubbleTap,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [bubbles, setBubbles] = useState<BubbleData[]>([]);
  const animFrameRef = useRef<number | null>(null);
  const containerSizeRef = useRef<{ w: number; h: number }>({ w: 360, h: 500 });

  // Re-generate bubbles whenever stage or remaining activeGases change, or container resizes
  useEffect(() => {
    if (!containerRef.current || activeGases.length === 0) return;

    const updateDimensionsAndBubbles = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const w = rect.width > 150 ? rect.width : window.innerWidth;
      const h = rect.height > 150 ? rect.height : Math.max(window.innerHeight - 200, 480);
      containerSizeRef.current = { w, h };

      const displayList = stage === 1 ? activeGases : shuffleArray(activeGases);

      // Scale bubble size according to screen width
      const size = Math.min(Math.max(w * 0.22, 70), 95);

      const initialBubbles: BubbleData[] = displayList.map((gas) => {
        const angle = Math.random() * Math.PI * 2;
        const speed = 0.8 + Math.random() * 1.2;

        let label = '';
        if (stage === 1) label = gas.korean;
        else if (stage === 2) label = gas.formula;
        else label = gas.colorName;

        return {
          id: gas.id,
          gasId: gas.id,
          label,
          x: size + Math.random() * (w - size * 2),
          y: size + Math.random() * (h - size * 2),
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          size,
          colorHex: stage === 3 ? gas.colorHex : undefined,
          borderHex: stage === 3 ? gas.borderHex : undefined,
          isDarkText: stage === 3 ? gas.isDarkText : false,
        };
      });

      setBubbles(initialBubbles);
    };

    updateDimensionsAndBubbles();

    const resizeObserver = new ResizeObserver(() => {
      updateDimensionsAndBubbles();
    });
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      resizeObserver.disconnect();
    };
  }, [stage, activeGases]);

  // Physics animation loop using dynamic container bounds
  useEffect(() => {
    let lastTime = performance.now();

    const updatePhysics = (now: number) => {
      const delta = Math.min((now - lastTime) / 16.6, 2);
      lastTime = now;

      const { w, h } = containerSizeRef.current;

      setBubbles((prevBubbles) =>
        prevBubbles.map((b) => {
          let { x, y, vx, vy, size } = b;

          x += vx * delta;
          y += vy * delta;

          const radius = size / 2;

          // Wall bounce physics using full container height
          if (x - radius <= 0) { x = radius; vx = Math.abs(vx); }
          if (x + radius >= w) { x = w - radius; vx = -Math.abs(vx); }
          if (y - radius <= 0) { y = radius; vy = Math.abs(vy); }
          if (y + radius >= h) { y = h - radius; vy = -Math.abs(vy); }

          return { ...b, x, y, vx, vy };
        })
      );

      animFrameRef.current = requestAnimationFrame(updatePhysics);
    };

    animFrameRef.current = requestAnimationFrame(updatePhysics);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  // Stage theme styling
  let stageBorder = '#4fc3f7';
  let stageBadgeBg = 'rgba(79, 195, 247, 0.25)';
  let stageBadgeText = '1단계: 이름';

  if (stage === 2) {
    stageBorder = '#69f0ae';
    stageBadgeBg = 'rgba(105, 240, 174, 0.25)';
    stageBadgeText = '2단계: 화학식';
  } else if (stage === 3) {
    stageBorder = '#ffd700';
    stageBadgeBg = 'rgba(255, 241, 118, 0.25)';
    stageBadgeText = '3단계: 용기색상';
  }

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      {bubbles.map((b) => {
        const gasItem = activeGases.find((g) => g.id === b.gasId);
        if (!gasItem) return null;

        const isShaking = shakeTarget === b.id;
        const radius = b.size / 2;

        const bubbleBg =
          stage === 3 && b.colorHex
            ? b.colorHex
            : '#FFFFFF';

        const borderColor =
          stage === 3 && b.borderHex
            ? b.borderHex
            : stageBorder;

        const textColor =
          stage === 3
            ? (b.isDarkText ? '#0F172A' : '#FFFFFF')
            : '#0F172A';

        return (
          <div
            key={b.id}
            onClick={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              onBubbleTap(gasItem, rect.left + rect.width / 2, rect.top + rect.height / 2);
            }}
            className={isShaking ? 'shake-anim' : ''}
            style={{
              position: 'absolute',
              left: `${b.x - radius}px`,
              top: `${b.y - radius}px`,
              width: `${b.size}px`,
              height: `${b.size}px`,
              borderRadius: '50%',
              backgroundColor: bubbleBg,
              border: `3px solid ${borderColor}`,
              boxShadow: `0 4px 15px rgba(15, 23, 42, 0.1), 0 0 12px ${borderColor}44`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'transform 0.15s ease-out, border-color 0.2s',
              zIndex: 10,
            }}
          >
            {/* Stage type badge */}
            <span
              style={{
                fontSize: '0.65rem',
                fontWeight: 800,
                color: stageBorder,
                backgroundColor: stageBadgeBg,
                padding: '2px 6px',
                borderRadius: '8px',
                marginBottom: '3px',
              }}
            >
              {stageBadgeText}
            </span>

            {/* Bubble Label Text */}
            <span
              style={{
                fontWeight: 900,
                fontSize: b.label.length > 4 ? '0.9rem' : b.label.length > 3 ? '1.05rem' : '1.25rem',
                color: textColor,
                textAlign: 'center',
                lineHeight: 1.1,
              }}
            >
              {b.label}
            </span>
          </div>
        );
      })}
    </div>
  );
};
