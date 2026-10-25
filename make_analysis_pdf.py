# -*- coding: utf-8 -*-
"""
1급 소방안전관리자 시험 문제 분석 PDF 생성 스크립트
- 출력 위치: 1keub-pdf/시험 문제 분석.pdf
- 기술: PyMuPDF Drawing & Text API (한글 맑은 고딕 폰트)
"""

import os
import pymupdf

def build_pdf():
    doc = pymupdf.open()
    font_reg = "C:/Windows/Fonts/malgun.ttf"
    font_bold = "C:/Windows/Fonts/malgunbd.ttf"
    
    PAGE_W, PAGE_H = 595.3, 841.9 # A4
    MARGIN_X = 36.0
    CONTENT_W = PAGE_W - 2 * MARGIN_X
    
    current_page = None
    cur_y = 0.0
    page_num = 0

    def new_page():
        nonlocal current_page, cur_y, page_num
        current_page = doc.new_page(width=PAGE_W, height=PAGE_H)
        current_page.insert_font("malgun", font_reg)
        current_page.insert_font("malgunbd", font_bold)
        page_num += 1
        
        if page_num > 1:
            current_page.draw_rect(pymupdf.Rect(MARGIN_X, 22, MARGIN_X + CONTENT_W, 23), color=(0.85, 0.88, 0.92), fill=(0.85, 0.88, 0.92))
            current_page.insert_text((MARGIN_X, 18), "1급 소방안전관리자 과목별 시험 문제 출제 지도", fontname="malgun", fontsize=7.5, color=(0.4, 0.45, 0.5))
            current_page.insert_text((MARGIN_X + CONTENT_W - 30, 18), f"- {page_num} -", fontname="malgun", fontsize=7.5, color=(0.4, 0.45, 0.5))
            cur_y = 38.0
        else:
            cur_y = 28.0
            
    def ensure_space(height):
        nonlocal cur_y
        if cur_y + height > PAGE_H - 32.0:
            new_page()

    new_page()

    # 표지 헤더
    header_h = 76.0
    header_rect = pymupdf.Rect(MARGIN_X, cur_y, MARGIN_X + CONTENT_W, cur_y + header_h)
    current_page.draw_rect(header_rect, color=(0.06, 0.1, 0.22), fill=(0.06, 0.1, 0.22))
    
    # 뱃지
    badge_rect = pymupdf.Rect(MARGIN_X + 14, cur_y + 10, MARGIN_X + 155, cur_y + 24)
    current_page.draw_rect(badge_rect, color=(0.96, 0.62, 0.04), fill=(0.96, 0.62, 0.04))
    current_page.insert_text((MARGIN_X + 18, cur_y + 20), "★ 2026 합격 보장 핵심 로드맵", fontname="malgunbd", fontsize=8.0, color=(0.0, 0.0, 0.0))
    
    # 타이틀
    current_page.insert_text((MARGIN_X + 14, cur_y + 44), "1급 소방안전관리자 과목별 시험 문제 출제 지도", fontname="malgunbd", fontsize=15.0, color=(1.0, 1.0, 1.0))
    # 서브타이틀
    current_page.insert_text((MARGIN_X + 14, cur_y + 62), "1keub-pdf 교재 분권 파일별 [지문 격추] & [계산 도장] 완벽 총정리 및 수록 페이지 매핑", fontname="malgun", fontsize=8.5, color=(0.8, 0.85, 0.95))
    
    cur_y += header_h + 12.0

    def draw_section_header(title, is_vol2=False):
        nonlocal cur_y
        ensure_space(32)
        bg_col = (0.94, 0.98, 0.95) if is_vol2 else (0.94, 0.96, 0.99)
        bar_col = (0.02, 0.59, 0.41) if is_vol2 else (0.15, 0.39, 0.92)
        txt_col = (0.02, 0.4, 0.28) if is_vol2 else (0.08, 0.2, 0.55)
        
        rect = pymupdf.Rect(MARGIN_X, cur_y, MARGIN_X + CONTENT_W, cur_y + 22)
        current_page.draw_rect(rect, color=bg_col, fill=bg_col)
        bar_rect = pymupdf.Rect(MARGIN_X, cur_y, MARGIN_X + 5, cur_y + 22)
        current_page.draw_rect(bar_rect, color=bar_col, fill=bar_col)
        current_page.insert_text((MARGIN_X + 12, cur_y + 15), title, fontname="malgunbd", fontsize=10.5, color=txt_col)
        cur_y += 26.0

    def draw_card(title, file_name, items, page_info=None, is_vol2=False):
        nonlocal cur_y
        
        lines_count = sum(len(it.get('lines', [])) + 1 for it in items)
        calc_extra = sum(1 for it in items if 'formula' in it)
        est_h = 24 + (lines_count * 13) + (calc_extra * 16) + (18 if page_info else 0) + 12
        ensure_space(est_h)
        
        start_y = cur_y
        card_rect = pymupdf.Rect(MARGIN_X, cur_y, MARGIN_X + CONTENT_W, cur_y + est_h)
        current_page.draw_rect(card_rect, color=(0.88, 0.91, 0.94), fill=(1.0, 1.0, 1.0))
        
        hdr_rect = pymupdf.Rect(MARGIN_X, cur_y, MARGIN_X + CONTENT_W, cur_y + 20)
        current_page.draw_rect(hdr_rect, color=(0.96, 0.97, 0.98), fill=(0.96, 0.97, 0.98))
        current_page.draw_line((MARGIN_X, cur_y + 20), (MARGIN_X + CONTENT_W, cur_y + 20), color=(0.88, 0.91, 0.94))
        
        title_col = (0.02, 0.45, 0.32) if is_vol2 else (0.1, 0.25, 0.6)
        current_page.insert_text((MARGIN_X + 10, cur_y + 14), title, fontname="malgunbd", fontsize=9.2, color=title_col)
        
        f_badge_w = len(file_name) * 4.8 + 10
        f_rect = pymupdf.Rect(MARGIN_X + CONTENT_W - f_badge_w - 6, cur_y + 3, MARGIN_X + CONTENT_W - 6, cur_y + 17)
        current_page.draw_rect(f_rect, color=(0.9, 0.92, 0.95), fill=(0.9, 0.92, 0.95))
        current_page.insert_text((f_rect.x0 + 4, cur_y + 13), file_name, fontname="malgun", fontsize=7.2, color=(0.3, 0.35, 0.45))
        
        cur_y += 26.0

        for it in items:
            tag_type = it.get('type', 'shoot')
            tag_text = "[지문격추]" if tag_type == 'shoot' else "[계산도장]"
            tag_bg = (0.99, 0.9, 0.9) if tag_type == 'shoot' else (0.99, 0.94, 0.82)
            tag_fg = (0.75, 0.12, 0.12) if tag_type == 'shoot' else (0.7, 0.35, 0.05)
            
            tag_rect = pymupdf.Rect(MARGIN_X + 10, cur_y - 8, MARGIN_X + 62, cur_y + 4)
            current_page.draw_rect(tag_rect, color=tag_bg, fill=tag_bg)
            current_page.insert_text((tag_rect.x0 + 4, cur_y), tag_text, fontname="malgunbd", fontsize=7.0, color=tag_fg)
            
            current_page.insert_text((MARGIN_X + 68, cur_y), it['title'], fontname="malgunbd", fontsize=8.5, color=(0.1, 0.15, 0.25))
            cur_y += 13.0
            
            if 'formula' in it:
                f_box = pymupdf.Rect(MARGIN_X + 20, cur_y - 8, MARGIN_X + CONTENT_W - 14, cur_y + 6)
                current_page.draw_rect(f_box, color=(0.92, 0.95, 0.99), fill=(0.95, 0.97, 1.0))
                current_page.draw_line((f_box.x0, f_box.y0), (f_box.x0, f_box.y1), color=(0.23, 0.51, 0.96), width=2)
                current_page.insert_text((f_box.x0 + 6, cur_y + 1), it['formula'], fontname="malgunbd", fontsize=7.5, color=(0.12, 0.25, 0.55))
                cur_y += 16.0
                
            for line in it.get('lines', []):
                current_page.insert_text((MARGIN_X + 20, cur_y), line, fontname="malgun", fontsize=8.0, color=(0.25, 0.3, 0.4))
                cur_y += 12.0
            cur_y += 2.0

        if page_info:
            sep_y = cur_y + 2
            current_page.draw_line((MARGIN_X + 10, sep_y), (MARGIN_X + CONTENT_W - 10, sep_y), color=(0.9, 0.92, 0.95), width=0.8)
            current_page.insert_text((MARGIN_X + 12, sep_y + 11), f"▶ 교재 수록: {page_info}", fontname="malgunbd", fontsize=7.6, color=(0.15, 0.4, 0.75))
            cur_y = sep_y + 16.0
        else:
            cur_y += 4.0
            
        cur_y += 8.0

    # ==================== 제1권 ====================
    draw_section_header("[제1권] 소방관계법령 및 화재이론 (01편 ~ 08편)")
    
    # 01편
    draw_card(
        "【제1편】 소방안전관리제도",
        "01_제1편_소방안전관리제도_(p9-20).pdf",
        [
            {
                "type": "shoot",
                "title": "특급 / 1급 / 2급 / 3급 소방안전관리대상물 구분",
                "lines": [
                    "• 특급: 50층 이상 또는 200m 이상 아파트 / 지하층 포함 30층 이상 또는 120m 이상(연면적 20만㎡ 이상) 특정대상물",
                    "• 1급: 30층 이상 또는 120m 이상 아파트 / 연면적 1만5천㎡ 이상 특정소방대상물(아파트 제외)"
                ]
            },
            {
                "type": "shoot",
                "title": "선임 자격 및 실무 경력 연수 매칭",
                "lines": [
                    "• 특급: 소방기술사·관리사 즉시 / 기사 실무 5년 / 산업기사 실무 7년 / 소방공무원 20년 이상",
                    "• 1급: 소방설비기사·산업기사 즉시 / 소방공무원 7년 / 2급 자격 취득 후 실무경력 5년 이상"
                ]
            },
            {
                "type": "calc",
                "title": "소방안전관리보조자 최소 선임 인원수 계산",
                "formula": "공식: 아파트 -> 300세대마다 1명 추가 | 일반대상물 -> 연면적 15,000㎡마다 1명 추가 (아파트 제외)",
                "lines": [
                    "• 예시: 1,500세대 아파트 = 기본 1명(300세대) + 추가 4명(1,200세대÷300) = [총 5명 도장]",
                    "• 숙박·수련시설 바닥면적 1,500㎡ 이상(1,000㎡ 함정 주의), 노유자·기숙사 1,000㎡ 이상"
                ]
            }
        ],
        page_info="순수 제도 및 선임기준 단원 (단원 마무리 문제 없음)"
    )

    # 02편
    draw_card(
        "【제2편】 소방관계법령 (소방기본법 · 화재예방법 · 소방시설법 등)",
        "02_제2편_소방관계법령_(p21-122).pdf",
        [
            {
                "type": "shoot",
                "title": "법정 벌칙 vs 과태료 한판 격추",
                "lines": [
                    "• 소방안전관리자 미선임 -> [300만원 이하 벌금 (형벌/전과)] (지연신고/거짓신고는 200만원 과태료)",
                    "• 피난시설, 방화구획 폐쇄·훼손·변경 행위 -> [300만원 이하 과태료] (1차 100만 / 2차 200만 / 3차 300만)",
                    "• 소방활동구역 무단 출입 -> [200만원 이하 과태료] | 비밀 누설 -> [300만원 이하 벌금]",
                    "• 출동 소방차 통행 방해 또는 대원 폭행 -> [5년 이하 징역 또는 5천만원 벌금 (최고형벌)]"
                ]
            },
            {
                "type": "shoot",
                "title": "★시험장 최다 함정: 법정 기한 및 일수(숫자) 매칭",
                "lines": [
                    "• 관리자 선임: 사유발생일 30일 이내 | 선임신고: 선임일로부터 14일 이내 (선임 30일 vs 신고 14일!)",
                    "• 점검결과보고서 관서 제출: 15일 이내 | 점검기록표 게시: 즉시 (30일 이상 출입자 게시)",
                    "• 건축허가등의 동의 회신: 5일 이내 (특급은 10일 이내, 보완 시 4일 범위 1회 연장)"
                ]
            }
        ],
        page_info="교재 수록 문제: 35쪽(기본법), 73쪽(시설법), 83쪽(다중법), 92쪽(초고층), 102쪽(재난법), 121쪽(위험물법)"
    )

    # 03편
    draw_card(
        "【제3편】 건축관계법령 (건축법 · 피난방화시설)",
        "03_제3편_건축관계법령_(p123-172).pdf",
        [
            {
                "type": "shoot",
                "title": "건축 구조 및 방화문 등급 구분",
                "lines": [
                    "• 주요구조부 6가지: 바·지·보·주·계·내 (바닥, 지붕틀, 보, 주계단, 내력벽, 기둥) [사이기둥, 옥외계단, 최하층바닥 제외!]",
                    "• 60분+ 방화문: 차열 30분 + 비차열 60분 이상 | 60분 방화문: 비차열 60분 이상 | 30분 방화문: 비차열 30분 이상"
                ]
            },
            {
                "type": "calc",
                "title": "방화구획 층수별 설치 면적 기준 계산",
                "formula": "10층 이하: 1,000㎡마다 | 11층 이상: 200㎡(불연내장 시 500㎡)마다 | 스프링클러 설치 시 기준 면적 3배 완화!",
                "lines": [
                    "• 예시: 11층 이상 층에 불연내장재 시공 + 스프링클러 전면 설치 = 500㎡ × 3배 = [1,500㎡ 도장]"
                ]
            }
        ],
        page_info="교재 수록 문제: 151쪽 ~ 152쪽 (건축관계법령 종합 2쪽 분량)"
    )

    # 04편 & 05편
    draw_card(
        "【제4편】 소방학개론 & 【제5편】 위험물·전기·가스안전관리",
        "04_제4편_(p173-198) · 05_제5편_(p199-212).pdf",
        [
            {
                "type": "shoot",
                "title": "화재 분류(A/B/C/D/K) 및 소화 4대 원리",
                "lines": [
                    "• 화재 분류: A급(일반-백색), B급(유류-황색), C급(전기-청색), D급(금속-무색/건조사), K급(주방-비누화 반응)",
                    "• 소화 원리: 냉각(물), 질식(CO2, 산소 15% 이하), 제거(가연물 격리), 억제/부촉매(할론, 할로겐화합물)"
                ]
            },
            {
                "type": "shoot",
                "title": "제1류 ~ 제6류 위험물 유별 성질 매칭",
                "lines": [
                    "• 1류(산화성 고체), 2류(가연성 고체), 3류(자연발화 및 금수성), 4류(인화성 액체), 5류(자기반응성), 6류(산화성 액체)"
                ]
            },
            {
                "type": "calc",
                "title": "★킬러 문항: 제4류 위험물 품명별 지정수량 및 배수 합산 계산",
                "formula": "특수 50L | 1석유 비수용 200L(수용 400L) | 알코올 400L | 2석유 비수용 1,000L(수용 2,000L) | 3석유 2,000L(수용 4,000L) | 4석유 6,000L",
                "lines": [
                    "• 예시: 톨루엔 400L(1석 비수용) + 아세톤 800L(1석 수용) + 경유 3,000L(2석 비수용) = 2.0 + 2.0 + 3.0 = [7.0배 도장]",
                    "• 판정: 품명별 배수의 합계가 1.0 이상이면 위험물안전관리법상 허가 대상 제조소등에 해당"
                ]
            }
        ],
        page_info="교재 수록 문제: 197쪽 (제4편 소방학개론), 212쪽 (제5편 위험물·전기·가스)"
    )

    # 06편, 07편, 08편
    draw_card(
        "【제6편 ~ 제8편】 공사장 안전관리 · 종합방재실 · 응급처치",
        "06_제6편 · 07_제7편 · 08_제8편_(p213-276).pdf",
        [
            {
                "type": "shoot",
                "title": "공사장 화기취급 및 잔류불씨 감시 (제6편)",
                "lines": [
                    "• 소화기 5m 이내 비치, 가연물 10m 이내 제거 또는 방호조치 | 작업 종료 후 [최소 30분 이상] 잔류불씨 감시 의무"
                ]
            },
            {
                "type": "shoot",
                "title": "종합방재실 설치 위치 및 면적 기준 (제7편 - 1급 전용)",
                "lines": [
                    "• 설치 위치: [1층 또는 피난층] (예외: 특별피난계단 출입구 5m 이내 시 2층 또는 지하 1층 허용)",
                    "• 바닥면적: 최소 [20㎡ 이상] 확보"
                ]
            },
            {
                "type": "shoot",
                "title": "심폐소생술(CPR) 및 자동심장충격기(AED) 프로토콜 (제8편)",
                "lines": [
                    "• 가슴압박 : 인공호흡 = [30 : 2] (속도 분당 100~120회, 깊이 약 5cm, 중단 시간 10초 이내)",
                    "• AED 패드 부착: [우측 쇄골(빗장뼈) 아래] + [좌측 젖꼭지 아래 겨드랑이선] | 심장충격 버튼 시 접촉 금지"
                ]
            }
        ],
        page_info="교재 수록 문제: 254쪽 (제7편 종합방재실), 270쪽 (제8편 응급처치)"
    )

    # ==================== 제2권 ====================
    draw_section_header("[제2권] 소방시설 구조점검 및 실무 (10편 ~ 15편)", is_vol2=True)

    # 10편 & 11편
    draw_card(
        "【제1편】 소방시설의 구조·점검 및 핵심 계산 (★시험 고득점 킬러)",
        "10_2권_제1편-1 · 11_2권_제1편-2_(p9-174).pdf",
        [
            {
                "type": "shoot",
                "title": "5대 소방시설 분류 & 소화기구 점검",
                "lines": [
                    "• 소화활동설비 6종: 제·연·송·용·콘·무 (제연, 연결송수관, 연결살수, 연소방지, 비상콘센트, 무선통신보조)",
                    "• 피난구조설비 4종: 피·인·유·비 (피난기구, 인명구조기구[방열·방화복/공기호흡기/인공소생기], 유도등, 비상조명등)",
                    "• 축압식 소화기 압력계: [녹색 정상 범위 0.7 ~ 0.98 MPa] | 보행거리: 소형 20m, 대형 30m 이내 배치"
                ]
            },
            {
                "type": "calc",
                "title": "옥내소화전 & 스프링클러 수원 저수량 계산",
                "formula": "옥내: N(최대 2개) × 2.6㎥ (30층 이상: N × 5.2㎥) | 스프링클러: 기준개수(아파트 10개) × 1.6㎥ = 16㎥",
                "lines": [
                    "• 예시: 15층 건물 층별 소화전 3개 -> 최대 2개 적용 = 2 × 2.6㎥ = [5.2 ㎥ 도장] (방수압 0.17 MPa, 방수량 130 L/min)",
                    "• 스프링클러 헤드 선단 방수압력 0.1 MPa 이상, 방수량 80 L/min 이상"
                ]
            },
            {
                "type": "shoot",
                "title": "소화펌프 성능시험 3단계 판정 기준",
                "lines": [
                    "• 체절운전(토출밸브 차단): 토출압력이 정격토출압력의 [140% 이하] | 릴리프 밸브는 [체절압력 미만]에서 개방",
                    "• 정격부하운전(정격 100% 방출): 정격토출압력의 [100% 이상] | 피크부하운전(150% 유량): 정격토출압력의 [65% 이상]"
                ]
            },
            {
                "type": "calc",
                "title": "화재감지기 설치 개수 & 수용인원 계산",
                "formula": "감지기: 바닥면적 ÷ 부착높이별 기준면적 (올림) | 수용인원: 강의실 1.9, 강당 4.6, 침대없는숙박 종사자+(면적÷3) (반올림)",
                "lines": [
                    "• 예시: 면적 200㎡, 높이 4m, 내화구조 거실 차동식 2종 = 200 ÷ 35 = 5.71개 -> [최소 6개 도장] (높이 4m 함정 주의)",
                    "• 경계구역 산정: 1개 구역 600㎡ 이하, 한 변의 길이 50m 이하 (출입구에서 내부 전체 보일 시 1,000㎡ 이하)"
                ]
            }
        ],
        page_info="교재 수록 문제: 170쪽 ~ 173쪽 (소방시설 1~9장 통합 학습평가 4쪽 연속)",
        is_vol2=True
    )

    # 12편 ~ 14편
    draw_card(
        "【제2편 ~ 제4편】 소방계획 수립 · 교육훈련 · 자체점검 실무",
        "12_2권_제2편 · 13_2권_제3편 · 14_2권_제4편_(p175-336).pdf",
        [
            {
                "type": "shoot",
                "title": "소방계획서 작성 3대 원칙 & 자위소방대 편성 (제2편)",
                "lines": [
                    "• 3대 원칙: 종합적 안전관리, 실현 가능성(최우선 평가), 관계인의 참여",
                    "• 자위소방대 4대 핵심 활동팀: [비상연락팀 / 초기소화팀 / 피난유도팀 / 응급구조팀]",
                    "• 초기대응체계 비상상주자: 야간·휴일에도 방재실, 경비실에 상시 상주하여 초동조치 가능한 인력"
                ]
            },
            {
                "type": "shoot",
                "title": "소방안전 교육 및 훈련 기준 (제3편)",
                "lines": [
                    "• 실시 주기: [연 1회 이상] (소방서장이 필요하다고 인정 시 2회 범위 내 추가 요청 가능)",
                    "• 훈련 결과 관서 제출 대상: [특급 및 1급 소방안전관리대상물] (훈련 종료 후 30일 이내)"
                ]
            },
            {
                "type": "shoot",
                "title": "자체점검(작동점검 vs 종합점검) 구분 및 실시 시기 (제4편)",
                "lines": [
                    "• 종합점검 대상: [스프링클러설비 설치 대상(면적 무관 무조건)], 물분무등 5,000㎡ 이상, 다중이용업소 2,000㎡ 이상",
                    "• 점검 시기 기준일: 완공일(X)이 아니라 건축물 [사용승인일]이 속하는 달에 실시!",
                    "• 점검결과보고서 제출 기한: 점검을 마친 날부터 [15일 이내]에 관할 소방서장에게 제출"
                ]
            }
        ],
        page_info="교재 수록 문제: 282쪽 (제2편 소방계획 수립), 313쪽 (제3편 소방안전교육 및 훈련)",
        is_vol2=True
    )

    # 부록
    draw_card(
        "【부록】 교재 분권 파일 전체 목차 & 학습평가(18쪽) 연계 안내",
        "15_2권_부록_소방계획서및훈련시나리오참고자료_(p337-376).pdf",
        [
            {
                "type": "shoot",
                "title": "학습평가 단권화 모음 및 데이터 파일 안내",
                "lines": [
                    "• 교재 내 수록된 18개 학습평가 문제는 '1keub-pdf/교재_학습평가_18제_모음.pdf'에서 단권으로 즉시 학습 가능합니다.",
                    "• 앱 연동용 JSON 메타데이터: 'quiz_page_mapping.json' | 전체 상세 색인표: '교재_학습평가_색인.md'"
                ]
            }
        ],
        page_info="소방계획서 및 훈련 시나리오 표준 서식 참고자료",
        is_vol2=True
    )

    out_path = os.path.join("1keub-pdf", "시험 문제 분석.pdf")
    doc.save(out_path, deflate=True)
    print(f"PDF 저장 완료: {out_path} (총 {len(doc)}페이지)")

if __name__ == "__main__":
    build_pdf()
