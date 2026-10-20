import streamlit as st
import streamlit.components.v1 as components

BUBBLE_GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background: #0f172a;
    color: #f8fafc;
    overflow: hidden;
    width: 100vw;
    height: 100vh;
  }
  #game-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100vh;
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    background: radial-gradient(circle at top, #1e293b 0%, #0f172a 100%);
  }
  /* 상단 대시보드 */
  #header {
    padding: 10px 14px;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    border-bottom: 1px solid #334155;
    z-index: 10;
  }
  .top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .stat-badge {
    background: #1e293b;
    border: 1px solid #475569;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
  }
  .stat-badge span { color: #38bdf8; }
  .score-badge span { color: #facc15; }
  .combo-badge span { color: #f43f5e; }

  /* 타겟 미션 카드 */
  #mission-card {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    border: 1.5px solid #6366f1;
    border-radius: 10px;
    padding: 8px 12px;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
  }
  #target-title {
    font-size: 16px;
    font-weight: 800;
    color: #a5b4fc;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  #target-mnemonic {
    font-size: 13px;
    color: #fef08a;
    margin-top: 3px;
    font-weight: 600;
  }

  /* 버블 떠다니는 플레이 필드 */
  #playfield {
    flex: 1;
    position: relative;
    overflow: hidden;
    touch-action: none;
  }

  /* 버블 스타일 */
  .bubble {
    position: absolute;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 8px;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    box-shadow: inset 0 -6px 12px rgba(0,0,0,0.3), 0 6px 16px rgba(0,0,0,0.35);
    transition: transform 0.1s ease;
    will-change: transform, top, left;
  }
  .bubble:active {
    transform: scale(0.92);
  }
  .bubble-inner {
    pointer-events: none;
    line-height: 1.25;
    word-break: keep-all;
    text-shadow: 0 1px 3px rgba(0,0,0,0.8);
  }

  /* 버블 컬러 테마 */
  .b-cyan { background: radial-gradient(circle at 35% 35%, #67e8f9, #0891b2 80%); color: #fff; border: 2px solid #a5f3fc; }
  .b-emerald { background: radial-gradient(circle at 35% 35%, #6ee7b7, #059669 80%); color: #fff; border: 2px solid #a7f3d0; }
  .b-amber { background: radial-gradient(circle at 35% 35%, #fde047, #d97706 80%); color: #1e293b; border: 2px solid #fef08a; }
  .b-purple { background: radial-gradient(circle at 35% 35%, #d8b4fe, #7e22ce 80%); color: #fff; border: 2px solid #e9d5ff; }
  .b-rose { background: radial-gradient(circle at 35% 35%, #fda4af, #e11d48 80%); color: #fff; border: 2px solid #fecdd3; }

  /* 팝 파티클 애니메이션 */
  @keyframes popEffect {
    0% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.4); opacity: 0.8; }
    100% { transform: scale(1.8); opacity: 0; }
  }
  .popping {
    animation: popEffect 0.25s forwards;
    pointer-events: none;
  }

  /* 오답 진동 */
  @keyframes shakeEffect {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-8px); }
    40%, 80% { transform: translateX(8px); }
  }
  .shaking {
    animation: shakeEffect 0.35s ease;
    border-color: #ef4444 !important;
  }

  /* 플로팅 피드백 텍스트 */
  .float-msg {
    position: absolute;
    font-size: 16px;
    font-weight: 800;
    pointer-events: none;
    animation: floatUp 0.8s ease forwards;
    z-index: 20;
    text-shadow: 0 2px 4px rgba(0,0,0,0.8);
  }
  @keyframes floatUp {
    0% { transform: translateY(0); opacity: 1; }
    100% { transform: translateY(-45px); opacity: 0; }
  }

  /* 하단 피드백 바 */
  #footer-bar {
    padding: 8px 12px;
    background: rgba(15, 23, 42, 0.95);
    border-top: 1px solid #334155;
    font-size: 13px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 44px;
  }
  #feedback-text {
    font-weight: 600;
    color: #cbd5e1;
    flex: 1;
  }
  .btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 12px;
    cursor: pointer;
    margin-left: 4px;
    transition: background 0.15s ease;
  }
  .btn:hover { background: #2563eb; }
  .btn-next { background: #10b981; }
  .btn-next:hover { background: #059669; }
  .btn-back { background: #475569; }
  .btn-back:hover { background: #334155; }

  /* 완료 오버레이 */
  #clear-overlay {
    display: none;
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(6px);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 50;
    padding: 20px;
    text-align: center;
  }
  #clear-overlay h2 { color: #facc15; font-size: 26px; margin-bottom: 10px; }
  #clear-overlay p { color: #e2e8f0; font-size: 15px; margin-bottom: 20px; line-height: 1.6; }
</style>
</head>
<body>

<div id="game-container">
  <!-- 상단 대시보드 -->
  <div id="header">
    <div class="top-row">
      <div class="stat-badge score-badge">점수: <span id="val-score">0</span></div>
      <div class="stat-badge combo-badge">연속: <span id="val-combo">0</span>🔥</div>
      <div class="stat-badge">남은 타겟: <span id="val-remain">0</span>개</div>
    </div>
    
    <div id="mission-card">
      <div id="target-title">
        <span id="target-category-name">특수인화물 (50 L)</span>
        <div style="display:flex; align-items:center; gap:4px;">
          <button class="btn btn-back" id="btn-prev" onclick="prevStage()" title="이전 품명으로 되돌아가기">◀ 이전 (Back)</button>
          <button class="btn btn-next" id="btn-skip" onclick="nextStage()" title="다음 품명으로 건너뛰기">다음 ▶</button>
        </div>
      </div>
      <div id="target-mnemonic">💡 암기: "특수하게 디·이·아·산 (특수 다이아 산다!)"</div>
    </div>
  </div>

  <!-- 플레이 필드 (버블 생성) -->
  <div id="playfield"></div>

  <!-- 하단 피드백 -->
  <div id="footer-bar">
    <div id="feedback-text">💡 화면에 떠오르는 물질 중 현재 품명에 해당하는 버블을 터뜨리세요!</div>
    <button class="btn" onclick="togglePause()" id="btn-pause">일시정지 ⏸</button>
  </div>

  <!-- 클리어 오버레이 -->
  <div id="clear-overlay">
    <h2>🎉 스테이지 퍼펙트 클리어!</h2>
    <p id="clear-msg">모든 타겟을 완벽하게 찾아냈습니다!</p>
    <div style="display:flex; gap:10px;">
      <button class="btn btn-back" style="font-size: 15px; padding: 10px 18px;" onclick="prevStage()">◀ 이전 품명</button>
      <button class="btn btn-next" style="font-size: 15px; padding: 10px 20px;" onclick="nextStage()">다음 품명 도전하기 ▶</button>
    </div>
  </div>
</div>

<script>
// 제4류 위험물 품명 데이터 & 암기법 매핑
const DATA = [
  {
    name: "특수인화물 (50 L)",
    mnemonic: "특수하게 디·이·아·산! (특수 다이아 산다!)",
    targets: ["디에틸에테르", "이황화탄소", "아세트알데히드", "산화프로필렌"]
  },
  {
    name: "제1석유류 비수용성 (200 L)",
    mnemonic: "1등 휘·벤·톨·콜! (휘파람 불며 벤츠 타고 톨게이트 콜!)",
    targets: ["휘발유", "벤젠", "톨루엔", "콜로디온"]
  },
  {
    name: "제1석유류 수용성 (400 L)",
    mnemonic: "아·피! (물에 빠져서 아이고 피난다!)",
    targets: ["아세톤", "피리딘"]
  },
  {
    name: "알코올류 (400 L)",
    mnemonic: "알·사(400)탕 먹고 메·에 취한다! (60wt% 이상)",
    targets: ["메틸알코올", "에틸알코올", "프로필알코올", "이소프로필알코올"]
  },
  {
    name: "제2석유류 비수용성 (1,000 L)",
    mnemonic: "등·경·테·송·크·클! (등경이가 테레비 보며 송편 먹다 크클 웃었다)",
    targets: ["등유", "경유", "테레핀유", "송근유", "크실렌", "클로로벤젠"]
  },
  {
    name: "제2석유류 수용성 (2,000 L)",
    mnemonic: "아·아(산)! (둘 다 뒤에 '산(Acid)'이 붙음)",
    targets: ["아세트산(초산)", "아크릴산"]
  },
  {
    name: "제3석유류 비수용성 (2,000 L)",
    mnemonic: "중·크·아·니! (3등은 중간 크기 아니냐?)",
    targets: ["중유", "크레오소트유", "아닐린", "니트로벤젠"]
  },
  {
    name: "제3석유류 수용성 (4,000 L)",
    mnemonic: "에·글! (3석유류 물에 빠지니 애글복걸)",
    targets: ["에틸렌글리콜", "글리세린"]
  },
  {
    name: "제4석유류 (6,000 L)",
    mnemonic: "사(4)기·실·기! (기계 부품 윤활유 계열)",
    targets: ["기계유", "실린더유", "기어유"]
  },
  {
    name: "동식물유류 건성유 (요오드가 130 이상)",
    mnemonic: "아·들은 마르면 건성!",
    targets: ["아마인유", "들기름"]
  },
  {
    name: "동식물유류 반건성유 (요오드가 100~130)",
    mnemonic: "참·콩은 절반만!",
    targets: ["참기름", "콩기름"]
  },
  {
    name: "동식물유류 불건성유 (요오드가 100 이하)",
    mnemonic: "올·피는 절대 안 마름!",
    targets: ["올리브유", "피마자유"]
  }
];

// 전체 물질 역방향 검색 사전 (오답 안내용)
const ALL_SUBSTANCES = {};
DATA.forEach(cat => {
  cat.targets.forEach(item => {
    ALL_SUBSTANCES[item] = {
      catName: cat.name,
      mnemonic: cat.mnemonic
    };
  });
});
const ALL_ITEMS_POOL = Object.keys(ALL_SUBSTANCES);

let stageIdx = 0;
let score = 0;
let combo = 0;
let isPaused = false;
let spawnedTargets = new Set();
let remainingTargets = [];
let activeBubbles = [];
let spawnTimer = null;
let animFrameId = null;

const playfield = document.getElementById("playfield");
const valScore = document.getElementById("val-score");
const valCombo = document.getElementById("val-combo");
const valRemain = document.getElementById("val-remain");
const targetCatName = document.getElementById("target-category-name");
const targetMnemonic = document.getElementById("target-mnemonic");
const feedbackText = document.getElementById("feedback-text");
const clearOverlay = document.getElementById("clear-overlay");
const clearMsg = document.getElementById("clear-msg");

const colors = ["b-cyan", "b-emerald", "b-amber", "b-purple", "b-rose"];

// 오디오 사운드 효과 (Web Audio API)
let audioCtx = null;
function playSound(isSuccess) {
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    if (isSuccess) {
      osc.type = "sine";
      osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); // C5
      osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15); // A5
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.2);
    } else {
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(180, audioCtx.currentTime);
      osc.frequency.linearRampToValueAtTime(110, audioCtx.currentTime + 0.2);
      gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.25);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.25);
    }
  } catch(e) {}
}

function initStage(idx) {
  stageIdx = idx % DATA.length;
  const cur = DATA[stageIdx];
  targetCatName.innerText = cur.name;
  targetMnemonic.innerText = "💡 암기: " + cur.mnemonic;
  remainingTargets = [...cur.targets];
  valRemain.innerText = remainingTargets.length;
  clearOverlay.style.display = "none";
  feedbackText.innerHTML = `👉 <strong>[${cur.name}]</strong>에 속하는 물질을 터뜨리세요!`;

  // 기존 버블 제거
  activeBubbles.forEach(b => b.el.remove());
  activeBubbles = [];

  if (!animFrameId) updateBubbles();
}

// 버블 생성 로직
function spawnBubble() {
  if (isPaused) return;
  const cur = DATA[stageIdx];
  const fieldWidth = playfield.clientWidth || 360;

  // 60% 확률로 타겟 물질 생성, 40%는 무작위 타 물질
  let itemName = "";
  let isTarget = false;
  if (remainingTargets.length > 0 && Math.random() < 0.6) {
    itemName = remainingTargets[Math.floor(Math.random() * remainingTargets.length)];
    isTarget = true;
  } else {
    // 풀에서 무작위 선택
    const randomPick = ALL_ITEMS_POOL[Math.floor(Math.random() * ALL_ITEMS_POOL.length)];
    itemName = randomPick;
    isTarget = cur.targets.includes(itemName);
  }

  const el = document.createElement("div");
  const colorClass = colors[Math.floor(Math.random() * colors.length)];
  const size = Math.floor(Math.random() * 16) + 76; // 76~92px

  el.className = `bubble ${colorClass}`;
  el.style.width = size + "px";
  el.style.height = size + "px";

  const maxLeft = fieldWidth - size - 10;
  const posX = Math.max(10, Math.floor(Math.random() * maxLeft));
  const posY = playfield.clientHeight + 10;

  el.style.left = posX + "px";
  el.style.top = posY + "px";
  el.innerHTML = `<div class="bubble-inner">${itemName}</div>`;

  // 터치/클릭 이벤트 바인딩
  const handlePop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    onBubbleClick(el, itemName, isTarget);
  };
  el.addEventListener("pointerdown", handlePop);

  playfield.appendChild(el);

  // 속도: 초당 60~110px 상승
  const speed = (Math.random() * 0.7 + 0.9);
  const wobbleSpeed = Math.random() * 0.04 + 0.02;
  const wobbleAmp = Math.random() * 20 + 10;

  activeBubbles.push({
    el,
    name: itemName,
    x: posX,
    y: posY,
    speed,
    wobbleSpeed,
    wobbleAmp,
    time: Math.random() * 100,
    size
  });
}

