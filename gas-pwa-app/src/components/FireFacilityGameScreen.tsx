import React, { useState, useEffect, useMemo } from 'react';
import confetti from 'canvas-confetti';
import {
  FIRE_FACILITY_CATEGORIES,
  FIRE_EQUIPMENT_ITEMS,
  getShuffledEquipmentItems,
} from '../data/fireFacilityData';
import type {
  FireFacilityCategoryId,
  FireEquipmentItem,
  GameMode,
} from '../types/fireFacility';
import {
  ArrowLeft,
  RotateCcw,
  Trophy,
  Sparkles,
  Info,
  CheckCircle2,
  Flame,
  Check,
} from 'lucide-react';

interface Props {
  onBackToHome: () => void;
}

export const FireFacilityGameScreen: React.FC<Props> = ({ onBackToHome }) => {
  // Game Mode
  const [gameMode, setGameMode] = useState<GameMode>('full-match');

  // Full Match Game State
  const [equipmentList, setEquipmentList] = useState<FireEquipmentItem[]>([]);
  const [matchedIds, setMatchedIds] = useState<string[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<FireFacilityCategoryId | null>(null);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string | null>(null);

  // Score & Stats
  const [score, setScore] = useState(0);
  const [combo, setCombo] = useState(0);
  const [feedbackMsg, setFeedbackMsg] = useState<{ text: string; isError: boolean } | null>(null);
  const [isShaking, setIsShaking] = useState(false);
  const [showWinModal, setShowWinModal] = useState(false);
  const [showStudyModal, setShowStudyModal] = useState(false);

  // Filter for Equipment List
  const [filterCategory, setFilterCategory] = useState<string>('all');

  // Speed Quiz State
  const [speedIndex, setSpeedIndex] = useState(0);

  // Initialize Game
  useEffect(() => {
    startNewGame();
  }, [gameMode]);

  const startNewGame = () => {
    const shuffled = getShuffledEquipmentItems();
    setEquipmentList(shuffled);
    setMatchedIds([]);
    setSelectedCategoryId(null);
    setSelectedEquipmentId(null);
    setScore(0);
    setCombo(0);
    setFeedbackMsg(null);
    setShowWinModal(false);
    setSpeedIndex(0);
  };

  // Sound effects helper using Web Audio API
  const playSound = (type: 'correct' | 'wrong' | 'win') => {
    try {
      const ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === 'correct') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15); // A5
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
        osc.start();
        osc.stop(ctx.currentTime + 0.2);
      } else if (type === 'wrong') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, ctx.currentTime); // A3
        osc.frequency.setValueAtTime(164.81, ctx.currentTime + 0.1); // E3
        gain.gain.setValueAtTime(0.25, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.25);
        osc.start();
        osc.stop(ctx.currentTime + 0.25);
      } else if (type === 'win') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, ctx.currentTime);
        osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.1);
        osc.frequency.setValueAtTime(783.99, ctx.currentTime + 0.2);
        osc.frequency.setValueAtTime(1046.50, ctx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }
    } catch {
      // Audio context fallback
    }
  };

  // Evaluate matching when both selections are active
  const checkMatch = (catId: FireFacilityCategoryId, equipId: string) => {
    const equipItem = equipmentList.find((e) => e.id === equipId);
    if (!equipItem) return;

    if (equipItem.categoryId === catId) {
      // MATCH SUCCESS
      playSound('correct');
      const newMatched = [...matchedIds, equipId];
      setMatchedIds(newMatched);

      const comboBonus = combo * 50;
      const points = 100 + comboBonus;
      setScore((prev) => prev + points);
      setCombo((prev) => prev + 1);

      setFeedbackMsg({
        text: `✨ 정답! [${equipItem.name}] ➔ [${equipItem.categoryName}] 매칭 (+${points}점)`,
        isError: false,
      });

      confetti({
        particleCount: 25,
        spread: 50,
        origin: { y: 0.6 },
      });

      // Reset selections
      setSelectedCategoryId(null);
      setSelectedEquipmentId(null);

      // Check for Game Completion (all 22 items matched)
      if (newMatched.length === FIRE_EQUIPMENT_ITEMS.length) {
        playSound('win');
        setShowWinModal(true);
        confetti({
          particleCount: 100,
          spread: 80,
          origin: { y: 0.5 },
        });
      }
    } else {
      // MATCH MISMATCH
      playSound('wrong');
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 500);

      setCombo(0);
      setFeedbackMsg({
        text: `❌ 오답! [${equipItem.name}] 은/는 [${equipItem.categoryName}]에 속합니다!`,
        isError: true,
      });

      // Clear selections after short delay
      setTimeout(() => {
        setSelectedCategoryId(null);
        setSelectedEquipmentId(null);
      }, 400);
    }
  };

  // Click handler for Fixed Category Buttons
  const handleCategoryClick = (catId: FireFacilityCategoryId) => {
    if (gameMode === 'speed-quiz') {
      handleSpeedQuizChoice(catId);
      return;
    }

    if (selectedEquipmentId) {
      // Equipment was already selected, now category clicked -> evaluate match
      checkMatch(catId, selectedEquipmentId);
    } else {
      // Toggle category selection
      if (selectedCategoryId === catId) {
        setSelectedCategoryId(null);
      } else {
        setSelectedCategoryId(catId);
        setFeedbackMsg({ text: `🎯 [${FIRE_FACILITY_CATEGORIES.find(c => c.id === catId)?.name}] 선택됨. 우측 주요설비를 터치하세요!`, isError: false });
      }
    }
  };

  // Click handler for Equipment Items
  const handleEquipmentClick = (equip: FireEquipmentItem) => {
    if (matchedIds.includes(equip.id)) return;

    if (selectedCategoryId) {
      // Category was already selected, now equipment clicked -> evaluate match
      checkMatch(selectedCategoryId, equip.id);
    } else {
      // Toggle equipment selection
      if (selectedEquipmentId === equip.id) {
        setSelectedEquipmentId(null);
      } else {
        setSelectedEquipmentId(equip.id);
        setFeedbackMsg({ text: `🎯 [${equip.name}] 선택됨. 좌측 고정된 소방시설 종류를 터치하세요!`, isError: false });
      }
    }
  };

  // Speed Quiz Choice Handler
  const handleSpeedQuizChoice = (catId: FireFacilityCategoryId) => {
    const currentItem = equipmentList[speedIndex];
    if (!currentItem) return;

    if (currentItem.categoryId === catId) {
      playSound('correct');
      setScore((prev) => prev + 150 + combo * 30);
      setCombo((prev) => prev + 1);
      setMatchedIds((prev) => [...prev, currentItem.id]);
      setFeedbackMsg({ text: `⚡ 정답! [${currentItem.name}] ➔ [${currentItem.categoryName}]`, isError: false });
    } else {
      playSound('wrong');
      setCombo(0);
      setFeedbackMsg({ text: `❌ 오답! [${currentItem.name}] 은/는 [${currentItem.categoryName}]입니다!`, isError: true });
    }

    if (speedIndex + 1 < equipmentList.length) {
      setSpeedIndex((prev) => prev + 1);
    } else {
      playSound('win');
      setShowWinModal(true);
      confetti({ particleCount: 80, spread: 70 });
    }
  };

  // Category Completion Status
  const categoryProgress = useMemo(() => {
    const map: Record<FireFacilityCategoryId, { matched: number; total: number; isDone: boolean }> = {
      extinguishing: { matched: 0, total: 5, isDone: false },
      alarm: { matched: 0, total: 5, isDone: false },
      evacuation: { matched: 0, total: 4, isDone: false },
      'water-supply': { matched: 0, total: 2, isDone: false },
      'fire-fighting': { matched: 0, total: 6, isDone: false },
    };

    matchedIds.forEach((id) => {
      const item = FIRE_EQUIPMENT_ITEMS.find((e) => e.id === id);
      if (item) {
        map[item.categoryId].matched += 1;
      }
    });

    Object.keys(map).forEach((key) => {
      const catKey = key as FireFacilityCategoryId;
      if (map[catKey].matched >= map[catKey].total) {
        map[catKey].isDone = true;
      }
    });

    return map;
  }, [matchedIds]);

  // Filtered Equipment items
  const filteredEquipments = useMemo(() => {
    if (filterCategory === 'unmatched') {
      return equipmentList.filter((e) => !matchedIds.includes(e.id));
    }
    if (filterCategory !== 'all') {
      return equipmentList.filter((e) => e.categoryId === filterCategory);
    }
    return equipmentList;
  }, [equipmentList, matchedIds, filterCategory]);

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#F8FAFC',
        overflowY: 'auto',
        position: 'relative',
      }}
    >
      {/* Top Header Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 'max(12px, env(safe-area-inset-top)) 14px 10px 14px',
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          zIndex: 10,
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.03)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={onBackToHome}
            style={{
              background: 'none',
              border: 'none',
              color: '#64748B',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 800,
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

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              padding: '4px 10px',
              borderRadius: '20px',
              backgroundColor: 'rgba(236, 72, 153, 0.15)',
              border: '1px solid rgba(236, 72, 153, 0.3)',
              color: '#f472b6',
              fontWeight: 800,
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Trophy size={14} /> {score}점
          </div>
          {combo > 1 && (
            <div
              style={{
                padding: '4px 8px',
                borderRadius: '20px',
                backgroundColor: 'rgba(245, 158, 11, 0.2)',
                border: '1px solid #f59e0b',
                color: '#ffd700',
                fontWeight: 900,
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '2px',
              }}
            >
              <Flame size={12} fill="#ffd700" /> x{combo}
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <button
            onClick={() => setShowStudyModal(true)}
            style={{
              padding: '6px 10px',
              borderRadius: '12px',
              border: '1px solid rgba(79, 195, 247, 0.3)',
              backgroundColor: 'rgba(79, 195, 247, 0.1)',
              color: '#4fc3f7',
              fontSize: '0.78rem',
              fontWeight: 800,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Info size={14} /> 정답표
          </button>
          <button
            onClick={startNewGame}
            style={{
              padding: '6px',
              borderRadius: '10px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              backgroundColor: '#21262d',
              color: '#c9d1d9',
              cursor: 'pointer',
            }}
          >
            <RotateCcw size={16} />
          </button>
        </div>
      </div>

      {/* Mode Switcher & Feedback Bar */}
      <div
        style={{
          padding: '8px 14px',
          backgroundColor: '#F8FAFC',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
        }}
      >
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', backgroundColor: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '3px', flex: 1 }}>
            <button
              onClick={() => setGameMode('full-match')}
              style={{
                flex: 1,
                padding: '6px',
                borderRadius: '9px',
                border: 'none',
                backgroundColor: gameMode === 'full-match' ? '#0284C7' : 'transparent',
                color: gameMode === 'full-match' ? '#ffffff' : '#64748B',
                fontWeight: 800,
                fontSize: '0.78rem',
                cursor: 'pointer',
              }}
            >
              🧩 전체 짝맞추기 (22종)
            </button>
            <button
              onClick={() => setGameMode('speed-quiz')}
              style={{
                flex: 1,
                padding: '6px',
                borderRadius: '9px',
                border: 'none',
                backgroundColor: gameMode === 'speed-quiz' ? '#EC4899' : 'transparent',
                color: gameMode === 'speed-quiz' ? '#ffffff' : '#64748B',
                fontWeight: 800,
                fontSize: '0.78rem',
                cursor: 'pointer',
              }}
            >
              ⚡ 스피드 퀴즈
            </button>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 800, whiteSpace: 'nowrap' }}>
            매칭 완료 {matchedIds.length} / 22
          </div>
        </div>

        {/* Feedback Message Toast */}
        {feedbackMsg && (
          <div
            style={{
              padding: '6px 12px',
              borderRadius: '8px',
              backgroundColor: feedbackMsg.isError ? '#FEE2E2' : '#D1FAE5',
              border: `1px solid ${feedbackMsg.isError ? '#FCA5A5' : '#6EE7B7'}`,
              color: feedbackMsg.isError ? '#991B1B' : '#065F46',
              fontSize: '0.78rem',
              fontWeight: 800,
              textAlign: 'center',
              transition: 'all 0.2s',
            }}
          >
            {feedbackMsg.text}
          </div>
        )}
      </div>

      {/* Game Content Area (Split View: Fixed Left Categories Panel + Right Equipment Stage) */}
      <div
        className={isShaking ? 'shake-anim' : ''}
        style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'row',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {/* ======================================================== */}
        {/* LEFT PANEL: 5 Fixed Categories ("소방시설종류 리스트 고정") */}
        {/* ======================================================== */}
        <div
          style={{
            width: '38%',
            maxWidth: '220px',
            minWidth: '135px',
            backgroundColor: '#FFFFFF',
            borderRight: '1px solid #E2E8F0',
            display: 'flex',
            flexDirection: 'column',
            padding: '10px 8px',
            gap: '8px',
            overflowY: 'auto',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              fontWeight: 900,
              color: '#8b949e',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              paddingLeft: '4px',
              marginBottom: '2px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <Sparkles size={12} color="#ffd700" /> 소방시설 종류 (고정)
          </div>

          {FIRE_FACILITY_CATEGORIES.map((cat) => {
            const prog = categoryProgress[cat.id];
            const isSelected = selectedCategoryId === cat.id;

            return (
              <button
                key={cat.id}
                onClick={() => handleCategoryClick(cat.id)}
                className={isSelected ? 'selected-glow' : ''}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                  padding: '10px 10px',
                  borderRadius: '14px',
                  border: isSelected
                    ? '2px solid #ffd700'
                    : prog.isDone
                    ? `1.5px solid ${cat.borderHex}`
                    : `1px solid ${cat.borderHex}44`,
                  backgroundColor: isSelected
                    ? `${cat.color}35`
                    : prog.isDone
                    ? `${cat.color}20`
                    : cat.bgHex,
                  color: '#ffffff',
                  textAlign: 'left',
                  cursor: 'pointer',
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  boxShadow: isSelected ? `0 0 12px ${cat.color}88` : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', marginBottom: '4px' }}>
                  <span style={{ fontSize: '1rem' }}>{cat.icon}</span>
                  {prog.isDone ? (
                    <span
                      style={{
                        fontSize: '0.68rem',
                        fontWeight: 900,
                        backgroundColor: '#10b981',
                        color: '#0d1117',
                        padding: '1px 6px',
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '2px',
                      }}
                    >
                      <Check size={10} /> 완료
                    </span>
                  ) : (
                    <span
                      style={{
                        fontSize: '0.68rem',
                        fontWeight: 800,
                        backgroundColor: isSelected ? '#ffd700' : 'rgba(255,255,255,0.1)',
                        color: isSelected ? '#0d1117' : cat.badgeColor,
                        padding: '1px 6px',
                        borderRadius: '10px',
                      }}
                    >
                      {prog.matched}/{cat.totalCount}
                    </span>
                  )}
                </div>

                <div style={{ fontWeight: 900, fontSize: '0.88rem', color: isSelected ? '#ffd700' : '#ffffff' }}>
                  {cat.name}
                </div>

                {isSelected && (
                  <div style={{ fontSize: '0.65rem', color: '#ffd700', fontWeight: 800, marginTop: '2px' }}>
                    🎯 선택됨 (설비 터치)
                  </div>
                )}
              </button>
            );
          })}

          <div
            style={{
              marginTop: 'auto',
              padding: '8px',
              borderRadius: '10px',
              backgroundColor: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.05)',
              fontSize: '0.68rem',
              color: '#8b949e',
              lineHeight: 1.35,
            }}
          >
            💡 <strong>매칭 팁:</strong> 종류 선택 ➔ 우측 주요설비 터치 (또는 반대)
          </div>
        </div>

        {/* ======================================================== */}
        {/* RIGHT PANEL: Equipment Cards / Speed Stage               */}
        {/* ======================================================== */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#F8FAFC',
            padding: '10px',
            overflowY: 'auto',
            gap: '10px',
          }}
        >
          {gameMode === 'full-match' ? (
            <>
              {/* Category Filter Chips */}
              <div style={{ display: 'flex', gap: '4px', overflowX: 'auto', paddingBottom: '4px' }}>
                <button
                  onClick={() => setFilterCategory('all')}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    backgroundColor: filterCategory === 'all' ? '#0284C7' : '#FFFFFF',
                    color: filterCategory === 'all' ? '#ffffff' : '#64748B',
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                  }}
                >
                  전체 (22)
                </button>
                <button
                  onClick={() => setFilterCategory('unmatched')}
                  style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    backgroundColor: filterCategory === 'unmatched' ? '#D97706' : '#FFFFFF',
                    color: filterCategory === 'unmatched' ? '#ffffff' : '#64748B',
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                  }}
                >
                  미완료만 ({22 - matchedIds.length})
                </button>
              </div>

              {/* Equipment Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))',
                  gap: '8px',
                }}
              >
                {filteredEquipments.map((equip) => {
                  const isMatched = matchedIds.includes(equip.id);
                  const isSelected = selectedEquipmentId === equip.id;
                  const categoryObj = FIRE_FACILITY_CATEGORIES.find((c) => c.id === equip.categoryId);

                  return (
                    <button
                      key={equip.id}
                      onClick={() => handleEquipmentClick(equip)}
                      disabled={isMatched}
                      style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        padding: '10px 8px',
                        borderRadius: '12px',
                        border: isSelected
                          ? '2px solid #0284C7'
                          : isMatched
                          ? '1px solid #10B981'
                          : '1px solid #E2E8F0',
                        backgroundColor: isSelected
                          ? '#E0F2FE'
                          : isMatched
                          ? '#ECFDF5'
                          : '#FFFFFF',
                        color: isMatched ? '#059669' : '#0F172A',
                        textAlign: 'left',
                        cursor: isMatched ? 'default' : 'pointer',
                        minHeight: '75px',
                        position: 'relative',
                        transition: 'all 0.15s ease',
                        boxShadow: isSelected ? '0 0 12px rgba(2, 132, 199, 0.3)' : '0 2px 6px rgba(0,0,0,0.03)',
                        opacity: isMatched ? 0.85 : 1,
                      }}
                    >
                      <div style={{ fontSize: '0.85rem', fontWeight: 900, lineHeight: 1.25, color: isMatched ? '#059669' : '#0F172A' }}>
                        {equip.name}
                      </div>

                      <div style={{ marginTop: '6px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        {isMatched ? (
                          <span
                            style={{
                              fontSize: '0.65rem',
                              fontWeight: 800,
                              color: '#69f0ae',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '2px',
                            }}
                          >
                            <CheckCircle2 size={12} /> {equip.categoryName}
                          </span>
                        ) : (
                          <span style={{ fontSize: '0.65rem', color: '#8b949e' }}>
                            {isSelected ? '🎯 선택됨' : '터치하여 매칭'}
                          </span>
                        )}
                        {categoryObj && (
                          <span style={{ fontSize: '0.75rem', opacity: isMatched ? 0.5 : 0.9 }}>
                            {categoryObj.icon}
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </>
          ) : (
            /* Speed Quiz Stage */
            <div
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '16px',
                gap: '16px',
              }}
            >
              <div
                className="glass-panel"
                style={{
                  width: '100%',
                  maxWidth: '320px',
                  padding: '24px',
                  textAlign: 'center',
                  borderColor: '#ec4899',
                  boxShadow: '0 0 20px rgba(236, 72, 153, 0.2)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <div style={{ fontSize: '0.8rem', color: '#ec4899', fontWeight: 800 }}>
                  ⚡ 스피드 퀴즈 ({speedIndex + 1} / 22)
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#ffffff' }}>
                  {equipmentList[speedIndex]?.name}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#8b949e' }}>
                  {equipmentList[speedIndex]?.detail}
                </div>
                <div
                  style={{
                    fontSize: '0.75rem',
                    color: '#ffd700',
                    fontWeight: 800,
                    backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    padding: '4px 12px',
                    borderRadius: '12px',
                  }}
                >
                  👈 좌측 고정된 5대 소방시설 종류 중 하나를 선택하세요!
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ======================================================== */}
      {/* Victory Modal Celebration                                */}
      {/* ======================================================== */}
      {showWinModal && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px',
            zIndex: 100,
          }}
        >
          <div
            className="glass-panel"
            style={{
              width: '100%',
              maxWidth: '360px',
              padding: '24px',
              textAlign: 'center',
              borderColor: '#ffd700',
              boxShadow: '0 0 40px rgba(255, 215, 0, 0.4)',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
          >
            <div style={{ fontSize: '3rem' }}>🏆</div>
            <h2 style={{ fontSize: '1.6rem', fontWeight: 900, color: '#ffd700' }}>
              축하합니다! 매칭 완성!
            </h2>
            <p style={{ color: '#c9d1d9', fontSize: '0.9rem', lineHeight: 1.5 }}>
              소방시설 5대 분류(소화, 경보, 피난구조, 소화용수, 소화활동) 및 주요 구성 설비 22종을 모두 완벽하게 마스터하셨습니다!
            </p>
            <div
              style={{
                backgroundColor: 'rgba(255,255,255,0.05)',
                borderRadius: '12px',
                padding: '12px',
                display: 'flex',
                justifyContent: 'space-around',
              }}
            >
              <div>
                <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>최종 점수</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#4fc3f7' }}>{score}점</div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#8b949e' }}>매칭 수</div>
                <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#69f0ae' }}>22 / 22</div>
              </div>
            </div>
            <button
              onClick={startNewGame}
              style={{
                width: '100%',
                padding: '14px',
                borderRadius: '14px',
                border: 'none',
                background: 'linear-gradient(135deg, #ffd700 0%, #ff8f00 100%)',
                color: '#0d1117',
                fontWeight: 900,
                fontSize: '1rem',
                cursor: 'pointer',
                boxShadow: '0 4px 15px rgba(255, 215, 0, 0.4)',
              }}
            >
              🔄 다시 도전하기
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* Reference Study Table Modal (Image 1 Table Exact View)  */}
      {/* ======================================================== */}
      {showStudyModal && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            zIndex: 100,
          }}
        >
          <div
            className="glass-panel"
            style={{
              width: '100%',
              maxWidth: '480px',
              maxHeight: '90%',
              overflowY: 'auto',
              padding: '18px',
              borderColor: '#3b82f6',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 900, color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '6px' }}>
                📋 1. 소방시설의 5대 분류 개요 정답표
              </h3>
              <button
                onClick={() => setShowStudyModal(false)}
                style={{ background: 'none', border: 'none', color: '#8b949e', cursor: 'pointer', fontSize: '1rem' }}
              >
                ✕
              </button>
            </div>

            <div style={{ fontSize: '0.8rem', color: '#c9d1d9', lineHeight: 1.4 }}>
              자격시험에 매회 출제되는 핵심 소방시설 분류 기준입니다.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
              {FIRE_FACILITY_CATEGORIES.map((cat) => {
                const items = FIRE_EQUIPMENT_ITEMS.filter((e) => e.categoryId === cat.id);
                return (
                  <div
                    key={cat.id}
                    style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: '10px',
                      padding: '10px 12px',
                      border: `1px solid ${cat.borderHex}55`,
                    }}
                  >
                    <div style={{ fontWeight: 900, color: cat.badgeColor, fontSize: '0.88rem', marginBottom: '4px' }}>
                      {cat.icon} {cat.name} ({cat.totalCount}종)
                    </div>
                    <div style={{ color: '#e2e8f0', fontSize: '0.8rem', lineHeight: 1.4 }}>
                      {items.map((i) => i.name).join(', ')}
                    </div>
                  </div>
                );
              })}
            </div>

            <button
              onClick={() => setShowStudyModal(false)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                border: 'none',
                backgroundColor: '#21262d',
                color: '#ffffff',
                fontWeight: 800,
                cursor: 'pointer',
                marginTop: '8px',
              }}
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
