import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import { KEY_NUMBERS_DATA } from '../data/numberData';
import type { NumberGasItem } from '../data/numberData';

interface NumberGameScreenProps {
  onBackToHome: () => void;
}

interface BubblePhysics {
  id: string;
  type: 'value' | 'name';
  text: string;
  color: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  itemId: string;
}

export const NumberGameScreen: React.FC<NumberGameScreenProps> = ({ onBackToHome }) => {
  const [stage, setStage] = useState<1 | 2 | 3>(1);
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);

  // Stage 1 State
  const [stage1Items, setStage1Items] = useState<NumberGasItem[]>([]);
  const [stage1Index, setStage1Index] = useState(0);

  // Stage 2 State
  const [stage2MatchedIds, setStage2MatchedIds] = useState<string[]>([]);
  const [selectedBubble, setSelectedBubble] = useState<BubblePhysics | null>(null);

  // Stage 3 State
  const [stage3Items, setStage3Items] = useState<NumberGasItem[]>([]);
  const [stage3Index, setStage3Index] = useState(0);
  const [lowerInput, setLowerInput] = useState('');
  const [upperInput, setUpperInput] = useState('');
  const [activeInputTarget, setActiveInputTarget] = useState<'lower' | 'upper'>('lower');

  // UI state
  const [feedbackMsg, setFeedbackMsg] = useState<{ text: string; isError: boolean } | null>(null);
  const [showWinModal, setShowWinModal] = useState(false);

  // DOM Container & Bubbles
  const containerRef = useRef<HTMLDivElement>(null);
  const [bubbles, setBubbles] = useState<BubblePhysics[]>([]);
  const animFrameRef = useRef<number | null>(null);
  const containerSizeRef = useRef<{ w: number; h: number }>({ w: 360, h: 500 });

  // Initialize Stage 1
  useEffect(() => {
    startNewGame();
  }, []);

  const startNewGame = () => {
    const shuffled = [...KEY_NUMBERS_DATA].sort(() => Math.random() - 0.5);
    setStage1Items(shuffled);
    setStage1Index(0);
    setStage(1);
    setScore(0);
    setCombo(0);
    setStage2MatchedIds([]);
    setSelectedBubble(null);
    setShowWinModal(false);
    setFeedbackMsg(null);
  };

  // Re-initialize bubble list when stage or matched items change
  useEffect(() => {
    if (!containerRef.current) return;

    const updateDimensionsAndBubbles = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const w = rect.width > 150 ? rect.width : window.innerWidth;
      const h = rect.height > 150 ? rect.height : Math.max(window.innerHeight - 200, 480);
      containerSizeRef.current = { w, h };

      if (stage === 1) {
        const size = Math.min(Math.max(w * 0.22, 76), 96);
        const list: BubblePhysics[] = KEY_NUMBERS_DATA.map((item) => {
          const angle = Math.random() * Math.PI * 2;
          const speed = 0.8 + Math.random() * 1.2;
          return {
            id: `s1-val-${item.id}`,
            type: 'value',
            text: item.displayShort,
            color: item.color,
            x: size + Math.random() * (w - size * 2),
            y: size + Math.random() * (h - size * 2),
            vx: Math.cos(angle) * speed,
            vy: Math.sin(angle) * speed,
            size,
            itemId: item.id,
          };
        });
        setBubbles(list);
      } else if (stage === 2) {
        const remainingItems = KEY_NUMBERS_DATA.filter((i) => !stage2MatchedIds.includes(i.id));
        const size = Math.min(Math.max(w * 0.2, 70), 88);
        const list: BubblePhysics[] = [];

        remainingItems.forEach((item) => {
          const angle1 = Math.random() * Math.PI * 2;
          const speed1 = 0.8 + Math.random() * 1.2;
          list.push({
            id: `s2-name-${item.id}`,
            type: 'name',
            text: item.name,
            color: '#3B82F6',
            x: size + Math.random() * (w - size * 2),
            y: size + Math.random() * (h - size * 2),
            vx: Math.cos(angle1) * speed1,
            vy: Math.sin(angle1) * speed1,
            size,
            itemId: item.id,
          });

          const angle2 = Math.random() * Math.PI * 2;
          const speed2 = 0.8 + Math.random() * 1.2;
          list.push({
            id: `s2-val-${item.id}`,
            type: 'value',
            text: item.displayShort,
            color: item.color,
            x: size + Math.random() * (w - size * 2),
            y: size + Math.random() * (h - size * 2),
            vx: Math.cos(angle2) * speed2,
            vy: Math.sin(angle2) * speed2,
            size,
            itemId: item.id,
          });
        });
        setBubbles(list);
      }
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
  }, [stage, stage1Index, stage2MatchedIds]);

  // Smooth DOM Bubble Physics Animation Loop
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

          // Wall bounce physics using dynamic container bounds
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

  // Handle Bubble Tap
  const handleBubbleTap = (b: BubblePhysics, tapX: number, tapY: number) => {
    if (stage === 1) {
      const currentQ = stage1Items[stage1Index];
      if (b.itemId === currentQ.id) {
        // Correct!
        confetti({
          particleCount: 40,
          spread: 60,
          origin: { x: tapX / window.innerWidth, y: tapY / window.innerHeight },
        });
        setScore((prev) => prev + 100 + combo * 20);
        setCombo((prev) => prev + 1);
        setFeedbackMsg({ text: `정답! ${currentQ.name}: ${currentQ.targetValue}`, isError: false });

        if (stage1Index + 1 < stage1Items.length) {
          setStage1Index((prev) => prev + 1);
        } else {
          // Advance to Stage 2
          setFeedbackMsg({ text: '🎉 1 Stage 통과! 2 Stage 짝맞추기 시작!', isError: false });
          setTimeout(() => {
            setStage(2);
            setSelectedBubble(null);
            setFeedbackMsg(null);
          }, 1200);
        }
      } else {
        // Wrong
        setCombo(0);
        setFeedbackMsg({ text: '오답입니다! 정답 수치를 다시 터치하세요.', isError: true });
      }
    } else if (stage === 2) {
      if (!selectedBubble) {
        setSelectedBubble(b);
      } else if (selectedBubble.id === b.id) {
        setSelectedBubble(null);
      } else {
        // Check match
        if (selectedBubble.itemId === b.itemId && selectedBubble.type !== b.type) {
          // Match success!
          confetti({
            particleCount: 45,
            spread: 70,
            origin: { x: tapX / window.innerWidth, y: tapY / window.innerHeight },
          });
          setScore((prev) => prev + 150);
          setCombo((prev) => prev + 1);
          const newMatched = [...stage2MatchedIds, b.itemId];
          setStage2MatchedIds(newMatched);
          setSelectedBubble(null);
          setFeedbackMsg({ text: `짝 맞추기 성공! (${b.itemId})`, isError: false });

          if (newMatched.length === KEY_NUMBERS_DATA.length) {
            // Advance to Stage 3
            setFeedbackMsg({ text: '🔥 2 Stage 통과! 마지막 3 Stage 직접 입력 도전!', isError: false });
            setTimeout(() => {
              const shuffled3 = [...KEY_NUMBERS_DATA].sort(() => Math.random() - 0.5);
              setStage3Items(shuffled3);
              setStage3Index(0);
              setLowerInput('');
              setUpperInput('');
              setActiveInputTarget('lower');
              setStage(3);
              setFeedbackMsg(null);
            }, 1400);
          }
        } else {
          // Match failed
          setCombo(0);
          setFeedbackMsg({ text: '서로 다른 짝입니다! 짝을 다시 선택하세요.', isError: true });
          setSelectedBubble(null);
        }
      }
    }
  };

  // Stage 3 Keypad input
  const handleKeypadPress = (val: string) => {
    if (val === 'DEL') {
      if (activeInputTarget === 'lower') setLowerInput((prev) => prev.slice(0, -1));
      else setUpperInput((prev) => prev.slice(0, -1));
    } else if (val === 'CLEAR') {
      if (activeInputTarget === 'lower') setLowerInput('');
      else setUpperInput('');
    } else {
      if (activeInputTarget === 'lower') {
        if (lowerInput.length < 6) setLowerInput((prev) => prev + val);
      } else {
        if (upperInput.length < 6) setUpperInput((prev) => prev + val);
      }
    }
  };

  // Stage 3 Submit
  const handleStage3Submit = () => {
    const currentItem = stage3Items[stage3Index];
    let isCorrect = false;

    if (currentItem.upperBound) {
      isCorrect =
        lowerInput.trim() === currentItem.lowerBound &&
        upperInput.trim() === currentItem.upperBound;
    } else {
      isCorrect = lowerInput.trim() === currentItem.lowerBound;
    }

    if (isCorrect) {
      confetti({ particleCount: 60, spread: 80, origin: { y: 0.6 } });
      setScore((prev) => prev + 300);
      setFeedbackMsg({ text: `정답입니다! (${currentItem.name}: ${currentItem.targetValue})`, isError: false });

      if (stage3Index + 1 < stage3Items.length) {
        setStage3Index((prev) => prev + 1);
        setLowerInput('');
        setUpperInput('');
        setActiveInputTarget('lower');
      } else {
        // Complete Game!
        setShowWinModal(true);
      }
    } else {
      // WRONG IN STAGE 3 -> HARDCORE RESET TO STAGE 1!
      setFeedbackMsg({
        text: `🚨 오답! (정답: ${currentItem.targetValue}) 1 Stage부터 다시 도전하세요!`,
        isError: true,
      });

      setTimeout(() => {
        const shuffled = [...KEY_NUMBERS_DATA].sort(() => Math.random() - 0.5);
        setStage1Items(shuffled);
        setStage1Index(0);
        setStage(1);
        setCombo(0);
        setStage2MatchedIds([]);
        setSelectedBubble(null);
        setLowerInput('');
        setUpperInput('');
      }, 2000);
    }
  };

  const currentStage1Item = stage1Items[stage1Index];
  const currentStage3Item = stage3Items[stage3Index];

  return (
    <div style={{ width: '100%', minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#F8FAFC', position: 'relative', overflowY: 'auto' }}>
      {/* Top Bar */}
      <div style={{ padding: 'max(12px, env(safe-area-inset-top)) 16px 12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#FFFFFF', borderBottom: '1px solid #E2E8F0', zIndex: 100, boxShadow: '0 2px 10px rgba(0,0,0,0.03)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onBackToHome}
            style={{ background: 'none', border: 'none', color: '#64748B', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem', fontWeight: 800, cursor: 'pointer' }}
          >
            ← 이전으로
          </button>
          <button
            onClick={() => {
              window.location.href = '/game-menu.html';
            }}
            style={{ backgroundColor: '#0284C7', color: '#FFFFFF', border: 'none', padding: '6px 14px', borderRadius: '10px', fontSize: '0.82rem', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', boxShadow: '0 3px 10px rgba(2, 132, 199, 0.25)' }}
          >
            🧠 치매 예방 센터 ➔
          </button>
        </div>
        <div className="flex items-center space-x-3 text-xs font-bold">
          <span style={{ backgroundColor: '#FEF3C7', color: '#D97706', padding: '4px 10px', borderRadius: '20px', border: '1px solid #FCD34D' }}>
            점수: {score}
          </span>
          <span style={{ backgroundColor: '#E0E7FF', color: '#4F46E5', padding: '4px 10px', borderRadius: '20px', border: '1px solid #C7D2FE' }}>
            Stage {stage}/3
          </span>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedbackMsg && (
        <div
          className={`py-2 px-4 text-center text-xs font-bold transition-all z-20 ${
            feedbackMsg.isError
              ? 'bg-rose-600/90 text-white animate-bounce'
              : 'bg-emerald-600/90 text-white'
          }`}
        >
          {feedbackMsg.text}
        </div>
      )}

      {/* Stage 1 & 2 Question Header */}
      {stage === 1 && currentStage1Item && (
        <div className="p-3 bg-slate-800/50 border-b border-slate-700 text-center z-20">
          <span className="text-xs text-amber-400 font-semibold uppercase tracking-wider block mb-1">
            Stage 1: 수치 버블 맞추기 ({stage1Index + 1}/{stage1Items.length})
          </span>
          <h2 className="text-base font-bold text-white">{currentStage1Item.question}</h2>
        </div>
      )}

      {stage === 2 && (
        <div className="p-3 bg-slate-800/50 border-b border-slate-700 text-center z-20">
          <span className="text-xs text-indigo-400 font-semibold uppercase tracking-wider block mb-1">
            Stage 2: 가스 카드 - 수치 카드 짝맞추기
          </span>
          <p className="text-xs text-slate-300">
            가스 이름을 터치한 후 해당 정답 수치를 연속 터치하세요! ({stage2MatchedIds.length}/6 짝 완료)
          </p>
        </div>
      )}

      {/* Full-Height Dynamic DOM Physics Canvas Area for Stage 1 & 2 */}
      {(stage === 1 || stage === 2) && (
        <div
          ref={containerRef}
          className="flex-1 min-h-[460px] relative w-full h-full bg-slate-950 overflow-hidden"
        >
          {bubbles.map((b) => {
            const isSelected = selectedBubble?.id === b.id;
            const radius = b.size / 2;

            return (
              <div
                key={b.id}
                onClick={(e) => handleBubbleTap(b, e.clientX, e.clientY)}
                style={{
                  position: 'absolute',
                  left: `${b.x - radius}px`,
                  top: `${b.y - radius}px`,
                  width: `${b.size}px`,
                  height: `${b.size}px`,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(26, 32, 53, 0.95)',
                  border: isSelected ? '3.5px solid #F59E0B' : `3px solid ${b.color}`,
                  boxShadow: isSelected
                    ? '0 0 20px #F59E0B, 0 4px 15px rgba(0,0,0,0.6)'
                    : `0 0 14px ${b.color}66, 0 4px 15px rgba(0,0,0,0.5)`,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  transition: 'transform 0.15s ease-out, border-color 0.2s',
                  zIndex: 10,
                }}
              >
                <span
                  style={{
                    fontSize: '0.65rem',
                    fontWeight: 800,
                    color: b.color,
                    backgroundColor: `${b.color}22`,
                    padding: '2px 6px',
                    borderRadius: '8px',
                    marginBottom: '2px',
                  }}
                >
                  {b.type === 'name' ? '가스명' : '수치'}
                </span>

                <span
                  style={{
                    fontWeight: 900,
                    fontSize: b.text.length > 8 ? '0.75rem' : b.text.length > 5 ? '0.85rem' : '1.05rem',
                    color: '#ffffff',
                    textAlign: 'center',
                    lineHeight: 1.1,
                    padding: '0 4px',
                  }}
                >
                  {b.text}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Stage 3 Direct Input UI */}
      {stage === 3 && currentStage3Item && (
        <div className="flex-1 flex flex-col p-4 bg-slate-950 overflow-y-auto">
          <div className="text-center mb-4">
            <span className="text-xs text-rose-400 font-bold uppercase tracking-wider block mb-1">
              Stage 3: 수치 직접 입력 ({stage3Index + 1}/{stage3Items.length})
            </span>
            <h2 className="text-lg font-extrabold text-white mb-1">{currentStage3Item.name}</h2>
            <p className="text-xs text-rose-300/80">⚠️ 틀릴 경우 1 Stage로 다시 강등됩니다!</p>
          </div>

          {/* Input Box Card */}
          <div className="bg-slate-800/90 border border-slate-700 rounded-2xl p-4 mb-4 text-center">
            <p className="text-xs text-slate-400 mb-3">{currentStage3Item.fullDisplay}</p>

            {currentStage3Item.upperBound ? (
              <div className="flex items-center justify-center space-x-2 text-sm">
                <span className="text-slate-300 font-semibold">하한:</span>
                <button
                  onClick={() => setActiveInputTarget('lower')}
                  className={`px-3 py-2 rounded-lg font-mono text-base font-bold min-w-[70px] border transition ${
                    activeInputTarget === 'lower'
                      ? 'bg-amber-500/20 border-amber-400 text-amber-300 ring-2 ring-amber-400/50'
                      : 'bg-slate-900 border-slate-700 text-slate-200'
                  }`}
                >
                  {lowerInput || '_'}
                </button>
                <span className="text-slate-400 font-bold">~ 상한:</span>
                <button
                  onClick={() => setActiveInputTarget('upper')}
                  className={`px-3 py-2 rounded-lg font-mono text-base font-bold min-w-[70px] border transition ${
                    activeInputTarget === 'upper'
                      ? 'bg-amber-500/20 border-amber-400 text-amber-300 ring-2 ring-amber-400/50'
                      : 'bg-slate-900 border-slate-700 text-slate-200'
                  }`}
                >
                  {upperInput || '_'}
                </button>
                <span className="text-slate-300 font-semibold">{currentStage3Item.unit}</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2 text-sm">
                <span className="text-slate-300 font-semibold">기준 수치:</span>
                <button
                  onClick={() => setActiveInputTarget('lower')}
                  className={`px-4 py-2 rounded-lg font-mono text-base font-bold min-w-[100px] border transition ${
                    activeInputTarget === 'lower'
                      ? 'bg-amber-500/20 border-amber-400 text-amber-300 ring-2 ring-amber-400/50'
                      : 'bg-slate-900 border-slate-700 text-slate-200'
                  }`}
                >
                  {lowerInput || '_'}
                </button>
                <span className="text-slate-300 font-semibold">{currentStage3Item.unit}</span>
              </div>
            )}
          </div>

          {/* On-screen Keypad */}
          <div className="max-w-xs mx-auto w-full grid grid-cols-3 gap-2 mb-4">
            {['1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '0', 'DEL'].map((k) => (
              <button
                key={k}
                onClick={() => handleKeypadPress(k)}
                className="py-3 bg-slate-800 hover:bg-slate-700 active:bg-slate-600 rounded-xl text-base font-bold font-mono border border-slate-700/80 shadow-sm transition active:scale-95"
              >
                {k}
              </button>
            ))}
          </div>

          <div className="flex space-x-2 max-w-xs mx-auto w-full">
            <button
              onClick={() => handleKeypadPress('CLEAR')}
              className="flex-1 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl text-xs font-bold text-slate-200 transition active:scale-95"
            >
              지우기
            </button>
            <button
              onClick={handleStage3Submit}
              className="flex-[2] py-3 bg-emerald-600 hover:bg-emerald-500 rounded-xl text-sm font-bold text-white shadow-lg shadow-emerald-900/40 transition active:scale-95"
            >
              정답 확인 ✓
            </button>
          </div>
        </div>
      )}

      {/* Win Modal */}
      {showWinModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 text-center max-w-xs w-full shadow-2xl animate-scale-in">
            <div className="text-5xl mb-3">👑</div>
            <h2 className="text-xl font-extrabold text-white mb-2">핵심 수치 완전 마스터!</h2>
            <p className="text-xs text-slate-300 mb-4">
              3 Stage를 완벽하게 통과하셨습니다!<br />
              최종 점수: <span className="text-amber-400 font-bold">{score}점</span>
            </p>
            <button
              onClick={startNewGame}
              className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl shadow-lg transition active:scale-95 mb-2"
            >
              다시 게임하기
            </button>
            <button
              onClick={onBackToHome}
              className="w-full py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-semibold rounded-xl transition"
            >
              홈으로 돌아가기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