// 버블 클릭 핸들러
function onBubbleClick(el, name, isTarget) {
  if (el.classList.contains("popping")) return;

  const cur = DATA[stageIdx];
  const rect = el.getBoundingClientRect();
  const parentRect = playfield.getBoundingClientRect();
  const clickX = rect.left - parentRect.left + rect.width / 2;
  const clickY = rect.top - parentRect.top;

  if (isTarget) {
    // 정답!
    playSound(true);
    combo++;
    score += (100 + combo * 10);
    valScore.innerText = score;
    valCombo.innerText = combo;

    showFloatMsg(clickX, clickY, `+${100 + combo * 10}!`, "#4ade80");

    // 남은 타겟에서 제거
    const tIdx = remainingTargets.indexOf(name);
    if (tIdx > -1) {
      remainingTargets.splice(tIdx, 1);
      valRemain.innerText = remainingTargets.length;
    }

    feedbackText.innerHTML = `⭕ <strong style="color:#4ade80;">[${name}] 정답!</strong> (${cur.mnemonic})`;

    el.classList.add("popping");
    setTimeout(() => {
      removeBubbleObj(el);
    }, 200);

    // 모든 타겟 클리어 체크
    if (remainingTargets.length === 0) {
      setTimeout(() => {
        showStageClear();
      }, 350);
    }
  } else {
    // 오답!
    playSound(false);
    combo = 0;
    valCombo.innerText = combo;
    showFloatMsg(clickX, clickY, "❌ 오답!", "#f87171");

    el.classList.add("shaking");
    setTimeout(() => { el.classList.remove("shaking"); }, 400);

    const info = ALL_SUBSTANCES[name];
    if (info) {
      feedbackText.innerHTML = `❌ <strong>[${name}]</strong>은 <span style="color:#f87171;">'${info.catName}'</span>입니다! (${info.mnemonic})`;
    } else {
      feedbackText.innerHTML = `❌ <strong>[${name}]</strong>은 현재 품명이 아닙니다!`;
    }
  }
}

