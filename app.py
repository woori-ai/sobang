# -*- coding: utf-8 -*-
"""
1급 소방안전관리자 합격 올인원 튜터 웹앱
- 문제 풀이 후 정답 및 상세 해설 카드 고정 노출 (암기 후 다음 문제 버튼 클릭 시 이동)
- 기본값: 안 푼 문제만 순차 노출 (진도 클리어 방식)
- 4가지 상태 필터 (안 푼 문제 / 오답 복습 / 헷갈림 별표 / 전체 보기)
- 4지선다 122제 (실전 컬러 사진 및 계산문제 포함, 심폐소생술 제외)
- 지엽적 방어선 OX 68제
- 🎮 우측 공간 및 전용 모드: 10대 핵심 수치 짝맞추기 게임 & 암기 족보 윈도우
"""

import streamlit as st
import json, os, random, time
from bubble_game import render_bubble_game

st.set_page_config(
    page_title="1급 소방안전관리자 합격 튜터",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모바일/PC 버튼 텍스트 자동 줄바꿈(잘림 방지) 커스텀 CSS
st.markdown("""
<style>
div[data-testid="stButton"] button {
    white-space: normal !important;
    word-break: break-word !important;
    height: auto !important;
    min-height: 48px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 12px 14px !important;
    line-height: 1.5 !important;
}
div[data-testid="stButton"] button p {
    white-space: normal !important;
    word-break: break-word !important;
    text-align: left !important;
    margin: 0 !important;
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)

PROGRESS_FILE = "user_progress.json"
GAME_FILE = "game_data.json"

def load_questions():
    with open("questions_mcq.json", "r", encoding="utf-8") as f:
        mcq = json.load(f)
    with open("questions_ox.json", "r", encoding="utf-8") as f:
        ox = json.load(f)
    return mcq, ox

def load_game_data():
    if os.path.exists(GAME_FILE):
        with open(GAME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_75_cards():
    if os.path.exists("cards_75.json"):
        with open("cards_75.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

mcq_data, ox_data = load_questions()
game_data = load_game_data()
cards_75_data = load_75_cards()

# 진행상황 로컬 저장/로드
def load_progress():
    default_prog = {
        "mcq_answers": {},
        "ox_answers": {},
        "c75_answers": {},
        "wrong_mcqs": [],
        "wrong_oxs": [],
        "wrong_c75s": [],
        "starred_mcqs": [],
        "starred_oxs": [],
        "starred_c75s": []
    }
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k in default_prog:
                    if k not in data:
                        data[k] = default_prog[k]
                return data
        except Exception:
            pass
    return default_prog

def save_progress(prog):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(prog, f, ensure_ascii=False, indent=2)

if "prog" not in st.session_state:
    st.session_state.prog = load_progress()

if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0

if "ox_idx" not in st.session_state:
    st.session_state.ox_idx = 0

if "c75_card_idx" not in st.session_state:
    st.session_state.c75_card_idx = 0

# 피드백 노출 상태 유지용 세션 키
if "mcq_feedback_id" not in st.session_state:
    st.session_state.mcq_feedback_id = None

if "ox_feedback_id" not in st.session_state:
    st.session_state.ox_feedback_id = None

if "c75_feedback_id" not in st.session_state:
    st.session_state.c75_feedback_id = None

# 우측 암기 게임 패널 상태
if "show_right_game_panel" not in st.session_state:
    st.session_state.show_right_game_panel = False

# 짝맞추기 게임 상태 초기화
if "game_theme" not in st.session_state:
    st.session_state.game_theme = "theme_1"
if "game_cards_left" not in st.session_state:
    st.session_state.game_cards_left = []
if "game_cards_right" not in st.session_state:
    st.session_state.game_cards_right = []
if "game_selected_l" not in st.session_state:
    st.session_state.game_selected_l = None
if "game_selected_r" not in st.session_state:
    st.session_state.game_selected_r = None
if "game_matched_l" not in st.session_state:
    st.session_state.game_matched_l = []
if "game_matched_r" not in st.session_state:
    st.session_state.game_matched_r = []
if "game_tries" not in st.session_state:
    st.session_state.game_tries = 0
if "game_start_time" not in st.session_state:
    st.session_state.game_start_time = time.time()

def init_game(theme_key):
    st.session_state.game_theme = theme_key
    st.session_state.game_selected_l = None
    st.session_state.game_selected_r = None
    st.session_state.game_matched_l = []
    st.session_state.game_matched_r = []
    st.session_state.game_tries = 0
    st.session_state.game_start_time = time.time()
    
    theme_info = game_data.get(theme_key, {})
    pairs = theme_info.get("pairs", [])
    lefts = [{"id": i, "text": p["left"]} for i, p in enumerate(pairs)]
    rights = [{"id": i, "text": p["right"]} for i, p in enumerate(pairs)]
    random.shuffle(lefts)
    random.shuffle(rights)
    st.session_state.game_cards_left = lefts
    st.session_state.game_cards_right = rights

if not st.session_state.game_cards_left and game_data:
    init_game(st.session_state.game_theme)

# --- 사이드바 ---
st.sidebar.title("🔥 1급 소방 튜터")
st.sidebar.caption("10월 23일 자격시험 완벽 대비")

main_tab = st.sidebar.radio(
    "학습 모드 선택",
    [
        f"🎯 실전 4지선다 퀴즈 ({len(mcq_data)}제)",
        f"📖 주제별 핵심 75제 ({len(cards_75_data)}제 4지선다·회독)",
        f"⚡ 지엽적 방어선 OX ({len(ox_data)}제)",
        "📑 핵심 연상 암기장 (10대 암기법 & 필수 족보)",
        "🎮 핵심 수치 짝맞추기 게임 (10대 테마)",
        "📊 내 학습 현황 & 오답노트"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 문제 표시 상태 (핵심 옵션)")

# 🛡️ 70점 합격 안전빵 모드 (어려운 지엽 킬러 문제 제외)
safe_mode = st.sidebar.checkbox(
    "🛡️ 70점 합격 안전빵 모드 (킬러 제외)",
    value=st.session_state.get("safe_70_mode", True),
    help="복잡하고 지엽적인 킬러 문제를 제외하고, 과락 없이 평균 70점 이상 합격에 꼭 필요한 알짜배기 기본빈출+실기응용 문제만 집중 공략합니다!"
)
st.session_state.safe_70_mode = safe_mode

# ★ 4대 상태 필터: 기본값은 "안 푼 문제만 보기"
status_filter = st.sidebar.radio(
    "어떤 문제를 볼까요?",
    [
        "🆕 1. 안 푼 문제만 보기 (기본값)",
        "❌ 2. 틀렸거나 모른 문제 보기 (오답·취약점 복습)",
        "⭐ 3. 헷갈림(별표) 문제만 보기",
        "📖 4. 전체 문제 보기 (풀었던 문제 포함)"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 검색 및 정렬 필터")

# 1. 시간표 날짜 필터
all_dates = ["전체 날짜"] + sorted(list(set(q["date"] for q in mcq_data)))
selected_date = st.sidebar.selectbox("📅 시간표 날짜별 필터", all_dates, index=0)

# 2. 교재 장별 필터
all_chapters = ["전체 장(단원)"] + sorted(list(set(f"{q['book']} > {q['chapter']}" for q in mcq_data)))
selected_chapter = st.sidebar.selectbox("📚 교재 장(단원)별 필터", all_chapters, index=0)

# 3. 그림 문제만 보기 필터
only_image = st.sidebar.checkbox("📸 그림·도면 문제만 모아보기", value=False)

# 4. 정렬 기준
sort_option = st.sidebar.selectbox(
    "↕ 문제 정렬 기준",
    ["1. 교재 목차순 (기본)", "2. 시간표 일정순", "3. 최근 오답 우선순", "4. 고난도 킬러 우선순"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎮 암기 공간 옵션")
show_panel_toggle = st.sidebar.toggle("오른쪽 암기 게임 공간 열기", value=st.session_state.show_right_game_panel)
st.session_state.show_right_game_panel = show_panel_toggle

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 기록 관리")

col_rst1, col_rst2 = st.sidebar.columns(2)
with col_rst1:
    if st.button("❌ 오답만 초기화", use_container_width=True):
        st.session_state.prog["wrong_mcqs"] = []
        st.session_state.prog["wrong_oxs"] = []
        st.session_state.prog["wrong_c75s"] = []
        st.session_state.mcq_feedback_id = None
        st.session_state.ox_feedback_id = None
        st.session_state.c75_feedback_id = None
        save_progress(st.session_state.prog)
        st.sidebar.success("오답 목록이 비워졌습니다.")
        st.rerun()
with col_rst2:
    if st.button("🔄 전체 초기화", use_container_width=True):
        st.session_state.prog = {
            "mcq_answers": {},
            "ox_answers": {},
            "c75_answers": {},
            "wrong_mcqs": [],
            "wrong_oxs": [],
            "wrong_c75s": [],
            "starred_mcqs": [],
            "starred_oxs": [],
            "starred_c75s": []
        }
        st.session_state.mcq_feedback_id = None
        st.session_state.ox_feedback_id = None
        st.session_state.c75_feedback_id = None
        save_progress(st.session_state.prog)
        st.session_state.card_idx = 0
        st.session_state.ox_idx = 0
        st.session_state.c75_card_idx = 0
        st.sidebar.success("모든 기록이 초기화되었습니다.")
        st.rerun()


# --- 데이터 필터링 & 정렬 로직 ---
def apply_filter(items, is_mcq=True):
    filtered = items.copy()
    
    # 0. 🛡️ 70점 합격 안전빵 모드 (지엽 킬러 문제 제외)
    if st.session_state.get("safe_70_mode", True):
        filtered = [x for x in filtered if x.get("difficulty") != "지엽킬러"]
    
    # 1. 날짜 필터
    if selected_date != "전체 날짜":
        filtered = [x for x in filtered if x.get("date") == selected_date]
        
    # 2. 장별 필터
    if selected_chapter != "전체 장(단원)":
        filtered = [x for x in filtered if f"{x.get('book')} > {x.get('chapter')}" == selected_chapter]
        
    # 3. 그림 문제만 보기 필터
    if is_mcq and only_image:
        filtered = [x for x in filtered if x.get("image")]

    # 4. ★ 상태 필터 (안 푼 문제 / 오답 / 별표 / 전체)
    solved_map = st.session_state.prog["mcq_answers"] if is_mcq else st.session_state.prog["ox_answers"]
    wrong_keys = st.session_state.prog["wrong_mcqs"] if is_mcq else st.session_state.prog["wrong_oxs"]
    starred_keys = st.session_state.prog["starred_mcqs"] if is_mcq else st.session_state.prog["starred_oxs"]
    feedback_id = st.session_state.mcq_feedback_id if is_mcq else st.session_state.ox_feedback_id
    
    if "1. 안 푼 문제만 보기" in status_filter:
        filtered = [x for x in filtered if (str(x["id"]) not in solved_map) or (x["id"] == feedback_id)]
    elif "2. 틀렸거나 모른 문제" in status_filter or "2. 내가 틀린 문제" in status_filter:
        filtered = [x for x in filtered if x["id"] in wrong_keys]
    elif "3. 헷갈림(별표)" in status_filter:
        filtered = [x for x in filtered if x["id"] in starred_keys]
        
    # 5. 정렬 (Sorting)
    if sort_option == "1. 교재 목차순 (기본)":
        filtered.sort(key=lambda x: (x.get("book", ""), x.get("chapter", ""), x["id"]))
    elif sort_option == "2. 시간표 일정순":
        filtered.sort(key=lambda x: (x.get("date", ""), x["id"]))
    elif sort_option == "3. 최근 오답 우선순":
        filtered.sort(key=lambda x: (0 if x["id"] in wrong_keys else 1, x["id"]))
    elif sort_option == "4. 고난도 킬러 우선순":
        diff_order = {"지엽킬러": 0, "실기응용": 1, "기본빈출": 2}
        filtered.sort(key=lambda x: diff_order.get(x.get("difficulty", "기본빈출"), 3))
        
    return filtered

filtered_mcqs = apply_filter(mcq_data, is_mcq=True)
filtered_oxs = apply_filter(ox_data, is_mcq=False)


# ==========================================================
# 핵심 연상 암기장 & 필수 족보 페이지 렌더링 함수
# ==========================================================
def render_memorization_page():
    st.title("📖 1급 소방 핵심 연상 암기장 & 필수 족보")
    st.caption("시험 전 반드시 외워야 할 10대 핵심 연상 암기법, 자체점검 기준, 테마별 수치를 한눈에 집중 암기하는 전용 학습 페이지입니다.")

    cat_col1, cat_col2 = st.columns([3, 1])
    with cat_col1:
        memo_category = st.radio(
            "암기 카테고리 선택",
            [
                "🔥 1. 10대 핵심 연상 암기 비법 (기출 1순위)",
                "🧯 2. 소화약제 화재별(A·B·C급) 적응성 완벽 암기 족보",
                "📋 3. 자체점검(종합·작동) 및 법령 핵심 족보",
                "📊 4. 테마별 수치 종합 요약집 (10대 테마)"
            ],
            horizontal=True
        )
    with cat_col2:
        expand_all = st.checkbox("📖 모두 펼쳐서 보기", value=True)

    st.markdown("---")

    if memo_category.startswith("🔥 1. 10대 핵심 연상 암기"):
        st.subheader("🔥 출제 빈도 1위! 10대 핵심 연상 암기 비법")
        st.caption("문장을 소리 내어 3번 읽으면 시험장에서 정답이 바로 튀어나옵니다.")

        mnemonics = [
            {
                "num": "1",
                "title": "한국소방안전원의 업무",
                "phrase": "조교가 간발의 차로 홍보 행위를 했더니 극혐하더라",
                "content": """
- **조 / 교**: **조**사연구, **교**육 업무
- **간 / 발**: **간**행물 **발**간
- **홍보**: 대국민 **홍보**
- **행**: **행**정기관 위탁 업무
- **극 / 혐**: **국**제협력 (**극**제협력)
                """,
                "trap": "화재원인조사는 소방청장·소방본부장·소방서장의 고유 권한입니다 (안전원 업무 아님!)"
            },
            {
                "num": "2",
                "title": "방염 성능 기준",
                "phrase": "바람 불어오는 20대, 불안한 30대를 길이길이 보내고 나니, 사람과 접촉하는 상상만 하는 사연 많은 적적한 50대가 되었다",
                "content": """
- **바람(불꽃 올려/잔염) 20대**: 잔염시간 **20초 이내**
- **불안(불꽃 안 올려/잔진) 30대**: 잔진시간 **30초 이내**
- **길이길이(탄화길이) 보내고**: 탄화길이 **20cm 이내**
- **접촉 상상(3회)**: 불꽃 접촉 횟수 **3회 이상**
- **사연(연기밀도 400) 많은**: 발연량 최대연기밀도 **400 이하**
- **적적한 50대(탄화면적)**: 탄화면적 **50㎠ 이내**
                """,
                "trap": "탄화길이는 20cm, 탄화면적은 50㎠! 잔염 20초와 잔진 30초 숫자를 바꿔치기하는 함정 주의!"
            },
            {
                "num": "3",
                "title": "소방신호 (사이렌 기준)",
                "phrase": "경발해훈 / 5 33 / 5 3 / 1 / 11 3",
                "content": """
- **경계신호 (5-33)**: **5**초 간격, **3**0초씩 **3**회
- **발화신호 (5-5-3)**: **5**초 간격, **5**초씩 **3**회
- **해제신호 (1)**: **1**분간 **1**회 (연속 발령)
- **훈련신호 (1-1-3)**: **1**0초 간격, **1**분씩 **3**회
                """,
                "trap": "발화신호는 다급하니 5초씩 짧게 3회! 경계신호는 미리 주의를 주니 30초씩 길게 3회!"
            },
            {
                "num": "4",
                "title": "수용인원 산정 기준",
                "phrase": "33오오 모여서 강의실 갔는데 휴교로 상실했다. 학교 몇 살까지 다닌다? 19살(1.9)까지 다닌다",
                "content": """
- **33오오 (숙박시설)**: 침대 없는 숙박시설 = 종사자 수 + (바닥면적 ÷ **3**) *(소수점 반올림)*
- **강의실 휴교상실 (1.9)**: **강**의실, **휴**게실, **교**무실, **상**담실, **실**습실 = 바닥면적 ÷ **1.9**
- *(참고)* 강당, 문화집회, 운동시설 (고정의자 없는 경우) = 바닥면적 ÷ **4.6**
                """,
                "trap": "침대 없는 숙박시설은 면적/3, 강의실/휴게실은 면적/1.9! 계산 시 소수점 이하는 무조건 반올림!"
            },
            {
                "num": "5",
                "title": "제4류 위험물 품명별 지정수량 & 대표물질 암기 공식",
                "phrase": "특수 다이아 산다 / 1등 휘·벤·톨·콜 / 아·피 / 알·사탕 메·에 / 2등 등·경·테·송·크·클 / 아·아(산) / 3등 중·크·아·니 / 에·글 / 사기·실·기",
                "content": """
- **① 특수인화물 (50 L)**: 디에틸에테르, 이황화탄소, 아세트알데히드, 산화프로필렌 ➡️ *"특수하게 디·이·아·산 (특수 다이아 산다)"*
- **② 제1석유류 (비수용 200 L / 수용성 400 L)**:
  - 비수용성(200L): 휘발유, 벤젠, 톨루엔, 콜로디온 ➡️ *"1등 휘·벤·톨·콜"*
  - 수용성(400L): 아세톤, 피리딘 ➡️ *"아·피 (물에 빠져서 아이고 피난다)"*
- **③ 알코올류 (400 L)**: 메탄올, 에탄올, 프로필알코올, 이소프로필알코올 ➡️ *"알·사(400)탕 먹고 메·에 취한다"*
  - *(핵심)* 탄소수 1~3개 포화 1가 알코올, 농도 60wt% 이상만 위험물, 단일 400L
- **④ 제2석유류 (비수용 1,000 L / 수용성 2,000 L)**:
  - 비수용성(1,000L): 등유, 경유, 테레핀유, 송근유, 크실렌, 클로로벤젠 ➡️ *"등·경·테·송·크·클"*
  - 수용성(2,000L): 아세트산(초산), 아크릴산 ➡️ *"아·아(산) (뒤에 산 붙음)"*
- **⑤ 제3석유류 (비수용 2,000 L / 수용성 4,000 L)**:
  - 비수용성(2,000L): 중유, 크레오소트유, 아닐린, 니트로벤젠 ➡️ *"중·크·아·니 (중간 크기 아니냐?)"*
  - 수용성(4,000L): 에틸렌글리콜, 글리세린 ➡️ *"에·글 (물에 빠져 애글복걸)"*
- **⑥ 제4석유류 (6,000 L)**: 기계유, 실린더유, 기어유 ➡️ *"사(4)기·실·기 (기계 윤활유)"*
- **⑦ 동식물유류 (10,000 L)**:
  - 건성유(요오드가 130 이상): 아마인유, 들기름 ➡️ *"아·들은 마르면 건성"*
  - 반건성유(100~130): 참기름, 콩기름 ➡️ *"참·콩은 절반만"*
  - 불건성유(100 이하): 올리브유, 피마자유 ➡️ *"올·피는 절대 안 마름"*
                """,
                "trap": "알코올류는 60 wt% 이상만 해당! 제1·2·3석유류는 수용성이 되면 지정수량이 정확히 2배로 늘어납니다!"
            },
            {
                "num": "6",
                "title": "소방기본법 최고 벌칙 (5년 / 5천만원)",
                "phrase": "소방대의 출동·구조·소화 등 '소방 활동 방해' = 5년 징역 또는 5천만원 벌금",
                "content": """
- 화재진압, 인명구조, 구급활동을 방해하는 행위
- 출동하는 소방자동차의 출동을 방해하는 행위
- 소방용수시설 또는 비상소화장치를 사용하거나 효용을 해치는 행위
                """,
                "trap": "⚠️ [오답 함정] '생활안전활동 방해'는 100만원 이하 과태료입니다! 복귀 중인 소방대 방해도 제외."
            },
            {
                "num": "7",
                "title": "소방안전 특별관리시설물",
                "phrase": "공항철도 타고 지영이가 전통시장에 갔다",
                "content": """
- **공항철도**: **공항**시설, **철도**·도시철도 시설, 항만시설
- **지**: **지**정문화유산
- **영**: **영**화상영관 (수용인원 **1,000명 이상**)
- **전통시장**: **전통시장** (점포 **500개 이상**)
- *(참고)* 화재예방안전진단 주기: **5년마다 1회**
                """,
                "trap": "영화관은 500명이 아니라 1,000명 이상! 전통시장은 500개 점포 이상! 숫자를 바꿔치기함!"
            },
            {
                "num": "8",
                "title": "위험물안전관리법 과태료",
                "phrase": "위험물안전관리법 과태료 = 무조건 500만원 이하",
                "content": """
- 임시저장·취급 승인 위반
- 저장·취급 기준 준수 위반
- 위험물안전관리자 선임·해임·퇴직 신고 위반
- 지위승계, 용도폐지 신고 미이행 등
                """,
                "trap": "소방기본법(200만/100만), 소방시설법(300만)과 혼동 금지! 위험물법에서 과태료를 물으면 무조건 500만원!"
            },
            {
                "num": "9",
                "title": "종합방재실 설치 위치",
                "phrase": "이지원, 특별히 오너라",
                "content": """
- **원칙**: **1층 또는 피난층**에 설치
- **예외 (이·지·원)**: 지상 **2**층 또는 **지**하 **1**층
- **조건 (특별히 오너라)**: **특별**피난계단 출입구로부터 **5m** 이내 설치 시
                """,
                "trap": "지상 3층 이상이나 지하 2층 이하는 어떠한 경우에도 설치 불가! 오직 2층과 지하1층만 예외 허용!"
            },
            {
                "num": "10",
                "title": "주요 물질의 연소범위",
                "phrase": "중요한 다섯 손가락 / 등에 업기 실어 / 콜록콜록 36대",
                "content": """
- **중유 (1.0 ~ 5.0 %)**: **중**요한 것은 다섯 손가락 (**1~5%**)
- **등유 (0.7 ~ 5.0 %)**: **등**에 업기 실어 (**0.7 ~ 5%**)
- **메틸알코올 (6.0 ~ 36.0 %)**: **콜(6)**록콜록 **36**대 간다 (**6 ~ 36%**)
- *(참고)* 휘발유 (1.4 ~ 7.6%), 아세톤 (2.5 ~ 12.8%), LPG(프로판) (2.1 ~ 9.5%), LNG(메탄) (5 ~ 15%)
                """,
                "trap": "등유(0.7)와 중유(1.0)의 하한계 차이 및 메틸알코올(6~36%)의 넓은 범위를 정확히 외울 것!"
            },
            {
                "num": "11",
                "title": "소화기 약제별 화재(A·B·C급) 적응성",
                "phrase": "인산염·할론·할로겐·고체에어로졸은 ABC 만능 올패스! 중탄산염은 A급 탈락(BC급 전용)!",
                "content": """
- **A·B·C급 모두 적응 가능한 약제 (만능 4총사)**:
  1. **인산염류 소화약제** (제3종 분말 - 인산이수소암모늄)
  2. **할론 소화약제** (가스계)
  3. **할로겐화합물 및 불활성기체 소화약제** (가스계)
  4. **고체에어로졸화합물** (기타)
- **A급(일반화재)에 적응성이 없는 약제 (B·C급 전용)**:
  - **중탄산염류 소화약제** (제1종·제2종·제4종 분말) ➡️ **A급 불가능(-)**, B급·C급만 가능!
  - **이산화탄소($CO_2$)** ➡️ B급·C급만 가능!
                """,
                "trap": "중탄산염류(제1·2·4종) 분말은 일반화재(A급)에 적응성이 없습니다! 가장 흔한 ABC 분말 소화기는 '인산염류(제3종)'입니다!"
            }
        ]

        for item in mnemonics:
            with st.expander(f"📌 {item['num']}. {item['title']} : \"{item['phrase']}\"", expanded=expand_all):
                st.markdown(f"""
                <div style="background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 14px 18px; border-radius: 6px; margin-bottom: 12px;">
                    <span style="font-size: 15px; color: #666;">🎯 핵심 연상 암기 공식</span><br>
                    <strong style="font-size: 18px; color: #d9381e;">"{item['phrase']}"</strong>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(item["content"])
                st.warning(f"⚠️ **시험장 함정 포인트**: {item['trap']}")

    elif memo_category.startswith("🧯 2. 소화약제"):
        st.subheader("🧯 소화약제별 화재(A·B·C급) 적응성 완벽 암기 족보")
        st.caption("소방안전관리자 1급 교과서 수록 핵심 도표 기반 (ABC급 가능 약제 vs BC급 전용 약제)")

        st.markdown("""
        <div style="background-color: #f8f9fa; border-left: 5px solid #ff4b4b; padding: 14px 18px; border-radius: 6px; margin-bottom: 15px;">
            <span style="font-size: 15px; color: #666;">🎯 핵심 연상 암기 공식</span><br>
            <strong style="font-size: 18px; color: #d9381e;">"인산염·할론·할로겐·고체에어로졸은 ABC 만능 올패스! 중탄산염은 A급 탈락(BC급 전용)!"</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
| 구분 | 소화약제명 | A급 (일반화재) | B급 (유류화재) | C급 (전기화재) | 비고 및 시험 핵심 포인트 |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **분말** | **인산염류 소화약제 (제3종)** | **⭕ O** | **⭕ O** | **⭕ O** | **★대표적인 ABC급 소화기** (인산이수소암모늄 / 담홍색) |
| **분말** | **중탄산염류 소화약제 (제1·2·4종)** | **❌ -** | **⭕ O** | **⭕ O** | **⚠️ A급 적응성 없음! (BC급 전용)** |
| **가스** | **할론 소화약제** | **⭕ O** | **⭕ O** | **⭕ O** | ABC급 전소화약제 (부촉매 소화) |
| **가스** | **할로겐화합물 및 불활성기체 소화약제** | **⭕ O** | **⭕ O** | **⭕ O** | 친환경 가스계 소화약제 (ABC급 전소화약제) |
| **기타** | **고체에어로졸화합물** | **⭕ O** | **⭕ O** | **⭕ O** | 고체 미립자 에어로졸 (ABC급 전소화약제) |
| *(참고)* | **이산화탄소(CO₂) 소화약제** | **❌ -** | **⭕ O** | **⭕ O** | B·C급 전용 (질식 및 냉각 소화) |
| *(참고)* | **물 소화약제 (봉상)** | **⭕ O** | **❌ -** | **❌ -** | A급 전용 (감전 위험으로 C급 절대 불가) |
""")

        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.success("""
            #### ⭕ ABC급 모두 사용 가능한 약제 (4가지)
            1. **인산염류 소화약제** (제3종 분말, $NH_4H_2PO_4$)
            2. **할론 소화약제**
            3. **할로겐화합물 및 불활성기체 소화약제**
            4. **고체에어로졸화합물**
            
            👉 일반화재(A), 유류화재(B), 전기화재(C) 가리지 않고 전부 끌 수 있는 **만능 약제 4총사**!
            """)
        with col_m2:
            st.error("""
            #### ❌ A급(일반화재)에 쓸 수 없는 약제 (단골 함정!)
            1. **중탄산염류 소화약제** (제1종, 제2종, 제4종 분말)
            2. **이산화탄소($CO_2$) 소화약제**
            
            ⚠️ **시험장 단골 함정**: *"중탄산염류 분말소화약제는 A·B·C급 화재에 모두 적응성이 있다."* ➡️ **오답(X)** (A급 불가, B·C급 전용!)
            """)

    elif memo_category.startswith("📋 3. 자체점검"):
        st.subheader("📋 자체점검(종합점검 · 작동점검) 핵심 족보")
        st.caption("시험에 가장 빈번하게 출제되는 점검 시기 판단 기준일과 종합점검 대상 6가지 총정리")

        st.markdown("""
        <div style="background-color: #eef7ff; border-left: 6px solid #0066cc; padding: 18px 20px; border-radius: 8px; margin-bottom: 18px;">
            <h4 style="color: #004080; margin-top: 0;">⏰ 1. 점검 실시 시기 & 판단 기준일</h4>
            <ul style="font-size: 16px; line-height: 1.8; margin-bottom: 0;">
                <li><strong>판단 기준일</strong>: 완공일(❌)이 아니라 <strong>'사용승인일'</strong>(⭕) 기준! <em>(★완공일은 단골 오답 함정)</em></li>
                <li><strong>종합점검 실시 시기</strong>: <strong>매년 사용승인일이 속하는 달</strong>에 실시 (달 내에서 1일~말일 중 날짜는 무관)</li>
                <li><strong>작동점검 실시 시기</strong>: <strong>종합점검을 받은 달로부터 6개월이 되는 달</strong>에 실시 (날짜 무관)</li>
                <li><em>예시: 사용승인일이 5월 12일인 대상물 ➡️ 종합점검은 5월 중, 작동점검은 11월 중에 실시</em></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🏢 2. 종합점검 대상 (핵심 6가지)")
        c1, c2 = st.columns(2)
        with c1:
            st.info("""
            **1. 스프링클러설비 설치 대상**
            - 스프링클러설비가 설치된 **모든 특정소방대상물** (연면적 무관 전수 대상)
            
            **2. 물분무등소화설비 설치 대상**
            - 물분무등소화설비가 설치된 연면적 **5,000㎡ 이상**인 특정소방대상물
            
            **3. 다중이용업소 설치 대상**
            - 다중이용업의 영업장이 설치된 연면적 **2,000㎡ 이상**인 특정소방대상물
            """)
        with c2:
            st.info("""
            **4. 터널 시설**
            - **제연설비**가 설치된 도로 터널
            
            **5. 공공기관 시설**
            - 옥내소화전설비 또는 자동화재탐지설비가 설치된 연면적 **1,000㎡ 이상**인 공공기관
            
            **6. 건축물의 최초점검**
            - 신축 등으로 사용승인을 받은 특정소방대상물은 **사용승인일로부터 60일 이내**에 종합점검 실시
            """)

    elif memo_category.startswith("📊 4. 테마별 수치"):
        st.subheader("📊 테마별 핵심 수치 종합 요약집 (10대 테마)")
        st.caption("수치 짝맞추기 게임에 수록된 10대 핵심 테마의 요약 족보(치트시트)를 한눈에 모아봅니다.")

        for t_key, t_val in game_data.items():
            with st.expander(f"📌 {t_val['title']}", expanded=False):
                st.markdown(t_val.get("cheat_sheet", "요약 내용이 없습니다."))


# ==========================================================
# 공통 짝맞추기 게임 렌더링 함수
# ==========================================================
def render_matching_game(is_compact=False):
    if not game_data:
        st.warning("게임 데이터가 준비되지 않았습니다.")
        return

    theme_keys = list(game_data.keys())
    theme_titles = [game_data[k]["title"] for k in theme_keys]
    
    curr_theme_idx = theme_keys.index(st.session_state.game_theme) if st.session_state.game_theme in theme_keys else 0
    
    sel_title = st.selectbox(
        "🎯 암기 테마 선택",
        theme_titles,
        index=curr_theme_idx,
        key="compact_theme_sel" if is_compact else "full_theme_sel"
    )
    selected_key = theme_keys[theme_titles.index(sel_title)]
    
    if selected_key != st.session_state.game_theme:
        init_game(selected_key)
        st.rerun()

    theme_obj = game_data[selected_key]
    
    # [📖 암기 사항 요약 윈도우 (치트시트 족보)]
    with st.expander("📖 [암기 족보 윈도우] 핵심 공식 & 표 보기 (클릭)", expanded=False):
        st.markdown(theme_obj.get("cheat_sheet", "암기 요약 내용이 없습니다."))
        
    pairs = theme_obj.get("pairs", [])
    total_pairs = len(pairs)
    matched_count = len(st.session_state.game_matched_l)
    
    # 상태 대시보드
    status_col1, status_col2, status_col3 = st.columns([2, 1, 1])
    with status_col1:
        st.write(f"🧩 **매칭 현황**: `{matched_count} / {total_pairs} 완료`")
    with status_col2:
        st.write(f"🎯 **시도**: `{st.session_state.game_tries}회`")
    with status_col3:
        if st.button("🔄 리셋", key=f"rst_game_{is_compact}", use_container_width=True):
            init_game(selected_key)
            st.rerun()
            
    # 전체 완료 여부 체크
    if matched_count == total_pairs and total_pairs > 0:
        elapsed = int(time.time() - st.session_state.game_start_time)
        st.success(f"🎉 **퍼펙트 클리어!** ({elapsed}초 소요 / {st.session_state.game_tries}회 시도)")
        st.balloons()
        if st.button("👉 다음 암기 테마로 넘어가기", type="primary", use_container_width=True, key=f"next_th_{is_compact}"):
            next_idx = (curr_theme_idx + 1) % len(theme_keys)
            init_game(theme_keys[next_idx])
            st.rerun()
        return

    st.caption("💡 **플레이 방법**: 왼쪽 [품명/항목] 하나와 오른쪽 [수치/규격] 하나를 차례로 클릭하여 짝을 맞추세요!")

    col_l, col_r = st.columns(2)
    
    # 1. 왼쪽 카드 열
    with col_l:
        st.markdown("**[ 🟦 품명 / 대상 ]**")
        for item in st.session_state.game_cards_left:
            cid = item["id"]
            ctext = item["text"]
            is_matched = cid in st.session_state.game_matched_l
            is_selected = (st.session_state.game_selected_l == cid)
            
            btn_key = f"gl_{selected_key}_{cid}_{is_compact}"
            if is_matched:
                st.button(f"✅ {ctext}", key=btn_key, disabled=True, use_container_width=True)
            else:
                btn_type = "primary" if is_selected else "secondary"
                label = f"👉 {ctext}" if is_selected else ctext
                if st.button(label, key=btn_key, type=btn_type, use_container_width=True):
                    st.session_state.game_selected_l = cid
                    if st.session_state.game_selected_r is not None:
                        st.session_state.game_tries += 1
                        val_l = pairs[st.session_state.game_selected_l]["right"]
                        val_r = pairs[st.session_state.game_selected_r]["right"]
                        if val_l == val_r:
                            st.session_state.game_matched_l.append(st.session_state.game_selected_l)
                            st.session_state.game_matched_r.append(st.session_state.game_selected_r)
                            st.toast(f"🎉 매칭 성공! ({val_l})", icon="✅")
                        else:
                            st.toast("❌ 짝이 맞지 않습니다! 다시 시도하세요.", icon="⚠️")
                        st.session_state.game_selected_l = None
                        st.session_state.game_selected_r = None
                    st.rerun()

    # 2. 오른쪽 카드 열
    with col_r:
        st.markdown("**[ 🟨 수치 / 기준 ]**")
        for item in st.session_state.game_cards_right:
            cid = item["id"]
            ctext = item["text"]
            is_matched = cid in st.session_state.game_matched_r
            is_selected = (st.session_state.game_selected_r == cid)
            
            btn_key = f"gr_{selected_key}_{cid}_{is_compact}"
            if is_matched:
                st.button(f"✅ {ctext}", key=btn_key, disabled=True, use_container_width=True)
            else:
                btn_type = "primary" if is_selected else "secondary"
                label = f"👉 {ctext}" if is_selected else ctext
                if st.button(label, key=btn_key, type=btn_type, use_container_width=True):
                    st.session_state.game_selected_r = cid
                    if st.session_state.game_selected_l is not None:
                        st.session_state.game_tries += 1
                        val_l = pairs[st.session_state.game_selected_l]["right"]
                        val_r = pairs[st.session_state.game_selected_r]["right"]
                        if val_l == val_r:
                            st.session_state.game_matched_l.append(st.session_state.game_selected_l)
                            st.session_state.game_matched_r.append(st.session_state.game_selected_r)
                            st.toast(f"🎉 매칭 성공! ({val_r})", icon="✅")
                        else:
                            st.toast("❌ 짝이 맞지 않습니다! 다시 시도하세요.", icon="⚠️")
                        st.session_state.game_selected_l = None
                        st.session_state.game_selected_r = None
                    st.rerun()


# ==========================================================
# 탭 1: 4지선다 퀴즈 (우측 공간 분할 지원)
# ==========================================================
if main_tab.startswith("🎯 실전 4지선다"):
    st.title("🎯 실전 4지선다 기출·응용 퀴즈")
    
    # 상단 정보 헤더 & 우측 공간 토글
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        safe_badge = " &nbsp;`[🛡️ 70점 안전빵]`" if st.session_state.get("safe_70_mode", True) else ""
        st.write(f"📌 **잔여 문제**: **{len(filtered_mcqs)}문항**{safe_badge} &nbsp;|&nbsp; 모드: `{status_filter}`")
    with header_col2:
        view_mode = st.radio("화면 모드", ["🃏 카드 뷰", "📜 리스트 뷰"], horizontal=True)
    with header_col3:
        panel_on = st.toggle("🎮 우측 암기창", value=st.session_state.show_right_game_panel, key="mcq_panel_toggle")
        if panel_on != st.session_state.show_right_game_panel:
            st.session_state.show_right_game_panel = panel_on
            st.rerun()

    st.markdown("---")

    # 우측 공간 레이아웃 분할
    if st.session_state.show_right_game_panel:
        col_main, col_side = st.columns([65, 35])
    else:
        col_main = st.container()
        col_side = None

    with col_main:
        # --- 완료 상태 화면 (안 푼 문제가 없을 때) ---
        if len(filtered_mcqs) == 0:
            if "1. 안 푼 문제만 보기" in status_filter:
                st.balloons()
                st.success("🎉 **축하합니다! 현재 조건의 모든 문제를 다 풀었습니다!**")
                st.markdown("""
                - 왼쪽 사이드바에서 **`❌ 2. 내가 틀린 문제만 보기 (오답 복습)`**를 선택하여 틀린 문제만 다시 풀어보시거나,
                - **`📖 4. 전체 문제 보기`**로 전환하여 전체 문제를 족보처럼 회독하실 수 있습니다.
                - 다시 처음부터 풀고 싶으시다면 왼쪽 아래의 **`🔄 전체 초기화`** 버튼을 누르시면 됩니다.
                """)
            elif "2. 내가 틀린 문제만 보기" in status_filter:
                st.success("🎉 **현재 틀린 문제(오답)가 없습니다! 완벽하게 마스터하셨습니다.**")
            elif "3. 헷갈림(별표)" in status_filter:
                st.info("⭐ 아직 헷갈림(별표)으로 등록한 문제가 없습니다. 문제 카드 상단의 ⭐ 버튼을 눌러 등록해 보세요.")
            else:
                st.warning("선택한 조건에 해당하는 문제가 없습니다. 날짜나 장(단원) 필터를 조정해 보세요.")
                
        # --- 모드 A: 1문제씩 카드 뷰 ---
        elif view_mode == "🃏 카드 뷰":
            if st.session_state.mcq_feedback_id is not None:
                matching = [i for i, q in enumerate(filtered_mcqs) if q["id"] == st.session_state.mcq_feedback_id]
                if matching:
                    st.session_state.card_idx = matching[0]

            if st.session_state.card_idx >= len(filtered_mcqs):
                st.session_state.card_idx = max(0, len(filtered_mcqs) - 1)
                
            cur_q = filtered_mcqs[st.session_state.card_idx]
            q_id = cur_q["id"]
            
            badge_col1, badge_col2 = st.columns([3, 1])
            with badge_col1:
                st.markdown(f"### [ Q{st.session_state.card_idx + 1} / {len(filtered_mcqs)} ] &nbsp; `ID: {q_id}`")
                st.markdown(f"🏷️ **{cur_q['book']}** > **{cur_q['chapter']}** | 📅 `{cur_q['date']}` | 난이도: **{cur_q['difficulty']}**")
            with badge_col2:
                is_starred = q_id in st.session_state.prog["starred_mcqs"]
                star_label = "⭐ 헷갈림 해제" if is_starred else "☆ 헷갈림(별표) 등록"
                if st.button(star_label, key=f"star_mcq_{q_id}"):
                    if is_starred:
                        st.session_state.prog["starred_mcqs"].remove(q_id)
                    else:
                        st.session_state.prog["starred_mcqs"].append(q_id)
                    save_progress(st.session_state.prog)
                    st.rerun()

            if cur_q.get("image") and os.path.exists(cur_q["image"]):
                st.image(cur_q["image"], use_container_width=True)
            st.info(f"**{cur_q['question']}**")

            saved_ans = st.session_state.prog["mcq_answers"].get(str(q_id))

            # 보기 선택지 버튼 (2개씩 행 단위 배치하여 모바일에서도 1->2->3->4 순서 완벽 유지)
            opts = cur_q["options"]
            for r in range(0, len(opts), 2):
                row_cols = st.columns(2)
                for c in range(2):
                    idx = r + c
                    if idx < len(opts):
                        btn_label = f"**{idx+1}.** {opts[idx]}"
                        with row_cols[c]:
                            if st.button(btn_label, key=f"mcq_{q_id}_{idx}", use_container_width=True):
                                chosen = idx + 1
                                correct = cur_q["answer"]
                                st.session_state.prog["mcq_answers"][str(q_id)] = chosen
                                st.session_state.mcq_feedback_id = q_id
                                
                                if chosen == correct:
                                    if q_id in st.session_state.prog["wrong_mcqs"]:
                                        st.session_state.prog["wrong_mcqs"].remove(q_id)
                                else:
                                    if q_id not in st.session_state.prog["wrong_mcqs"]:
                                        st.session_state.prog["wrong_mcqs"].append(q_id)
                                        
                                save_progress(st.session_state.prog)
                                st.rerun()

            # 4지 선다 아래: '잘 모르겠어요' 버튼 (오답 및 취약점 바구니에 자동 저장)
            if saved_ans is None:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("❓ 잘 모르겠어요 (정답 확인 & 취약점 복습 등록)", key=f"unknown_mcq_{q_id}", use_container_width=True):
                    st.session_state.prog["mcq_answers"][str(q_id)] = 0  # 0: 모름 표시
                    st.session_state.mcq_feedback_id = q_id
                    if q_id not in st.session_state.prog["wrong_mcqs"]:
                        st.session_state.prog["wrong_mcqs"].append(q_id)
                    save_progress(st.session_state.prog)
                    st.rerun()

            # ★ 풀이 후 정답 및 상세 해설 카드 표시 ★
            if saved_ans is not None:
                st.markdown("---")
                correct_ans = cur_q["answer"]
                correct_text = cur_q["options"][correct_ans - 1]
                
                # 방금 문제를 푼 직후(feedback_id == q_id)에는 해설 카드가 활짝 열리고, 다음 문제로 넘어가면 자동으로 닫히게 처리
                is_fresh_feedback = (st.session_state.mcq_feedback_id == q_id)
                
                if saved_ans == 0:
                    st.warning(f"### ❓ '모름'으로 체크되었습니다! (실제 정답: {correct_ans}번. {correct_text})")
                    st.info("📌 찍어서 맞추는 실수를 방지하고 다음에 다시 확실히 풀 수 있도록 **[오답·취약점 복습 바구니]**에 저장되었습니다. 아래 핵심 원리를 암기하세요!")
                elif saved_ans == correct_ans:
                    st.success(f"### ⭕ 정답입니다! (선택: {saved_ans}번)")
                else:
                    st.error(f"### ❌ 오답입니다! (내가 찍은 답: {saved_ans}번 / 실제 정답: {correct_ans}번)")

                explanation_card_html = f"""
                <div style="background-color: #f0f7ff; border-left: 6px solid #0066cc; padding: 18px 22px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="color: #004080; margin-top: 0; font-size: 18px;">📌 [정답 확인] : {correct_ans}번. {correct_text}</h4>
                    <div style="font-size: 16px; line-height: 1.7; color: #1a1a1a; margin-bottom: 12px; background: white; padding: 12px 16px; border-radius: 6px; border: 1px solid #d0e2ff;">
                        <strong style="color: #0056b3;">💡 상세 해설 및 원리</strong><br>{cur_q['explanation']}
                    </div>
                    <div style="background-color: #fff3cd; border: 1px solid #ffeeba; padding: 12px 16px; border-radius: 6px; color: #856404; font-size: 15px; line-height: 1.6;">
                        <strong>⚠️ 시험장 출제 함정 포인트</strong><br>{cur_q['trap_tip']}
                    </div>
                </div>
                """

                if is_fresh_feedback:
                    st.markdown(explanation_card_html, unsafe_allow_html=True)
                else:
                    with st.expander("💡 [정답 및 상세 해설 확인하기] (클릭 시 열림)", expanded=False, key=f"post_expander_mcq_{q_id}"):
                        st.markdown(explanation_card_html, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                btn_label = "👉 [암기 완료!] 다음 안 푼 문제로 이동 ▶" if "1. 안 푼 문제만 보기" in status_filter else "👉 [암기 완료!] 다음 문제로 이동 ▶"
                if st.button(btn_label, type="primary", use_container_width=True, key=f"next_btn_{q_id}"):
                    st.session_state.mcq_feedback_id = None
                    if "1. 안 푼 문제만 보기" in status_filter:
                        if st.session_state.card_idx >= len(filtered_mcqs) - 1:
                            st.session_state.card_idx = 0
                    else:
                        if st.session_state.card_idx < len(filtered_mcqs) - 1:
                            st.session_state.card_idx += 1
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.button("◀ 이전 문제", use_container_width=True, disabled=(st.session_state.card_idx == 0)):
                    st.session_state.mcq_feedback_id = None
                    st.session_state.card_idx = max(0, st.session_state.card_idx - 1)
                    st.rerun()
            with nav_col2:
                cur_num = min(st.session_state.card_idx + 1, len(filtered_mcqs))
                pct = int(cur_num / len(filtered_mcqs) * 100) if len(filtered_mcqs) > 0 else 0
                st.progress(pct / 100.0, text=f"진행도 {cur_num}/{len(filtered_mcqs)} ({pct}%)")
            with nav_col3:
                if st.button("다음 문제 ▶", use_container_width=True, disabled=(st.session_state.card_idx >= len(filtered_mcqs) - 1)):
                    st.session_state.mcq_feedback_id = None
                    st.session_state.card_idx = min(len(filtered_mcqs) - 1, st.session_state.card_idx + 1)
                    st.rerun()

        # --- 모드 B: 전체 리스트 뷰 ---
        elif view_mode == "📜 리스트 뷰":
            st.info("💡 전체 문제를 한 화면에서 빠르게 회독할 수 있는 모드입니다.")
            for idx, q in enumerate(filtered_mcqs):
                q_id = q["id"]
                st.markdown(f"#### Q{idx + 1}. [ID:{q_id}] {q['question']}")
                if q.get("image") and os.path.exists(q["image"]):
                    st.image(q["image"], width=400)
                for opt_idx, opt in enumerate(q["options"]):
                    opt_prefix = f"**{opt_idx + 1}**"
                    is_correct_opt = (opt_idx + 1 == q["answer"])
                    if is_correct_opt:
                        st.markdown(f"- ✅ {opt_prefix}: **{opt}** (정답)")
                    else:
                        st.markdown(f"- {opt_prefix}: {opt}")
                st.info(f"💡 **상세 해설**: {q['explanation']} | ⚠️ **함정 포인트**: {q['trap_tip']}")
                st.markdown("---")

    # 우측 공간 렌더링
    if col_side is not None:
        with col_side:
            st.markdown("### 🎮 우측 수치 암기 놀이터")
            st.caption("문제를 풀며 옆에서 즉시 짝맞추기 암기!")
            render_matching_game(is_compact=True)


# ==========================================================
# 탭 1.5: 📖 주제별 핵심 75제 (답 가리기 회독노트)
# ==========================================================
elif main_tab.startswith("📖 주제별 핵심 75제"):
    st.title("📖 소방안전관리자 1급 주제별 핵심 75제 (실전 4지선다)")
    st.caption("영상 2편 + 실전 문제집 통합 & 75문항 완전 4지선다 객관식화 완료! 실전 퀴즈 풀이와 회독 노트를 모두 지원합니다.")

    tab_quiz75, tab_notes75, tab_cov75, tab_corr75 = st.tabs([
        "🎯 75제 실전 4지선다 퀴즈",
        "📑 75제 단권화 회독 (답 가리기)",
        "📊 커버리지 & 출제 빈도 분석",
        "⚠️ 오류 정정표 & 보강 요약"
    ])

    # ----------------------------------------------------
    # 공통 필터링 로직 (단원, 중복출제, 오류정정, 검색어)
    # ----------------------------------------------------
    ch_list_75 = ["전체 단원 보기"] + sorted(list(set(c["chapter_name"] for c in cards_75_data)))

    # ====================================================
    # 서브 탭 1: 🎯 75제 실전 4지선다 퀴즈
    # ====================================================
    with tab_quiz75:
        # 상단 필터 & 모드 컨트롤
        q_fc1, q_fc2, q_fc3 = st.columns([2, 1, 1])
        with q_fc1:
            sel_ch_q = st.selectbox("📚 대단원 선택", ch_list_75, key="c75_quiz_ch")
        with q_fc2:
            f_dup_q = st.checkbox("🔥 최우선 암기 (중복)", value=False, key="c75_quiz_dup")
        with q_fc3:
            f_corr_q = st.checkbox("⚠️ 오류 정정 문항만", value=False, key="c75_quiz_corr")

        search_quiz = st.text_input("🔎 키워드 검색 (문제·해설·암기법)", "", key="c75_quiz_search")

        # 필터링 적용
        filtered_75 = cards_75_data
        if sel_ch_q != "전체 단원 보기":
            filtered_75 = [c for c in filtered_75 if c["chapter_name"] == sel_ch_q]
        if f_dup_q:
            filtered_75 = [c for c in filtered_75 if c.get("is_duplicate")]
        if f_corr_q:
            filtered_75 = [c for c in filtered_75 if c.get("correction")]
        if search_quiz.strip():
            sq = search_quiz.strip().lower()
            filtered_75 = [
                c for c in filtered_75
                if sq in c["title"].lower()
                or sq in c["question"].lower()
                or sq in c["explanation"].lower()
                or sq in c.get("memo", "").lower()
                or any(sq in opt.lower() for opt in c["options"])
            ]

        # 사이드바의 4대 상태 필터(안 푼 문제, 오답, 별표, 전체) 연동
        if "1. 안 푼 문제만 보기" in status_filter:
            filtered_75 = [c for c in filtered_75 if str(c["id"]) not in st.session_state.prog.get("c75_answers", {})]
        elif "2. 틀렸거나 모른 문제 보기" in status_filter:
            filtered_75 = [c for c in filtered_75 if c["id"] in st.session_state.prog.get("wrong_c75s", [])]
        elif "3. 헷갈림(별표)" in status_filter:
            filtered_75 = [c for c in filtered_75 if c["id"] in st.session_state.prog.get("starred_c75s", [])]

        # 상단 정보 헤더 & 뷰 모드
        h_col1, h_col2, h_col3 = st.columns([2, 1, 1])
        with h_col1:
            st.write(f"📌 **잔여 문제**: **{len(filtered_75)}문항** / 전체 75 &nbsp;|&nbsp; 모드: `{status_filter}`")
        with h_col2:
            view_mode_75 = st.radio("화면 모드", ["🃏 카드 뷰", "📜 리스트 뷰"], horizontal=True, key="c75_view_mode")
        with h_col3:
            panel_on_75 = st.toggle("🎮 우측 암기창", value=st.session_state.show_right_game_panel, key="c75_panel_toggle")
            if panel_on_75 != st.session_state.show_right_game_panel:
                st.session_state.show_right_game_panel = panel_on_75
                st.rerun()

        st.markdown("---")

        # 우측 분할 레이아웃
        if st.session_state.show_right_game_panel:
            col_main_75, col_side_75 = st.columns([65, 35])
        else:
            col_main_75 = st.container()
            col_side_75 = None

        with col_main_75:
            if len(filtered_75) == 0:
                if "1. 안 푼 문제만 보기" in status_filter:
                    st.balloons()
                    st.success("🎉 **축하합니다! 현재 조건의 모든 75제 문제를 다 풀었습니다!**")
                    st.markdown("""
                    - 왼쪽 사이드바에서 **`❌ 2. 내가 틀린 문제만 보기 (오답 복습)`**를 선택하여 오답을 집중 복습하시거나,
                    - **`📖 4. 전체 문제 보기`**로 전환하여 전체 75제를 족보처럼 다시 풀어보실 수 있습니다.
                    """)
                elif "2. 틀렸거나 모른 문제 보기" in status_filter:
                    st.success("🎉 **현재 75제 중 틀린 문제(오답)가 없습니다! 완벽하게 마스터하셨습니다.**")
                elif "3. 헷갈림(별표)" in status_filter:
                    st.info("⭐ 아직 헷갈림(별표)으로 등록한 75제 문제가 없습니다.")
                else:
                    st.warning("선택한 조건에 해당하는 문제가 없습니다. 단원이나 검색 필터를 조정해 보세요.")

            # --- [모드 A] 1문제씩 카드 뷰 ---
            elif view_mode_75 == "🃏 카드 뷰":
                if st.session_state.c75_feedback_id is not None:
                    matching_75 = [i for i, q in enumerate(filtered_75) if q["id"] == st.session_state.c75_feedback_id]
                    if matching_75:
                        st.session_state.c75_card_idx = matching_75[0]

                if st.session_state.c75_card_idx >= len(filtered_75):
                    st.session_state.c75_card_idx = max(0, len(filtered_75) - 1)

                cur_q = filtered_75[st.session_state.c75_card_idx]
                q_id = cur_q["id"]

                b_col1, b_col2 = st.columns([3, 1])
                with b_col1:
                    b_dup = " &nbsp;`🔥 최우선 암기(중복 출제)`" if cur_q.get("is_duplicate") else ""
                    st.markdown(f"### [ Q{st.session_state.c75_card_idx + 1} / {len(filtered_75)} ] &nbsp; `ID: {q_id}` {b_dup}")
                    st.markdown(f"🏷️ **{cur_q['chapter_name']}** | 출처: `{cur_q['source']}`")
                with b_col2:
                    is_starred = q_id in st.session_state.prog.get("starred_c75s", [])
                    star_label = "⭐ 헷갈림 해제" if is_starred else "☆ 헷갈림(별표) 등록"
                    if st.button(star_label, key=f"star_c75_{q_id}"):
                        if "starred_c75s" not in st.session_state.prog:
                            st.session_state.prog["starred_c75s"] = []
                        if is_starred:
                            st.session_state.prog["starred_c75s"].remove(q_id)
                        else:
                            st.session_state.prog["starred_c75s"].append(q_id)
                        save_progress(st.session_state.prog)
                        st.rerun()

                st.info(f"**{cur_q['question']}**")

                saved_ans = st.session_state.prog.get("c75_answers", {}).get(str(q_id))

                # 보기 선택지 버튼 (2열 배치)
                opts = cur_q["options"]
                for r in range(0, len(opts), 2):
                    row_cols = st.columns(2)
                    for c in range(2):
                        idx = r + c
                        if idx < len(opts):
                            btn_label = f"**{idx+1}.** {opts[idx]}"
                            with row_cols[c]:
                                if st.button(btn_label, key=f"btn_c75_{q_id}_{idx}", use_container_width=True):
                                    chosen = idx + 1
                                    correct = cur_q["answer"]
                                    if "c75_answers" not in st.session_state.prog:
                                        st.session_state.prog["c75_answers"] = {}
                                    if "wrong_c75s" not in st.session_state.prog:
                                        st.session_state.prog["wrong_c75s"] = []

                                    st.session_state.prog["c75_answers"][str(q_id)] = chosen
                                    st.session_state.c75_feedback_id = q_id

                                    if chosen == correct:
                                        if q_id in st.session_state.prog["wrong_c75s"]:
                                            st.session_state.prog["wrong_c75s"].remove(q_id)
                                    else:
                                        if q_id not in st.session_state.prog["wrong_c75s"]:
                                            st.session_state.prog["wrong_c75s"].append(q_id)

                                    save_progress(st.session_state.prog)
                                    st.rerun()

                # '잘 모르겠어요' 버튼
                if saved_ans is None:
                    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                    if st.button("❓ 잘 모르겠어요 (정답 확인 & 취약점 복습 등록)", key=f"unk_c75_{q_id}", use_container_width=True):
                        if "c75_answers" not in st.session_state.prog:
                            st.session_state.prog["c75_answers"] = {}
                        if "wrong_c75s" not in st.session_state.prog:
                            st.session_state.prog["wrong_c75s"] = []

                        st.session_state.prog["c75_answers"][str(q_id)] = 0
                        st.session_state.c75_feedback_id = q_id
                        if q_id not in st.session_state.prog["wrong_c75s"]:
                            st.session_state.prog["wrong_c75s"].append(q_id)
                        save_progress(st.session_state.prog)
                        st.rerun()

                # 풀이 후 채점 피드백 & 상세 해설 카드
                if saved_ans is not None:
                    st.markdown("---")
                    correct_ans = cur_q["answer"]
                    correct_text = cur_q["options"][correct_ans - 1]

                    if saved_ans == 0:
                        st.warning(f"### ❓ '모름'으로 체크되었습니다! (실제 정답: {correct_ans}번. {correct_text})")
                        st.info("📌 찍어서 맞추는 실수를 방지하기 위해 **[오답·취약점 복습 바구니]**에 저장되었습니다.")
                    elif saved_ans == correct_ans:
                        st.success(f"### ⭕ 정답입니다! (선택: {saved_ans}번. {correct_text})")
                    else:
                        st.error(f"### ❌ 오답입니다! (내가 찍은 답: {saved_ans}번 / 실제 정답: {correct_ans}번. {correct_text})")

                    st.markdown(f"""
                    <div style="background-color: #f0f7ff; border-left: 6px solid #0066cc; padding: 16px 20px; border-radius: 8px; margin: 12px 0;">
                        <h4 style="color: #004085; margin: 0 0 8px 0;">💡 정답 및 핵심 해설</h4>
                        <p style="color: #111; margin: 0; line-height: 1.6; font-size: 1.05rem;">{cur_q['explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if cur_q.get("memo"):
                        st.warning(f"💡 **암기 공식 / 두문자 꿀팁**:\n\n{cur_q['memo']}")
                    if cur_q.get("correction"):
                        st.error(f"⚠️ **[원자료 오류 정정]**:\n\n{cur_q['correction']}")

                # 하단 이전 / 다음 네비게이션
                st.markdown("<br>", unsafe_allow_html=True)
                nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
                with nav_c1:
                    if st.button("⬅️ 이전 문제", key="c75_prev_btn", use_container_width=True):
                        st.session_state.c75_card_idx = max(0, st.session_state.c75_card_idx - 1)
                        st.session_state.c75_feedback_id = None
                        st.rerun()
                with nav_c2:
                    st.markdown(f"<div style='text-align: center; color: #666; padding-top: 8px;'>문제 이동 ({st.session_state.c75_card_idx + 1} / {len(filtered_75)})</div>", unsafe_allow_html=True)
                with nav_c3:
                    if st.button("다음 문제 ➡️", key="c75_next_btn", use_container_width=True):
                        st.session_state.c75_card_idx = min(len(filtered_75) - 1, st.session_state.c75_card_idx + 1)
                        st.session_state.c75_feedback_id = None
                        st.rerun()

            # --- [모드 B] 리스트 뷰 ---
            else:
                for idx, q in enumerate(filtered_75):
                    q_id = q["id"]
                    saved_ans = st.session_state.prog.get("c75_answers", {}).get(str(q_id))
                    correct_ans = q["answer"]
                    b_dup = " `🔥 최우선 암기`" if q.get("is_duplicate") else ""

                    st.markdown(f"#### [{q_id}] {q['title']} &nbsp; `출처: {q['source']}`{b_dup}")
                    st.info(f"**{q['question']}**")

                    opts = q["options"]
                    row_c1, row_c2 = st.columns(2)
                    for opt_i, opt in enumerate(opts):
                        target_col = row_c1 if opt_i % 2 == 0 else row_c2
                        with target_col:
                            if saved_ans is not None:
                                if opt_i + 1 == correct_ans:
                                    st.success(f"**{opt_i+1}.** {opt} &nbsp; **(⭕ 정답)**")
                                elif saved_ans == opt_i + 1:
                                    st.error(f"**{opt_i+1}.** {opt} &nbsp; **(❌ 내가 고른 오답)**")
                                else:
                                    st.markdown(f"- **{opt_i+1}.** {opt}")
                            else:
                                if st.button(f"**{opt_i+1}.** {opt}", key=f"c75_list_{q_id}_{opt_i}", use_container_width=True):
                                    if "c75_answers" not in st.session_state.prog:
                                        st.session_state.prog["c75_answers"] = {}
                                    if "wrong_c75s" not in st.session_state.prog:
                                        st.session_state.prog["wrong_c75s"] = []
                                    chosen = opt_i + 1
                                    st.session_state.prog["c75_answers"][str(q_id)] = chosen
                                    if chosen == correct_ans:
                                        if q_id in st.session_state.prog["wrong_c75s"]:
                                            st.session_state.prog["wrong_c75s"].remove(q_id)
                                    else:
                                        if q_id not in st.session_state.prog["wrong_c75s"]:
                                            st.session_state.prog["wrong_c75s"].append(q_id)
                                    save_progress(st.session_state.prog)
                                    st.rerun()

                    if saved_ans is not None:
                        st.markdown(f"💡 **해설**: {q['explanation']}")
                        if q.get("memo"):
                            st.caption(f"💡 암기 공식: {q['memo']}")
                    st.markdown("---")

        # 우측 암기 놀이터 패널
        if col_side_75 is not None:
            with col_side_75:
                st.markdown("### 🎮 우측 수치 암기 놀이터")
                st.caption("75제를 풀며 옆에서 즉시 짝맞추기 암기!")
                render_matching_game(is_compact=True)

    # ====================================================
    # 서브 탭 2: 📑 75제 단권화 회독 (답 가리기 모드)
    # ====================================================
    with tab_notes75:
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            sel_ch_n = st.selectbox("📚 대단원 선택", ch_list_75, key="c75_note_ch")
        with f_col2:
            f_dup_n = st.checkbox("🔥 최우선 암기 (중복 출제만)", value=False, key="c75_note_dup")
        with f_col3:
            f_corr_n = st.checkbox("⚠️ 오류 정정 문항만", value=False, key="c75_note_corr")

        search_note = st.text_input("🔎 키워드 검색", "", key="c75_note_search")

        f_cards = cards_75_data
        if sel_ch_n != "전체 단원 보기":
            f_cards = [c for c in f_cards if c["chapter_name"] == sel_ch_n]
        if f_dup_n:
            f_cards = [c for c in f_cards if c.get("is_duplicate")]
        if f_corr_n:
            f_cards = [c for c in f_cards if c.get("correction")]
        if search_note.strip():
            sq = search_note.strip().lower()
            f_cards = [
                c for c in f_cards
                if sq in c["title"].lower()
                or sq in c["question"].lower()
                or sq in c["explanation"].lower()
                or sq in c.get("memo", "").lower()
                or any(sq in opt.lower() for opt in c["options"])
            ]

        ctrl_c1, ctrl_c2 = st.columns([3, 1])
        with ctrl_c1:
            st.markdown(f"**현재 표시된 문항**: 총 **{len(f_cards)}문항** / 전체 75문항")
        with ctrl_c2:
            exp_all = st.toggle("📂 전체 정답 일괄 열기", value=False, key="c75_toggle_all")

        st.markdown("---")

        if not f_cards:
            st.info("조건에 맞는 문항이 없습니다. 필터를 변경해 보세요.")
        else:
            for c_idx, item in enumerate(f_cards):
                b_source = f"`출처: {item['source']}`"
                b_dup = " &nbsp;`🔥 최우선 암기(중복 출제)`" if item.get("is_duplicate") else ""

                st.markdown(f"#### [{item['id']}] {item['title']} &nbsp; {b_source}{b_dup}")
                st.markdown(f"**{item['question']}**")

                if item["options"]:
                    for opt_i, opt in enumerate(item["options"]):
                        st.markdown(f"- **{opt_i+1}.** {opt}")

                with st.expander("💡 [정답 및 상세 해설 보기]", expanded=exp_all):
                    ans_num = item['answer']
                    ans_text = item['options'][ans_num - 1] if 1 <= ans_num <= len(item['options']) else ""
                    st.success(f"📌 **정답: {ans_num}번. {ans_text}**")
                    st.info(f"💡 **상세 해설**: {item['explanation']}")
                    if item.get("memo"):
                        st.warning(f"**💡 암기 공식 / 두문자 꿀팁**:\n\n{item['memo']}")
                    if item.get("correction"):
                        st.error(f"**⚠️ [원자료 오류 정정]**:\n\n{item['correction']}")

                st.markdown("---")

    with tab_cov75:
        st.subheader("📊 3대 원자료 커버리지 & 문항 분포")
        st.markdown("""
        - **통합 원자료**: 영상 강의 2편(A, B) + 실전 문제집(P)
        - **원자료 총 문항**: 91문항 ➡️ 중복 통합 후 **75개 핵심 카드**
        - **출처 표기 안내**:
          - `A`: 잔머리머리 영상(xlMj9jz9gFQ)
          - `B`: 잔머리머리 영상 1/2(Ij__JNUyOG8)
          - `P`: 실전 문제집 (T=테마, S=특강, R=복원)
        """)
        st.markdown("### 🏆 여러 자료에 겹쳐 나온 주제 (최우선 암기 14개)")
        dup_table = [
            {"주제": "실무교육 이수 기한", "출처": "B-4 · P-07", "번호": "2-6"},
            {"주제": "작동·종합점검 시기", "출처": "B-5 · P-10", "번호": "3-1"},
            {"주제": "방화구획 기준 및 개수 산정", "출처": "B-8 · P-20", "번호": "5-1"},
            {"주제": "건폐율·용적률", "출처": "P-17 · P-49", "번호": "5-3"},
            {"주제": "종합방재실 위치", "출처": "P-25 · P-T09", "번호": "5-7"},
            {"주제": "가연물의 구비조건", "출처": "B-11 · P-21", "번호": "6-1"},
            {"주제": "연소범위(폭발한계)", "출처": "B-12 · P-T10 · P-24", "번호": "6-2"},
            {"주제": "제4류 위험물 지정수량", "출처": "A-2 · P-14 · P-T05", "번호": "7-1"},
            {"주제": "LPG·LNG 특성과 누설경보기", "출처": "A-3 · P-24", "번호": "7-4"},
            {"주제": "소화기 능력단위·개수 산정", "출처": "P-27 · P-T14", "번호": "8-1"},
            {"주제": "옥내소화전 방수압력", "출처": "A-4 · P-30", "번호": "8-4"},
            {"주제": "스프링클러 방수 기준·기준개수", "출처": "A-5 · P-34 · P-35", "번호": "8-8"},
            {"주제": "습식 스프링클러 작동 순서", "출처": "P-32 · P-33", "번호": "8-10"},
            {"주제": "소방계획 수립 절차", "출처": "A-9 · P-42", "번호": "10-2"},
        ]
        st.table(dup_table)

    with tab_corr75:
        st.subheader("⚠️ 원자료 오류 정정표")
        corrections_list = [
            {"출처": "A-2 (7-1)", "원자료 내용": "유황 200kg, 휘발유 1,000L", "바른 내용": "황 100kg, 휘발유 200L"},
            {"출처": "B-3 (2-1)", "원자료 내용": "지하층 포함 30층 아파트 = 특급", "바른 내용": "아파트 층수는 지하층 제외. 특급 아파트는 50층 이상"},
            {"출처": "B-12 (6-2)", "원자료 내용": "등유는 가솔린보다 연소범위가 '높다'", "바른 내용": "등유 0.7~5% (가솔린 1.4~7.6%보다 낮고 좁음)"},
            {"출처": "A-1 (6-3)", "원자료 내용": "3~5m/s = 농연일 때", "바른 내용": "3~5m/s = 계단실 내 수직 이동"},
            {"출처": "A-5 (8-8)", "원자료 내용": "8m 이상 판매시설 20개", "바른 내용": "판매시설은 30개"},
            {"출처": "P-11 (4-4)", "원자료 내용": "보기 ③ 선임신고 태만 = 100만원 벌금", "바른 내용": "선임신고 미이행은 200만원 과태료 (보기 구성 오류)"},
            {"출처": "P-36 (9-1)", "원자료 내용": "해설 내 조건 혼선", "바른 내용": "부착높이 4~8m, 기준면적 45㎡ → 7개로 정리"}
        ]
        st.table(corrections_list)


# ==========================================================
# 탭 2: 지엽적 방어선 OX 족보
# ==========================================================
elif main_tab.startswith("⚡ 지엽적 방어선 OX"):
    st.title("⚡ 교재 구석 킬러 방어선 OX 족보")
    st.caption("단서조항(단, ~제외), 특수가연물 기준수량, 벌칙/과태료, 예외 규정 1초 스피드 정복")
    
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        safe_badge_ox = " &nbsp;`[🛡️ 70점 안전빵]`" if st.session_state.get("safe_70_mode", True) else ""
        st.write(f"📌 **현재 조건 잔여 OX**: **{len(filtered_oxs)}문항**{safe_badge_ox} &nbsp;|&nbsp; 모드: `{status_filter}`")
    with header_col2:
        ox_view = st.radio("화면 모드", ["🃏 1문 1답 카드", "📜 전체 리스트"], horizontal=True)
    with header_col3:
        panel_on_ox = st.toggle("🎮 우측 암기창", value=st.session_state.show_right_game_panel, key="ox_panel_toggle")
        if panel_on_ox != st.session_state.show_right_game_panel:
            st.session_state.show_right_game_panel = panel_on_ox
            st.rerun()

    st.markdown("---")

    if st.session_state.show_right_game_panel:
        col_ox_main, col_ox_side = st.columns([65, 35])
    else:
        col_ox_main = st.container()
        col_ox_side = None

    with col_ox_main:
        if len(filtered_oxs) == 0:
            st.success("🎉 현재 조건의 모든 OX 문제를 완료했습니다!")
            
        elif ox_view == "🃏 1문 1답 카드":
            if st.session_state.ox_feedback_id is not None:
                matching_ox = [i for i, x in enumerate(filtered_oxs) if x["id"] == st.session_state.ox_feedback_id]
                if matching_ox:
                    st.session_state.ox_idx = matching_ox[0]

            if st.session_state.ox_idx >= len(filtered_oxs):
                st.session_state.ox_idx = max(0, len(filtered_oxs) - 1)
                
            cur_ox = filtered_oxs[st.session_state.ox_idx]
            ox_id = cur_ox["id"]
            
            st.markdown(f"### [ OX No. {st.session_state.ox_idx + 1} / {len(filtered_oxs)} ] &nbsp; `ID: {ox_id}`")
            st.markdown(f"📚 **{cur_ox['book']}** > **{cur_ox['chapter']}** | 📅 `{cur_ox['date']}` | 난이도: **{cur_ox['difficulty']}**")
            
            st.success(f"### Q. {cur_ox['statement']}")
            
            saved_ox_ans = st.session_state.prog["ox_answers"].get(str(ox_id))
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("⭕ 그렇다 (O)", use_container_width=True, key=f"ox_o_{ox_id}"):
                    st.session_state.prog["ox_answers"][str(ox_id)] = True
                    st.session_state.ox_feedback_id = ox_id
                    if cur_ox["answer"] is True:
                        if ox_id in st.session_state.prog["wrong_oxs"]:
                            st.session_state.prog["wrong_oxs"].remove(ox_id)
                    else:
                        if ox_id not in st.session_state.prog["wrong_oxs"]:
                            st.session_state.prog["wrong_oxs"].append(ox_id)
                    save_progress(st.session_state.prog)
                    st.rerun()
                    
            with btn_col2:
                if st.button("❌ 아니다 (X)", use_container_width=True, key=f"ox_x_{ox_id}"):
                    st.session_state.prog["ox_answers"][str(ox_id)] = False
                    st.session_state.ox_feedback_id = ox_id
                    if cur_ox["answer"] is False:
                        if ox_id in st.session_state.prog["wrong_oxs"]:
                            st.session_state.prog["wrong_oxs"].remove(ox_id)
                    else:
                        if ox_id not in st.session_state.prog["wrong_oxs"]:
                            st.session_state.prog["wrong_oxs"].append(ox_id)
                    save_progress(st.session_state.prog)
                    st.rerun()

            # OX 아래: '잘 모르겠어요' 버튼 (오답 및 취약점 바구니에 자동 저장)
            if saved_ox_ans is None:
                st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
                if st.button("❓ 잘 모르겠어요 (정답 확인 & 취약점 복습 등록)", key=f"unknown_ox_{ox_id}", use_container_width=True):
                    st.session_state.prog["ox_answers"][str(ox_id)] = "unknown"
                    st.session_state.ox_feedback_id = ox_id
                    if ox_id not in st.session_state.prog["wrong_oxs"]:
                        st.session_state.prog["wrong_oxs"].append(ox_id)
                    save_progress(st.session_state.prog)
                    st.rerun()

            if saved_ox_ans is not None:
                st.markdown("---")
                correct_ox = cur_ox["answer"]
                user_is_correct = (saved_ox_ans == correct_ox)
                ans_str = "⭕ 그렇다 (O)" if correct_ox else "❌ 아니다 (X)"
                
                is_fresh_ox_feedback = (st.session_state.ox_feedback_id == ox_id)
                
                if saved_ox_ans == "unknown":
                    st.warning(f"### ❓ '모름'으로 체크되었습니다! (실제 정답: {ans_str})")
                    st.info("📌 찍어서 맞추는 실수를 방지하고 다음에 다시 확실히 풀 수 있도록 **[오답·취약점 복습 바구니]**에 저장되었습니다. 아래 핵심 팩트를 암기하세요!")
                elif user_is_correct:
                    st.success("### 🎉 정답입니다!")
                else:
                    st.error("### ⚠️ 오답입니다! 출제자의 함정을 조심하세요.")
                    
                ox_card_html = f"""
                <div style="background-color: #f8f9fa; border-left: 6px solid #28a745; padding: 18px 22px; border-radius: 8px; margin: 15px 0;">
                    <h4 style="color: #155724; margin-top: 0;">📌 정답 확인: {ans_str}</h4>
                    <p style="font-size: 16px; line-height: 1.6; color: #333;"><strong>💡 핵심 팩트 해설</strong>: {cur_ox['explanation']}</p>
                    <p style="font-size: 15px; color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px;"><strong>⚠️ 출제 함정 포인트</strong>: {cur_ox['trap_tip']}</p>
                </div>
                """

                if is_fresh_ox_feedback:
                    st.markdown(ox_card_html, unsafe_allow_html=True)
                else:
                    with st.expander("💡 [정답 및 해설 확인하기] (클릭 시 열림)", expanded=False, key=f"post_expander_ox_{ox_id}"):
                        st.markdown(ox_card_html, unsafe_allow_html=True)
                
                btn_ox_label = "👉 [암기 완료!] 다음 안 푼 OX로 이동 ▶" if "1. 안 푼 문제만 보기" in status_filter else "👉 [암기 완료!] 다음 OX로 이동 ▶"
                if st.button(btn_ox_label, type="primary", use_container_width=True, key=f"next_ox_{ox_id}"):
                    st.session_state.ox_feedback_id = None
                    if "1. 안 푼 문제만 보기" in status_filter:
                        if st.session_state.ox_idx >= len(filtered_oxs) - 1:
                            st.session_state.ox_idx = 0
                    else:
                        if st.session_state.ox_idx < len(filtered_oxs) - 1:
                            st.session_state.ox_idx += 1
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            with nav_col1:
                if st.button("◀ 이전 OX", use_container_width=True, disabled=(st.session_state.ox_idx == 0), key="ox_prev"):
                    st.session_state.ox_feedback_id = None
                    st.session_state.ox_idx = max(0, st.session_state.ox_idx - 1)
                    st.rerun()
            with nav_col2:
                cur_num = min(st.session_state.ox_idx + 1, len(filtered_oxs))
                pct = int(cur_num / len(filtered_oxs) * 100) if len(filtered_oxs) > 0 else 0
                st.progress(pct / 100.0, text=f"진행도 {cur_num}/{len(filtered_oxs)} ({pct}%)")
            with nav_col3:
                if st.button("다음 OX ▶", use_container_width=True, disabled=(st.session_state.ox_idx >= len(filtered_oxs) - 1), key="ox_next"):
                    st.session_state.ox_feedback_id = None
                    st.session_state.ox_idx = min(len(filtered_oxs) - 1, st.session_state.ox_idx + 1)
                    st.rerun()
                    
        elif ox_view == "📜 전체 리스트":
            st.info("💡 71개 OX 족보를 스크롤하며 빠르게 복습할 수 있는 전체 리스트 모드입니다.")
            for item in filtered_oxs:
                ans_text = "O" if item["answer"] else "X"
                st.markdown(f"**[{item['book']} > {item['chapter']}]** &nbsp; `ID: {item['id']}`")
                st.success(f"**지문**: {item['statement']}")
                st.markdown(f"- **정답**: `{ans_text}`")
                st.write(f"💡 {item['explanation']}")
                st.warning(f"⚠️ {item['trap_tip']}")
                st.markdown("---")

    if col_ox_side is not None:
        with col_ox_side:
            st.markdown("### 🎮 우측 수치 암기 놀이터")
            st.caption("OX를 풀며 옆에서 즉시 짝맞추기 암기!")
            render_matching_game(is_compact=True)


# ==========================================================
# 탭 3: 📖 핵심 연상 암기장 & 필수 족보 페이지
# ==========================================================
elif main_tab.startswith("📖 핵심 연상 암기장"):
    render_memorization_page()


# ==========================================================
# 탭 4: 🎮 핵심 수치 짝맞추기 게임 (10대 테마 전용 전체화면 모드)
# ==========================================================
elif main_tab.startswith("🎮 핵심 수치 짝맞추기"):
    st.title("🎮 1급 소방 핵심 수치 게임 파크")
    st.caption("위험물 지정수량, 특수가연물, 보행거리, 벌칙 등 빈출 핵심 수치와 물질을 재미있게 플레이하며 완벽 암기!")

    game_play_mode = st.radio(
        "🕹️ 플레이할 게임을 선택하세요",
        [
            "🎈 1. 제4류 위험물 버블 팝(Catch) 아케이드 (신규!)",
            "🧩 2. 1:1 수치 짝맞추기 카드 게임 (10대 테마)"
        ],
        horizontal=True
    )
    st.markdown("---")

    if game_play_mode.startswith("🎈 1. 제4류 위험물 버블 팝"):
        render_bubble_game()
    else:
        render_matching_game(is_compact=False)


# ==========================================================
# 탭 4: 학습 현황 대시보드 & 오답노트
# ==========================================================
elif main_tab == "📊 내 학습 현황 & 오답노트":
    st.title("📊 내 학습 현황 대시보드 & 약점 분석")
    st.caption("10월 23일 시험 합격(평균 70점 이상)을 위한 실시간 달성률 분석")

    mcq_total = len(mcq_data)
    mcq_solved = len(st.session_state.prog.get("mcq_answers", {}))
    mcq_wrong = len(st.session_state.prog.get("wrong_mcqs", []))
    mcq_correct = mcq_solved - mcq_wrong
    mcq_acc = (mcq_correct / mcq_solved * 100) if mcq_solved > 0 else 0.0

    c75_total = len(cards_75_data)
    c75_solved = len(st.session_state.prog.get("c75_answers", {}))
    c75_wrong = len(st.session_state.prog.get("wrong_c75s", []))
    c75_correct = c75_solved - c75_wrong
    c75_acc = (c75_correct / c75_solved * 100) if c75_solved > 0 else 0.0

    ox_total = len(ox_data)
    ox_solved = len(st.session_state.prog.get("ox_answers", {}))
    ox_wrong = len(st.session_state.prog.get("wrong_oxs", []))
    ox_correct = ox_solved - ox_wrong
    ox_acc = (ox_correct / ox_solved * 100) if ox_solved > 0 else 0.0

    mcq_unknown = sum(1 for v in st.session_state.prog.get("mcq_answers", {}).values() if v == 0)
    c75_unknown = sum(1 for v in st.session_state.prog.get("c75_answers", {}).values() if v == 0)
    ox_unknown = sum(1 for v in st.session_state.prog.get("ox_answers", {}).values() if v == "unknown")

    # 상단 6개 메트릭 (2행 또는 3개씩 분할)
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("🎯 실전 4지선다 진척도", f"{mcq_solved} / {mcq_total}문항", f"{mcq_solved/mcq_total*100:.1f}%")
    col_stat2.metric("📖 핵심 75제 진척도", f"{c75_solved} / {c75_total}문항", f"{c75_solved/c75_total*100:.1f}%")
    col_stat3.metric("⚡ OX 족보 진척도", f"{ox_solved} / {ox_total}문항", f"{ox_solved/ox_total*100:.1f}%")

    col_acc1, col_acc2, col_acc3 = st.columns(3)
    col_acc1.metric("🎯 4지선다 정답률", f"{mcq_acc:.1f}%", f"{mcq_correct}정답 / 취약 {mcq_wrong} (모름 {mcq_unknown})")
    col_acc2.metric("📖 75제 정답률", f"{c75_acc:.1f}%", f"{c75_correct}정답 / 취약 {c75_wrong} (모름 {c75_unknown})")
    col_acc3.metric("⚡ OX 족보 정답률", f"{ox_acc:.1f}%", f"{ox_correct}정답 / 취약 {ox_wrong} (모름 {ox_unknown})")

    st.markdown("---")
    st.subheader("🚨 집중 공략: 내 오답 및 취약점(모름) 바구니 리스트")
    st.caption("틀렸거나 모른 문제를 완벽히 복습하여 정답으로 맞추면 이 리스트에서 자동으로 지워집니다.")

    if mcq_wrong == 0 and c75_wrong == 0 and ox_wrong == 0:
        st.success("🎉 현재 모든 오답·취약점 바구니가 비어 있습니다! 완벽합니다.")
    else:
        if mcq_wrong > 0:
            st.markdown(f"#### 🔴 실전 4지선다 취약 문제 ({mcq_wrong}개, 모름 {mcq_unknown}개)")
            for q in mcq_data:
                if q["id"] in st.session_state.prog.get("wrong_mcqs", []):
                    is_unk = (st.session_state.prog.get("mcq_answers", {}).get(str(q["id"])) == 0)
                    tag = "❓ [모름]" if is_unk else "❌ [오답]"
                    st.error(f"**{tag} [ID:{q['id']}] [{q['chapter']}]** {q['question']}")
                    st.write(f"- 정답: **{q['answer']}번** ({q['options'][q['answer']-1]})")
                    st.write(f"- 💡 {q['explanation']}")
                    st.markdown("---")

        if c75_wrong > 0:
            st.markdown(f"#### 🔴 주제별 핵심 75제 취약 문제 ({c75_wrong}개, 모름 {c75_unknown}개)")
            for q in cards_75_data:
                if q["id"] in st.session_state.prog.get("wrong_c75s", []):
                    is_unk_75 = (st.session_state.prog.get("c75_answers", {}).get(str(q["id"])) == 0)
                    tag_75 = "❓ [모름]" if is_unk_75 else "❌ [오답]"
                    ans_n = q["answer"]
                    ans_t = q["options"][ans_n - 1] if 1 <= ans_n <= len(q["options"]) else ""
                    st.error(f"**{tag_75} [ID:{q['id']}] [{q['chapter_name']}]** {q['question']}")
                    st.write(f"- 정답: **{ans_n}번** ({ans_t})")
                    st.write(f"- 💡 {q['explanation']}")
                    if q.get("memo"):
                        st.caption(f"💡 암기 팁: {q['memo']}")
                    st.markdown("---")

        if ox_wrong > 0:
            st.markdown(f"#### 🔴 OX 족보 취약 문제 ({ox_wrong}개, 모름 {ox_unknown}개)")
            for ox in ox_data:
                if ox["id"] in st.session_state.prog.get("wrong_oxs", []):
                    is_unk_ox = (st.session_state.prog.get("ox_answers", {}).get(str(ox["id"])) == "unknown")
                    tag_ox = "❓ [모름]" if is_unk_ox else "❌ [오답]"
                    ans_char = "O" if ox["answer"] else "X"
                    st.error(f"**{tag_ox} [ID:{ox['id']}] [{ox['chapter']}]** {ox['statement']}")
                    st.write(f"- 정답: **{ans_char}** | 💡 {ox['explanation']}")
                    st.markdown("---")
