import React, { useState, useEffect, useRef, useCallback } from 'react';
import confetti from 'canvas-confetti';
import { ArrowLeft, RefreshCw, Flame, Trophy, CheckCircle2 } from 'lucide-react';
import { BubbleCanvas } from './BubbleCanvas';
import type { Stage, GasItem, MatchedSet, ScorePopup } from '../types/game';
import { generateGameRoundGases } from '../data/gasData';

type Props = {
  onGoHome: () => void;
};

export const GameScreen: React.FC<Props> = ({ onGoHome }) => {
  const [stage, setStage] = useState<Stage>(1);
  const [roundTotalCount, setRoundTotalCount] = useState(10);
  const [activeGases, setActiveGases] = useState<GasItem[]>([]);
  const [targetGas, setTargetGas] = useState<GasItem | null>(null);
  const [matchedSets, setMatchedSets] = useState<MatchedSet[]>([]);
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [shakeTarget, setShakeTarget] = useState<string | null>(null);
  const [hint, setHint] = useState('1단계: 가스 한글 이름을 선택하세요');
  const [popups, setPopups] = useState<ScorePopup[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);

  const stepStartTimeRef = useRef(Date.now());

  // Initialize game round with 7 fixed gases + 3 random gases
  useEffect(() => {
    const roundGases = generateGameRoundGases();
    setActiveGases(roundGases);
    setRoundTotalCount(roundGases.length);
  }, []);

  // Haptic feedback helper
  const triggerHaptic = (type: 'select' | 'success' | 'error') => {
    if (typeof window !== 'undefined' && 'vibrate' in navigator) {
      if (type === 'select') navigator.vibrate(20);
      else if (type === 'success') navigator.vibrate([30, 40, 50]);
      else if (type === 'error') navigator.vibrate([80, 50, 80]);
    }
  };

  // Update dynamic hint message based on stage & targetGas
  useEffect(() => {
    if (stage === 1) {
      setHint('1단계: 가스 한글 이름을 선택하세요');
    } else if (stage === 2 && targetGas) {
      setHint(`✅ [${targetGas.korean}] 선택됨! 2단계: 올바른 화학식을 선택하세요`);
    } else if (stage === 3 && targetGas) {
      setHint(`✅ [${targetGas.korean} (${targetGas.formula})] 확인! 3단계: 올바른 용기 색상을 선택하세요`);
    }
  }, [stage, targetGas]);

  // Handle Bubble Tap per Stage
  const handleBubbleTap = useCallback(
    (gas: GasItem, tapX: number, tapY: number) => {
      // STAGE 1: Select Gas Name
      if (stage === 1) {
        triggerHaptic('select');
        setTargetGas(gas);
        setStage(2);
        stepStartTimeRef.current = Date.now();
        return;
      }

      // STAGE 2: Select Chemical Formula
      if (stage === 2) {
        if (!targetGas) return;

        if (gas.id === targetGas.id) {
          // Correct Formula!
          triggerHaptic('select');
          setStage(3);
        } else {
          // Wrong Formula!
          triggerHaptic('error');
          setShakeTarget(gas.id);
          setHint(`❌ 틀렸습니다! (${targetGas.korean} ≠ ${gas.formula}) 다시 이름을 선택하세요`);
          setTimeout(() => {
            setShakeTarget(null);
            setTargetGas(null);
            setStage(1);
            setCombo(0);
          }, 600);
        }
        return;
      }

      // STAGE 3: Select Container Color
      if (stage === 3) {
        if (!targetGas) return;

        // Compare colorName (e.g. Any '백색' matches '백색', any '회색' matches '회색')
        if (gas.colorName === targetGas.colorName) {
          // 💥 3-Stage Full Match Successful!
          triggerHaptic('success');

          // Trigger Confetti Particle Burst
          confetti({
            particleCount: 55,
            spread: 70,
            origin: { x: tapX / window.innerWidth, y: tapY / window.innerHeight },
          });

          // Calculate Speed & Combo Score
          const elapsed = (Date.now() - stepStartTimeRef.current) / 1000;
          const speedBonus = elapsed <= 5 ? 50 : 0;
          const comboMultiplier = combo >= 3 ? 2.5 : combo >= 2 ? 2.0 : combo >= 1 ? 1.5 : 1.0;
          const earned = Math.floor((100 + speedBonus) * comboMultiplier);

          const newMatched: MatchedSet = {
            gasId: targetGas.id,
            korean: targetGas.korean,
            formula: targetGas.formula,
            colorName: targetGas.colorName,
            colorHex: targetGas.colorHex,
          };

          setScore((s) => s + earned);
          setCombo((c) => c + 1);
          setMatchedSets((prev) => [...prev, newMatched]);

          // Floating Score Popup
          const newPopup: ScorePopup = { id: Date.now(), amount: earned, x: tapX, y: tapY };
          setPopups((prev) => [...prev, newPopup]);
          setTimeout(() => {
            setPopups((prev) => prev.filter((p) => p.id !== newPopup.id));
          }, 1000);

          // Remove matched gas from active list
          const nextActive = activeGases.filter((g) => g.id !== targetGas.id);
          setActiveGases(nextActive);

          setTargetGas(null);
          setStage(1);

          // Check if round complete
          if (nextActive.length === 0) {
            setTimeout(() => {
              setIsCompleted(true);
              confetti({ particleCount: 150, spread: 100, origin: { y: 0.6 } });
            }, 600);
          }
        } else {
          // Wrong Color!
          triggerHaptic('error');
          setShakeTarget(gas.id);
          setHint(`❌ 틀렸습니다! (${targetGas.korean} ≠ ${gas.colorName}) 다시 이름을 선택하세요`);
          setTimeout(() => {
            setShakeTarget(null);
            setTargetGas(null);
            setStage(1);
            setCombo(0);
          }, 600);
        }
      }
    },
    [stage, targetGas, activeGases, combo]
  );

  const resetGame = () => {
    const roundGases = generateGameRoundGases();
    setStage(1);
    setActiveGases(roundGases);
    setRoundTotalCount(roundGases.length);
    setTargetGas(null);
    setMatchedSets([]);
    setScore(0);
    setCombo(0);
    setIsCompleted(false);
    stepStartTimeRef.current = Date.now();
  };

  return (
    <div style={{
      width: '100%',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#F8FAFC',
      position: 'relative',
      overflowY: 'auto',
    }}>
      {/* Floating score popups */}
      {popups.map((p) => (
        <div
          key={p.id}
          className="floating-score"
          style={{ left: `${p.x - 30}px`, top: `${p.y - 40}px` }}
        >
          +{p.amount}
        </div>
      ))}

      {/* Header bar */}
      <div style={{
        padding: 'max(12px, env(safe-area-inset-top)) 16px 12px 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        zIndex: 100,
        boxShadow: '0 2px 10px rgba(0,0,0,0.03)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onGoHome}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748B',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.85rem',
              fontWeight: 800,
              cursor: 'pointer',
            }}
          >
            <ArrowLeft size={18} /> 이전으로
          </button>
          <button
            onClick={() => {
              window.location.href = '/game-menu.html';
            }}
            style={{
              backgroundColor: '#0284C7',
              color: '#FFFFFF',
              border: 'none',
              padding: '6px 14px',
              borderRadius: '10px',
              fontSize: '0.82rem',
              fontWeight: 800,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              boxShadow: '0 3px 10px rgba(2, 132, 199, 0.25)',
            }}
          >
            🧠 치매 예방 센터 ➔
          </button>
        </div>

        {/* Score & Progress */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#90a4ae', textTransform: 'uppercase', fontWeight: 800 }}>SCORE</span>
            <div style={{ color: '#ffffff', fontSize: '1.25rem', fontWeight: 900, fontFamily: 'Outfit' }}>
              {score.toLocaleString()}
            </div>
          </div>

          <div style={{ textAlign: 'center' }}>
            <span style={{ fontSize: '0.65rem', color: '#90a4ae', textTransform: 'uppercase', fontWeight: 800 }}>진행률</span>
            <div style={{ color: '#69f0ae', fontSize: '1.1rem', fontWeight: 900 }}>
              {matchedSets.length}/{roundTotalCount}
            </div>
          </div>

          {/* Combo badge */}
          {combo >= 2 && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: 'rgba(255, 215, 0, 0.15)',
              border: '1px solid #ffd700',
              padding: '4px 8px',
              borderRadius: '12px',
              color: '#ffd700',
              fontWeight: 800,
              fontSize: '0.8rem',
            }}>
              <Flame size={14} color="#ffd700" /> {combo} COMBO!
            </div>
          )}
        </div>

        <button
          onClick={resetGame}
          style={{
            background: 'none',
            border: 'none',
            color: '#90a4ae',
            cursor: 'pointer',
            padding: '4px',
          }}
        >
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Matched Gas sidebar badge tags (Rendered behind bubbles) */}
      {matchedSets.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '70px',
          right: '12px',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          zIndex: 2,
          opacity: 0.8,
          pointerEvents: 'none',
        }}>
          {matchedSets.map((m) => (
            <div
              key={m.gasId}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                backgroundColor: 'rgba(26, 32, 53, 0.9)',
                border: '1px solid #69f0ae',
                borderRadius: '12px',
                padding: '4px 10px',
                fontSize: '0.75rem',
                color: '#69f0ae',
                fontWeight: 700,
                backdropFilter: 'blur(8px)',
              }}
            >
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: m.colorHex }} />
              {m.korean} ({m.formula}) - {m.colorName}
            </div>
          ))}
        </div>
      )}

      {/* Main Physics Stage Bubble Canvas */}
      <div style={{ flex: 1, position: 'relative', zIndex: 10 }}>
        <BubbleCanvas
          stage={stage}
          activeGases={activeGases}
          shakeTarget={shakeTarget}
          onBubbleTap={handleBubbleTap}
        />
      </div>

      {/* Bottom Hint & Stage Navigation Banner */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: 'rgba(26, 32, 53, 0.95)',
        borderTop: '1px solid rgba(255, 255, 255, 0.08)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '8px',
        zIndex: 100,
        paddingBottom: 'max(16px, env(safe-area-inset-bottom))',
      }}>
        <div style={{ color: '#b0bec5', fontSize: '0.88rem', fontWeight: 600, textAlign: 'center' }}>
          {hint}
        </div>

        {/* 3-Stage Step Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
          <span style={{
            padding: '4px 12px',
            borderRadius: '14px',
            backgroundColor: stage === 1 ? 'rgba(79, 195, 247, 0.25)' : 'rgba(255,255,255,0.05)',
            color: stage === 1 ? '#4fc3f7' : '#90a4ae',
            border: stage === 1 ? '1.5px solid #4fc3f7' : '1px solid transparent',
            fontWeight: 800,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            {stage > 1 ? <CheckCircle2 size={13} color="#69f0ae" /> : null} 1. 이름
          </span>
          <span style={{ color: '#90a4ae' }}>→</span>
          <span style={{
            padding: '4px 12px',
            borderRadius: '14px',
            backgroundColor: stage === 2 ? 'rgba(105, 240, 174, 0.25)' : 'rgba(255,255,255,0.05)',
            color: stage === 2 ? '#69f0ae' : '#90a4ae',
            border: stage === 2 ? '1.5px solid #69f0ae' : '1px solid transparent',
            fontWeight: 800,
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}>
            {stage > 2 ? <CheckCircle2 size={13} color="#69f0ae" /> : null} 2. 화학식
          </span>
          <span style={{ color: '#90a4ae' }}>→</span>
          <span style={{
            padding: '4px 12px',
            borderRadius: '14px',
            backgroundColor: stage === 3 ? 'rgba(255, 241, 118, 0.25)' : 'rgba(255,255,255,0.05)',
            color: stage === 3 ? '#fff176' : '#90a4ae',
            border: stage === 3 ? '1.5px solid #fff176' : '1px solid transparent',
            fontWeight: 800,
          }}>
            3. 용기색상 💥
          </span>
        </div>
      </div>

      {/* Level Complete Modal Overlay */}
      {isCompleted && (
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(13, 17, 23, 0.95)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '30px',
          zIndex: 200,
          backdropFilter: 'blur(10px)',
        }}>
          <div className="glass-panel" style={{
            padding: '36px 24px',
            width: '100%',
            maxWidth: '340px',
            textAlign: 'center',
            borderColor: '#69f0ae',
            boxShadow: '0 0 30px rgba(105, 240, 174, 0.3)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '16px',
          }}>
            <Trophy size={60} color="#ffd700" />
            <h2 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#ffffff' }}>완전 정복! 🎉</h2>
            <p style={{ color: '#90a4ae', fontSize: '0.9rem' }}>기본 7종 + 무작위 가스 전체 매칭 성공</p>

            <div style={{
              fontSize: '2.5rem',
              fontWeight: 900,
              color: '#69f0ae',
              fontFamily: 'Outfit',
              margin: '10px 0',
            }}>
              {score.toLocaleString()} <span style={{ fontSize: '1rem', color: '#90a4ae' }}>점</span>
            </div>

            <div style={{ display: 'flex', gap: '12px', width: '100%' }}>
              <button
                onClick={resetGame}
                style={{
                  flex: 1,
                  padding: '14px',
                  borderRadius: '24px',
                  border: 'none',
                  backgroundColor: '#4fc3f7',
                  color: '#0d1117',
                  fontWeight: 900,
                  fontSize: '1rem',
                  cursor: 'pointer',
                }}
              >
                다시 도전 🔄
              </button>
              <button
                onClick={onGoHome}
                style={{
                  flex: 1,
                  padding: '14px',
                  borderRadius: '24px',
                  border: '1px solid rgba(255,255,255,0.2)',
                  backgroundColor: 'rgba(255,255,255,0.05)',
                  color: '#ffffff',
                  fontWeight: 800,
                  fontSize: '1rem',
                  cursor: 'pointer',
                }}
              >
                홈으로 🏠
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