function showFloatMsg(x, y, text, color) {
  const msg = document.createElement("div");
  msg.className = "float-msg";
  msg.style.left = (x - 20) + "px";
  msg.style.top = y + "px";
  msg.style.color = color;
  msg.innerText = text;
  playfield.appendChild(msg);
  setTimeout(() => msg.remove(), 800);
}

function removeBubbleObj(el) {
  el.remove();
  activeBubbles = activeBubbles.filter(b => b.el !== el);
}

// 버블 위치 갱신 루프
function updateBubbles() {
  if (!isPaused) {
    for (let i = activeBubbles.length - 1; i >= 0; i--) {
      const b = activeBubbles[i];
      b.y -= b.speed;
      b.time += b.wobbleSpeed;
      const wobbleX = b.x + Math.sin(b.time) * b.wobbleAmp;

      b.el.style.top = b.y + "px";
      b.el.style.left = wobbleX + "px";

      // 화면 상단 벗어나면 제거
      if (b.y < -b.size) {
        removeBubbleObj(b.el);
      }
    }
  }
  animFrameId = requestAnimationFrame(updateBubbles);
}

function showStageClear() {
  const cur = DATA[stageIdx];
  clearMsg.innerHTML = `<strong>${cur.name}</strong>의 모든 위험물을 완벽하게 잡았습니다!<br><br><span style="color:#fef08a;">💡 ${cur.mnemonic}</span>`;
  clearOverlay.style.display = "flex";
}

function prevStage() {
  const newIdx = (stageIdx - 1 + DATA.length) % DATA.length;
  initStage(newIdx);
}

function nextStage() {
  initStage(stageIdx + 1);
}

function togglePause() {
  isPaused = !isPaused;
  const btn = document.getElementById("btn-pause");
  if (isPaused) {
    btn.innerText = "계속하기 ▶";
    feedbackText.innerText = "⏸ 게임이 일시정지되었습니다.";
  } else {
    btn.innerText = "일시정지 ⏸";
    feedbackText.innerText = "🎮 게임 재개!";
  }
}

// 0.8초마다 버블 스폰
setInterval(() => {
  if (!isPaused && activeBubbles.length < 9) {
    spawnBubble();
  }
}, 850);

// 초기 시작
window.onload = () => {
  initStage(0);
};
</script>
</body>
</html>
"""

def render_bubble_game():
    st.subheader("🎈 제4류 위험물 버블 팝(Catch) 아케이드")
    st.caption("아래에서 떠오르는 버블 중 현재 타겟 품명에 해당하는 위험물을 콕 터뜨리세요! 콤보를 쌓으며 1초 만에 자동 반사 암기!")
    components.html(BUBBLE_GAME_HTML, height=650, scrolling=False)
