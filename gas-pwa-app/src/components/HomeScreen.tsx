import React, { useState } from 'react';
import { ALL_GAS_DATA } from '../data/gasData';
import { KEY_NUMBERS_DATA } from '../data/numberData';
import { FIRE_FACILITY_CATEGORIES, FIRE_EQUIPMENT_ITEMS } from '../data/fireFacilityData';
import { Play, Share, PlusSquare, Sparkles, ChevronRight, Info } from 'lucide-react';
import { Navbar } from './Navbar';

type Props = {
  onStartColorGame: () => void;
  onStartNumberGame: () => void;
  onStartFacilityGame: () => void;
};

export const HomeScreen: React.FC<Props> = ({
  onStartColorGame,
  onStartNumberGame,
  onStartFacilityGame,
}) => {
  const [mainCategory, setMainCategory] = useState<'fire' | 'gas'>('fire');
  const [activeTab, setActiveTab] = useState<'color' | 'number' | 'facility'>('facility');
  const [showPwaGuide, setShowPwaGuide] = useState(true);

  return (
    <div
      style={{
        width: '100%',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: '#F8FAFC',
      }}
    >
      <Navbar />

      <div
        style={{
          width: '100%',
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '16px max(14px, env(safe-area-inset-right)) max(20px, env(safe-area-inset-bottom)) max(14px, env(safe-area-inset-left))',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >

      {/* Top Ocean Blue Header Hero Banner - 치매 예방 센터 스타일 */}
      <div
        style={{
          background: 'linear-gradient(135deg, #0284C7 0%, #0F172A 100%)',
          borderRadius: '20px',
          padding: '24px 20px',
          color: '#FFFFFF',
          boxShadow: '0 8px 25px rgba(2, 132, 199, 0.2)',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 14px',
            borderRadius: '20px',
            backgroundColor: 'rgba(255, 255, 255, 0.18)',
            color: '#E0F2FE',
            fontSize: '0.8rem',
            fontWeight: 800,
            marginBottom: '10px',
            backdropFilter: 'blur(4px)',
          }}
        >
          <Sparkles size={14} /> 🧠 소방안전관리자 & 가스기능사 암기왕
        </div>
        <h1
          style={{
            fontSize: '1.7rem',
            fontWeight: 900,
            letterSpacing: '-0.5px',
            color: '#FFFFFF',
            lineHeight: 1.3,
          }}
        >
          {activeTab === 'facility'
            ? '🚒 소방시설 5대 분류 매칭'
            : activeTab === 'color'
            ? '⚗️ 용기 색상 암기왕'
            : '🔢 핵심 수치 암기왕'}
        </h1>
        <p style={{ color: '#BAE6FD', fontSize: '0.85rem', marginTop: '6px', lineHeight: 1.4 }}>
          {activeTab === 'facility'
            ? '고정된 5대 소방시설 종류 ➔ 주요 구성 설비 22종 매칭 게임'
            : activeTab === 'color'
            ? '한글 이름 ➔ 원소기호 ➔ 용기 색상 3단계 게임'
            : '버블 맞추기 ➔ 짝맞추기 ➔ 직접 입력 3단계'}
        </p>
      </div>

      {/* 1차 자격증/분야 메인 카테고리 탭 (소방안전기사 / 가스기능사) */}
      <div
        style={{
          display: 'flex',
          backgroundColor: '#FFFFFF',
          borderRadius: '18px',
          padding: '6px',
          border: '2px solid #CBD5E1',
          gap: '6px',
          boxShadow: '0 4px 15px rgba(15, 23, 42, 0.05)',
        }}
      >
        <button
          onClick={() => {
            setMainCategory('fire');
            setActiveTab('facility');
          }}
          style={{
            flex: 1,
            padding: '14px 8px',
            borderRadius: '14px',
            border: 'none',
            backgroundColor: mainCategory === 'fire' ? '#BE185D' : '#F1F5F9',
            color: mainCategory === 'fire' ? '#FFFFFF' : '#475569',
            fontWeight: 900,
            fontSize: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: mainCategory === 'fire' ? '0 4px 14px rgba(190, 24, 93, 0.35)' : 'none',
          }}
        >
          🚒 1. 소방안전기사 (소방안전관리자)
        </button>

        <button
          onClick={() => {
            setMainCategory('gas');
            setActiveTab('color');
          }}
          style={{
            flex: 1,
            padding: '14px 8px',
            borderRadius: '14px',
            border: 'none',
            backgroundColor: mainCategory === 'gas' ? '#0284C7' : '#F1F5F9',
            color: mainCategory === 'gas' ? '#FFFFFF' : '#475569',
            fontWeight: 900,
            fontSize: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s',
            boxShadow: mainCategory === 'gas' ? '0 4px 14px rgba(2, 132, 199, 0.35)' : 'none',
          }}
        >
          ⚗️ 2. 가스기능사
        </button>
      </div>

      {/* 2차 세부 암기/게임 메뉴 탭 */}
      <div
        style={{
          display: 'flex',
          backgroundColor: '#FFFFFF',
          borderRadius: '18px',
          padding: '5px',
          border: '1px solid #E2E8F0',
          gap: '4px',
          boxShadow: '0 4px 15px rgba(15, 23, 42, 0.04)',
        }}
      >
        {mainCategory === 'fire' ? (
          <>
            <button
              onClick={() => setActiveTab('facility')}
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: activeTab === 'facility' ? '#EC4899' : 'transparent',
                color: activeTab === 'facility' ? '#FFFFFF' : '#64748B',
                fontWeight: 800,
                fontSize: '0.88rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: activeTab === 'facility' ? '0 4px 12px rgba(236, 72, 153, 0.3)' : 'none',
              }}
            >
              🚒 소방시설 5대 분류
            </button>
            <button
              disabled
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: 'transparent',
                color: '#94A3B8',
                fontWeight: 700,
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'not-allowed',
                opacity: 0.65,
              }}
            >
              📕 화재안전기준 (추후 추가)
            </button>
            <button
              disabled
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: 'transparent',
                color: '#94A3B8',
                fontWeight: 700,
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'not-allowed',
                opacity: 0.65,
              }}
            >
              📘 소방관계법규 (추후 추가)
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => setActiveTab('color')}
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: activeTab === 'color' ? '#0284C7' : 'transparent',
                color: activeTab === 'color' ? '#FFFFFF' : '#64748B',
                fontWeight: 800,
                fontSize: '0.88rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: activeTab === 'color' ? '0 4px 12px rgba(2, 132, 199, 0.3)' : 'none',
              }}
            >
              🎨 용기 색상
            </button>
            <button
              onClick={() => setActiveTab('number')}
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: activeTab === 'number' ? '#D97706' : 'transparent',
                color: activeTab === 'number' ? '#FFFFFF' : '#64748B',
                fontWeight: 800,
                fontSize: '0.88rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: activeTab === 'number' ? '0 4px 12px rgba(217, 119, 6, 0.3)' : 'none',
              }}
            >
              🔢 핵심 수치
            </button>
            <button
              disabled
              style={{
                flex: 1,
                padding: '12px 4px',
                borderRadius: '14px',
                border: 'none',
                backgroundColor: 'transparent',
                color: '#94A3B8',
                fontWeight: 700,
                fontSize: '0.85rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                cursor: 'not-allowed',
                opacity: 0.65,
              }}
            >
              📗 가스안전관리 (추후 추가)
            </button>
          </>
        )}
      </div>

      {/* PWA Home Screen Guide Banner */}
      {showPwaGuide && (
        <div
          className="glass-panel"
          style={{
            padding: '12px 16px',
            borderColor: '#FBCFE8',
            backgroundColor: '#FDF2F8',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#BE185D', fontWeight: 800, fontSize: '0.85rem' }}>
              <Info size={16} /> 아이폰/갤럭시 홈 화면 앱 설치
            </div>
            <button
              onClick={() => setShowPwaGuide(false)}
              style={{ background: 'none', border: 'none', color: '#9D174D', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 700 }}
            >
              닫기 ✕
            </button>
          </div>
          <p style={{ color: '#831843', fontSize: '0.8rem', lineHeight: 1.4, marginBottom: '8px' }}>
            Safari <span style={{ color: '#0284C7', fontWeight: 800 }}>[공유 📤]</span> 후 <span style={{ color: '#059669', fontWeight: 800 }}>[홈 화면에 추가 ➕]</span>를 누르면 바탕화면에 설치됩니다!
          </p>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-around',
              backgroundColor: '#FFFFFF',
              borderRadius: '10px',
              padding: '6px 10px',
              fontSize: '0.75rem',
              color: '#475569',
              border: '1px solid #FBCFE8',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700 }}><Share size={13} color="#0284C7" /> 1. 공유</span>
            <ChevronRight size={13} color="#94A3B8" />
            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 700 }}><PlusSquare size={13} color="#059669" /> 2. 홈 화면 추가</span>
          </div>
        </div>
      )}

      {/* Start Game Action Button */}
      {activeTab === 'facility' ? (
        <button
          onClick={onStartFacilityGame}
          style={{
            width: '100%',
            padding: '16px',
            borderRadius: '18px',
            border: 'none',
            background: 'linear-gradient(135deg, #EC4899 0%, #BE185D 100%)',
            color: '#FFFFFF',
            fontSize: '1.15rem',
            fontWeight: 900,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: 'pointer',
            boxShadow: '0 6px 20px rgba(236, 72, 153, 0.35)',
            transition: 'transform 0.2s',
          }}
        >
          <Play fill="#FFFFFF" size={22} /> 소방시설 매칭 게임 시작
        </button>
      ) : activeTab === 'color' ? (
        <button
          onClick={onStartColorGame}
          style={{
            width: '100%',
            padding: '16px',
            borderRadius: '18px',
            border: 'none',
            background: 'linear-gradient(135deg, #0284C7 0%, #0D9488 100%)',
            color: '#FFFFFF',
            fontSize: '1.15rem',
            fontWeight: 900,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: 'pointer',
            boxShadow: '0 6px 20px rgba(2, 132, 199, 0.35)',
            transition: 'transform 0.2s',
          }}
        >
          <Play fill="#FFFFFF" size={22} /> 용기 색상 게임 시작
        </button>
      ) : (
        <button
          onClick={onStartNumberGame}
          style={{
            width: '100%',
            padding: '16px',
            borderRadius: '18px',
            border: 'none',
            background: 'linear-gradient(135deg, #D97706 0%, #B45309 100%)',
            color: '#FFFFFF',
            fontSize: '1.15rem',
            fontWeight: 900,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            cursor: 'pointer',
            boxShadow: '0 6px 20px rgba(217, 119, 6, 0.35)',
            transition: 'transform 0.2s',
          }}
        >
          <Play fill="#FFFFFF" size={22} /> 핵심 수치 게임 시작
        </button>
      )}

      {/* Mode Specific Reference Tables - 치매 예방 센터 라이트 스타일 */}
      {activeTab === 'facility' ? (
        <>
          <div className="glass-panel" style={{ padding: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '8px', color: '#BE185D' }}>
              🎮 소방시설 매칭 게임 플레이 방법
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.83rem', color: '#334155', lineHeight: 1.5 }}>
              <div>• <strong>고정 리스트:</strong> 5대 소방시설 종류 (소화 / 경보 / 피난구조 / 소화용수 / 소화활동설비) 패널이 고정되어 제공됩니다.</div>
              <div>• <strong>클릭 선택 매칭:</strong> 소방시설 종류 ➔ 주요 구성 설비를 터치하거나, 설비 ➔ 종류를 터치하여 짝을 맞춥니다.</div>
              <div>• <strong>실시간 피드백:</strong> 올바른 매칭 시 콤보 점수와 이펙트 발생, 틀릴 경우 정답 힌트 제공!</div>
            </div>
          </div>

          {/* Reference Table */}
          <div className="glass-panel" style={{ padding: '16px', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '12px', color: '#0F172A' }}>
              📋 1. 소방시설의 5대 분류 개요 (총 22종)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {FIRE_FACILITY_CATEGORIES.map((cat) => {
                const items = FIRE_EQUIPMENT_ITEMS.filter((e) => e.categoryId === cat.id);
                return (
                  <div
                    key={cat.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      backgroundColor: '#F8FAFC',
                      padding: '12px 14px',
                      borderRadius: '12px',
                      border: `1px solid #E2E8F0`,
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontWeight: 900, fontSize: '0.9rem', color: '#0F172A' }}>
                        {cat.icon} {cat.name}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#0284C7', fontWeight: 800, backgroundColor: '#E0F2FE', padding: '2px 8px', borderRadius: '10px' }}>
                        {items.length}개 설비
                      </span>
                    </div>
                    <div style={{ fontSize: '0.82rem', color: '#334155', lineHeight: 1.4, fontWeight: 600 }}>
                      {items.map((i) => i.name).join(', ')}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      ) : activeTab === 'color' ? (
        <>
          <div className="glass-panel" style={{ padding: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '10px', color: '#0284C7' }}>
              🎮 용기 색상 3-Stage 진행 방식
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.83rem', color: '#334155' }}>
              <div><strong style={{ color: '#0284C7' }}>Stage 1 (한글명)</strong>: 가스 이름 터치 ➔ <strong style={{ color: '#059669' }}>Stage 2 (화학식)</strong>: 원소기호 터치 ➔ <strong style={{ color: '#D97706' }}>Stage 3 (색상)</strong>: 용기 색상 터치!</div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '16px', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '12px', color: '#0F172A' }}>
              📋 가스 용기 색상 정답표 (총 10종)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {ALL_GAS_DATA.map((gas) => (
                <div
                  key={gas.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: '#F8FAFC',
                    padding: '10px 14px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                  }}
                >
                  <div
                    style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      backgroundColor: gas.colorHex,
                      border: `2px solid ${gas.borderHex}`,
                      marginRight: '12px',
                      boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
                    }}
                  />
                  <span style={{ flex: 1, fontWeight: 800, fontSize: '0.88rem', color: '#0F172A' }}>{gas.korean}</span>
                  <span style={{ color: '#059669', fontWeight: 800, width: '65px', textAlign: 'center', fontSize: '0.88rem' }}>{gas.formula}</span>
                  <span
                    style={{
                      color: '#0284C7',
                      fontWeight: 900,
                      width: '60px',
                      textAlign: 'right',
                      fontSize: '0.88rem',
                    }}
                  >
                    {gas.colorName}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="glass-panel" style={{ padding: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '10px', color: '#D97706' }}>
              🎮 핵심 수치 3-Stage 몰입 방식
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.83rem', color: '#334155' }}>
              <div><strong style={{ color: '#D97706' }}>Stage 1 (개념)</strong>: 질문 보고 정답 수치 버블 맞추기</div>
              <div><strong style={{ color: '#4F46E5' }}>Stage 2 (짝맞추기)</strong>: 가스 카드 - 수치 카드 6쌍 매칭하기</div>
              <div><strong style={{ color: '#E11D48' }}>Stage 3 (직접입력)</strong>: 수치 키패드 직접 입력</div>
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '16px', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '12px', color: '#0F172A' }}>
              📋 가스 필기 핵심 수치 정답표 (총 6종)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {KEY_NUMBERS_DATA.map((item) => (
                <div
                  key={item.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: '#F8FAFC',
                    padding: '12px 14px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                  }}
                >
                  <span style={{ fontWeight: 800, fontSize: '0.88rem', color: '#0284C7', width: '90px' }}>
                    {item.name}
                  </span>
                  <span style={{ flex: 1, color: '#0F172A', fontWeight: 800, textAlign: 'right', fontSize: '0.88rem' }}>
                    {item.fullDisplay}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
      </div>
    </div>
  );
};
