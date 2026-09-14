import React from 'react';

export const Navbar: React.FC = () => {
  return (
    <nav
      style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E2E8F0',
        padding: '12px 20px',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.04)',
      }}
    >
      <div
        style={{
          maxWidth: '1200px',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '10px',
        }}
      >
        {/* Top Row: Logo & User Profile */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <a
            href="/game-menu.html"
            style={{ display: 'flex', alignItems: 'center', gap: '14px', textDecoration: 'none' }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                background: 'linear-gradient(135deg, #0284C7, #0D9488)',
                borderRadius: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontSize: '24px',
                boxShadow: '0 6px 16px rgba(2, 132, 199, 0.3)',
              }}
            >
              🧠
            </div>
            <span style={{ fontSize: '1.25rem', fontWeight: 900, color: '#0F172A', letterSpacing: '-0.5px' }}>
              치매 예방 센터
            </span>
          </a>

          {/* User Profile Pill */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              backgroundColor: '#F1F5F9',
              padding: '6px 14px',
              borderRadius: '30px',
              border: '1px solid #CBD5E1',
            }}
          >
            <div
              style={{
                width: '28px',
                height: '28px',
                backgroundColor: '#0284C7',
                color: '#FFFFFF',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '14px',
              }}
            >
              👤
            </div>
            <span style={{ fontSize: '13px', fontWeight: 800, color: '#0F172A' }}>test@test.com</span>
            <a
              href="/settings.html"
              style={{
                fontSize: '12px',
                fontWeight: 700,
                color: '#475569',
                textDecoration: 'none',
                backgroundColor: '#E2E8F0',
                padding: '4px 10px',
                borderRadius: '8px',
              }}
            >
              ⚙️ 설정
            </a>
            <a
              href="/login_design.html"
              style={{
                fontSize: '12px',
                fontWeight: 700,
                color: '#475569',
                textDecoration: 'none',
                backgroundColor: '#E2E8F0',
                padding: '4px 10px',
                borderRadius: '8px',
              }}
            >
              로그아웃
            </a>
          </div>
        </div>

        {/* Bottom Row: Sub-menu Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', fontSize: '14px', fontWeight: 800, flexWrap: 'wrap' }}>
          <a href="/index.html#about" style={{ color: '#475569', textDecoration: 'none' }}>
            서비스 소개
          </a>
          <a href="/index.html#research" style={{ color: '#475569', textDecoration: 'none' }}>
            임상 연구 검증
          </a>
          <a href="/intro.html" style={{ color: '#475569', textDecoration: 'none' }}>
            게임 가이드
          </a>
          <a href="/game-menu.html" style={{ color: '#0284C7', textDecoration: 'none' }}>
            🎮 게임 센터 홈
          </a>
          <span style={{ color: '#EA580C', fontWeight: 900, backgroundColor: '#FFEDD5', padding: '4px 12px', borderRadius: '8px' }}>
            🚨 소방안전관리자 & 가스기능사 암기왕
          </span>
        </div>
      </div>
    </nav>
  );
};
