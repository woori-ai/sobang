# -*- coding: utf-8 -*-
"""
소방안전관리자 1급 주제별 75제 단권화 회독 페이지
- 문제 및 보기는 기본 노출
- '정답 및 해설 보기' 클릭 시 정답, 해설, 암기 공식, 오류 정정 노트 노출
- 전체 정답 일괄 펼치기/접기 지원
"""

import streamlit as st
import json, os

st.set_page_config(
    page_title="주제별 75제 회독노트 | 소방안전관리자 1급",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 모바일 및 가독성 최적화 CSS
st.markdown("""
<style>
.q-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}
.q-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 12px;
    line-height: 1.5;
}
.q-option {
    padding: 6px 10px;
    margin: 4px 0;
    border-radius: 6px;
    background-color: #f8fafc;
    border-left: 3px solid #cbd5e1;
    font-size: 0.98rem;
    color: #334155;
}
.source-badge {
    background-color: #e0f2fe;
    color: #0369a1;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.dup-badge {
    background-color: #fee2e2;
    color: #dc2626;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 700;
}
.ans-box {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 14px 18px;
    margin-top: 10px;
}
.ans-text {
    font-size: 1.1rem;
    font-weight: 800;
    color: #15803d;
    margin-bottom: 8px;
}
.tip-box {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    padding: 10px 14px;
    border-radius: 4px;
    margin-top: 10px;
    font-size: 0.95rem;
    color: #1e40af;
}
.corr-box {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: 10px 14px;
    border-radius: 4px;
    margin-top: 10px;
    font-size: 0.95rem;
    color: #92400e;
}
</style>
""", unsafe_allow_html=True)

# 데이터 로드
DATA_FILE = "cards_75.json"

@st.cache_data
def get_cards():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

cards = get_cards()

# 상단 헤더
st.title("📖 소방안전관리자 1급 주제별 통합 75제")
st.caption("영상 2편 + 실전 문제집 통합 & 오류 정정본 | 문제·보기는 보이고, [💡 정답 및 해설]을 눌러 답을 확인하세요.")

# 탭 구성
tab_quiz, tab_analysis, tab_corrections = st.tabs([
    "📑 75제 단권화 회독 (답 가리기)",
    "📊 커버리지 & 출제 빈도 분석",
    "⚠️ 오류 정정표 & 보강 요약"
])

# -------------------------------------------------------------
# 탭 1: 문제 회독 (답 가리기)
# -------------------------------------------------------------
with tab_quiz:
    # 사이드바 필터
    st.sidebar.header("🔍 문제 필터 및 검색")
    
    chapter_list = ["전체 단원 보기"] + sorted(list(set(c["chapter_name"] for c in cards)))
    selected_chapter = st.sidebar.selectbox("📚 대단원 선택", chapter_list)
    
    filter_dup = st.sidebar.checkbox("🔥 여러 자료에 겹친 주제만 보기 (최우선 암기)", value=False)
    filter_corr = st.sidebar.checkbox("⚠️ 오류 정정 노트가 있는 문항만 보기", value=False)
    
    search_query = st.sidebar.text_input("🔎 키워드 검색 (문제·해설·암기법)", "")
    
    # 필터링 로직
    filtered = cards
    if selected_chapter != "전체 단원 보기":
        filtered = [c for c in filtered if c["chapter_name"] == selected_chapter]
    if filter_dup:
        filtered = [c for c in filtered if c.get("is_duplicate")]
    if filter_corr:
        filtered = [c for c in filtered if c.get("correction")]
    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            c for c in filtered
            if q in c["title"].lower()
            or q in c["question"].lower()
            or q in c["explanation"].lower()
            or q in c.get("memo", "").lower()
            or any(q in opt.lower() for opt in c["options"])
        ]

    # 상단 컨트롤 바
    ctrl_col1, ctrl_col2 = st.columns([3, 1])
    with ctrl_col1:
        st.markdown(f"**현재 표시된 문항**: 총 **{len(filtered)}문항** / 전체 75문항")
    with ctrl_col2:
        expand_all = st.toggle("📂 전체 정답 일괄 열기", value=False)

    st.markdown("---")

    # 문항 목록 출력
    if not filtered:
        st.info("조건에 맞는 문항이 없습니다. 필터를 변경해 보세요.")
    else:
        for idx, item in enumerate(filtered):
            badges = []
            badges.append(f"<span class='source-badge'>출처: {item['source']}</span>")
            if item.get("is_duplicate"):
                badges.append("<span class='dup-badge'>🔥 최우선 암기 (중복 출제)</span>")
            
            badge_html = " ".join(badges)
            
            # 문제 카드 헤더
            st.markdown(f"""
            <div style="margin-top: 15px; margin-bottom: 5px;">
                <span style="font-weight: 800; font-size: 1.1rem; color: #2563eb;">[{item['id']}] {item['title']}</span>
                &nbsp;&nbsp;{badge_html}
            </div>
            """, unsafe_allow_html=True)
            
            # 문제 질문
            st.markdown(f"**{item['question']}**")
            
            # 보기 출력 (4지선다 보기가 있는 경우)
            if item["options"]:
                for opt in item["options"]:
                    st.markdown(f"<div class='q-option'>{opt}</div>", unsafe_allow_html=True)
            
            # 핵심 기능: 정답 및 해설 접이식 버튼 (기본 닫힘)
            with st.expander("💡 [정답 및 상세 해설 보기]", expanded=expand_all):
                st.markdown(f"""
                <div class="ans-box">
                    <div class="ans-text">📌 정답: {item['answer']}</div>
                    <div style="color: #334155; line-height: 1.6;">
                        <strong>[상세 해설]</strong><br>{item['explanation'].replace(chr(10), '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 암기 공식 팁이 있는 경우
                if item.get("memo"):
                    st.markdown(f"""
                    <div class="tip-box">
                        <strong>💡 암기 공식 / 두문자 꿀팁</strong><br>
                        {item['memo'].replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 원자료 정정 안내가 있는 경우
                if item.get("correction"):
                    st.markdown(f"""
                    <div class="corr-box">
                        <strong>⚠️ [원자료 오류 정정]</strong><br>
                        {item['correction'].replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 탭 2: 커버리지 분석
# -------------------------------------------------------------
with tab_analysis:
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

# -------------------------------------------------------------
# 탭 3: 오류 정정표 & 보강 요약
# -------------------------------------------------------------
with tab_corrections:
    st.subheader("⚠️ 원자료 오류 정정표")
    st.info("원자료 영상 및 문제집에 포함된 오류 7가지를 올바른 법령·교재 기준으로 바로잡았습니다.")
    
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

    st.markdown("---")
    st.subheader("📌 보강 요약 (원자료 누락 빈출 영역)")
    st.markdown("""
    - **화재 분류·소화 원리**:
      - A급 일반(백색) / B급 유류(황색) / C급 전기(청색) / K급 주방(식용유) / D급 금속
      - 소화 4원리: 냉각, 질식(산소 15% 이하), 제거, 억제(부촉매 - 유일한 화학적)
      - 분말소화약제: 1종 백색(BC) / 2종 담회색(BC) / 3종 담홍색(ABC) / 4종 회색(BC)
      - 축압식 지시압력계 정상: 0.7~0.98MPa(녹색), 내용연수 10년
    - **자동화재탐지설비**:
      - 경계구역: 1개 면적 600㎡ 이하, 한 변 50m 이하 (내부 보이면 1,000㎡)
      - 2개 층 걸치지 않음 (합계 500㎡ 이하면 2개 층 가능)
      - 발신기: 수평거리 25m 이하, 높이 0.8~1.5m
    - **옥외소화전**: 350L/min, 0.25~0.7MPa, 수평거리 40m 이하
      - *암기 팁*: 옥내(130L·0.17) / 옥외(350L·0.25) / 스프링클러(80L·0.1)
    """)
