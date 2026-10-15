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

mcq_data, ox_data = load_questions()
game_data = load_game_data()

# 진행상황 로컬 저장/로드
def load_progress():
    default_prog = {
        "mcq_answers": {},
        "ox_answers": {},
        "wrong_mcqs": [],
        "wrong_oxs": [],
        "starred_mcqs": [],
        "starred_oxs": []
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

# 피드백 노출 상태 유지용 세션 키
if "mcq_feedback_id" not in st.session_state:
    st.session_state.mcq_feedback_id = None

if "ox_feedback_id" not in st.session_state:
    st.session_state.ox_feedback_id = None

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
        f"⚡ 지엽적 방어선 OX ({len(ox_data)}제)",
        "📖 핵심 연상 암기장 (10대 암기법 & 필수 족보)",
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
        "❌ 2. 내가 틀린 문제만 보기 (오답 복습)",
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
        st.session_state.mcq_feedback_id = None
        st.session_state.ox_feedback_id = None
        save_progress(st.session_state.prog)
        st.sidebar.success("오답 목록이 비워졌습니다.")
        st.rerun()
with col_rst2:
    if st.button("🔄 전체 초기화", use_container_width=True):
        st.session_state.prog = {
            "mcq_answers": {},
            "ox_answers": {},
            "wrong_mcqs": [],
            "wrong_oxs": [],
            "starred_mcqs": [],
            "starred_oxs": []
        }
        st.session_state.mcq_feedback_id = None
        st.session_state.ox_feedback_id = None
        save_progress(st.session_state.prog)
        st.session_state.card_idx = 0
        st.session_state.ox_idx = 0
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
    elif "2. 내가 틀린 문제만 보기" in status_filter:
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
                "📋 2. 자체점검(종합·작동) 및 법령 핵심 족보",
                "📊 3. 테마별 수치 종합 요약집 (10대 테마)"
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
                "title": "제4류 위험물 주요 품명 지정수량",
                "phrase": "중2가 황백이랑 얼사 좋다고 헛둘헛둘 경등천을 건너는 삽질을 한다",
                "content": """
- **중2**: 중유 **2,000L** (제3석유류 비수용성)
- **황백**: 황 **100kg** (제2류 가연성고체)
- **얼사**: 알코올류 **400L**
- **헛둘**: 휘발유 **200L** (제1석유류 비수용성)
- **경등천**: 경유·등유 **1,000L** (제2석유류 비수용성)
- **삽질**: 질산 **300kg** (제6류 산화성액체)
                """,
                "trap": "수용성일 때는 지정수량이 2배로 뜁니다! (예: 제1석유류 비수용성 200L ➡️ 수용성 400L)"
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

    elif memo_category.startswith("📋 2. 자체점검"):
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

    elif memo_category.startswith("📊 3. 테마별 수치"):
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

            # 4지 선다 아래: 모르는 문제일 때 정답 및 해설을 먼저 확인할 수 있는 접이식 버튼 (기본 닫힘 & 고유 key)
            if saved_ans is None:
                with st.expander("💡 잘 모르겠다면? [정답 및 상세 해설 먼저 보기]", expanded=False, key=f"pre_expander_mcq_{q_id}"):
                    c_ans = cur_q["answer"]
                    c_opt = cur_q["options"][c_ans - 1]
                    st.markdown(f"### 📌 정답: **{c_ans}번. {c_opt}**")
                    st.markdown(f"**💡 상세 해설**: {cur_q['explanation']}")
                    st.warning(f"**⚠️ 시험장 함정 팁**: {cur_q['trap_tip']}")

            # ★ 풀이 후 정답 및 상세 해설 카드 표시 ★
            if saved_ans is not None:
                st.markdown("---")
                correct_ans = cur_q["answer"]
                correct_text = cur_q["options"][correct_ans - 1]
                
                # 방금 문제를 푼 직후(feedback_id == q_id)에는 해설 카드가 활짝 열리고, 다음 문제로 넘어가면 자동으로 닫히게 처리
                is_fresh_feedback = (st.session_state.mcq_feedback_id == q_id)
                
                if saved_ans == correct_ans:
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

            # 모르는 OX일 때 정답 및 해설을 먼저 확인할 수 있는 접이식 버튼 (기본 닫힘 & 고유 key)
            if saved_ox_ans is None:
                with st.expander("💡 잘 모르겠다면? [정답 및 해설 먼저 보기]", expanded=False, key=f"pre_expander_ox_{ox_id}"):
                    o_ans = "⭕ 그렇다 (O)" if cur_ox["answer"] else "❌ 아니다 (X)"
                    st.markdown(f"### 📌 정답: **{o_ans}**")
                    st.markdown(f"**💡 핵심 팩트 해설**: {cur_ox['explanation']}")
                    st.warning(f"**⚠️ 시험장 함정 팁**: {cur_ox['trap_tip']}")
                    
            if saved_ox_ans is not None:
                st.markdown("---")
                correct_ox = cur_ox["answer"]
                user_is_correct = (saved_ox_ans == correct_ox)
                ans_str = "⭕ 그렇다 (O)" if correct_ox else "❌ 아니다 (X)"
                
                is_fresh_ox_feedback = (st.session_state.ox_feedback_id == ox_id)
                
                if user_is_correct:
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
    st.title("🎮 1급 소방 핵심 수치 짝맞추기 게임 파크")
    st.caption("위험물 지정수량, 특수가연물, 보행거리, 벌칙 등 1급 시험 빈출 10대 핵심 수치를 카드 매칭으로 완벽 암기!")
    st.markdown("---")
    
    render_matching_game(is_compact=False)


# ==========================================================
# 탭 4: 학습 현황 대시보드 & 오답노트
# ==========================================================
elif main_tab == "📊 내 학습 현황 & 오답노트":
    st.title("📊 내 학습 현황 대시보드 & 약점 분석")
    st.caption("10월 23일 시험 합격(평균 70점 이상)을 위한 실시간 달성률 분석")

    mcq_total = len(mcq_data)
    mcq_solved = len(st.session_state.prog["mcq_answers"])
    mcq_wrong = len(st.session_state.prog["wrong_mcqs"])
    mcq_correct = mcq_solved - mcq_wrong
    mcq_acc = (mcq_correct / mcq_solved * 100) if mcq_solved > 0 else 0.0

    ox_total = len(ox_data)
    ox_solved = len(st.session_state.prog["ox_answers"])
    ox_wrong = len(st.session_state.prog["wrong_oxs"])
    ox_correct = ox_solved - ox_wrong
    ox_acc = (ox_correct / ox_solved * 100) if ox_solved > 0 else 0.0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("4지선다 진척도", f"{mcq_solved} / {mcq_total}문항", f"{mcq_solved/mcq_total*100:.1f}%")
    m2.metric("4지선다 정답률", f"{mcq_acc:.1f}%", f"{mcq_correct}정답 / {mcq_wrong}오답")
    m3.metric("OX 족보 진척도", f"{ox_solved} / {ox_total}문항", f"{ox_solved/ox_total*100:.1f}%")
    m4.metric("OX 족보 정답률", f"{ox_acc:.1f}%", f"{ox_correct}정답 / {ox_wrong}오답")

    st.markdown("---")
    st.subheader("🚨 집중 공략: 내 오답 바구니 리스트")
    st.caption("오답을 완벽히 복습하여 정답으로 바꾸면 이 리스트에서 자동으로 지워집니다.")

    if mcq_wrong == 0 and ox_wrong == 0:
        st.success("🎉 현재 오답 바구니가 비어 있습니다! 완벽합니다.")
    else:
        if mcq_wrong > 0:
            st.markdown(f"#### 🔴 4지선다 오답 ({mcq_wrong}개)")
            for q in mcq_data:
                if q["id"] in st.session_state.prog["wrong_mcqs"]:
                    st.error(f"**[ID:{q['id']}] [{q['chapter']}]** {q['question']}")
                    st.write(f"- 정답: **{q['answer']}번** ({q['options'][q['answer']-1]})")
                    st.write(f"- 💡 {q['explanation']}")
                    st.markdown("---")

        if ox_wrong > 0:
            st.markdown(f"#### 🔴 OX 족보 오답 ({ox_wrong}개)")
            for ox in ox_data:
                if ox["id"] in st.session_state.prog["wrong_oxs"]:
                    ans_char = "O" if ox["answer"] else "X"
                    st.error(f"**[ID:{ox['id']}] [{ox['chapter']}]** {ox['statement']}")
                    st.write(f"- 정답: **{ans_char}** | 💡 {ox['explanation']}")
                    st.markdown("---")
