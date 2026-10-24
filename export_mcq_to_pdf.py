# -*- coding: utf-8 -*-
"""
소방안전관리자 1급 4지선다 117문항 PDF 생성 및 다운로드 폴더 전송 스크립트
- HTML 기반 고품질 렌더링 + Microsoft Edge Headless PDF 인쇄
"""

import json
import os
import base64
import subprocess
from pathlib import Path

def generate_pdf():
    # 1. 문제 데이터 로드
    with open("questions_mcq.json", "r", encoding="utf-8") as f:
        all_questions = json.load(f)

    # 70점 안전빵 모드 필터링 (지엽킬러 제외 -> 117문항)
    questions = [q for q in all_questions if q.get("difficulty") != "지엽킬러"]
    print(f"총 {len(questions)}문항 대상 PDF 생성 시작...")

    # 2. 이미지 base64 인코딩 함수
    def get_img_base64(img_path):
        if img_path and os.path.exists(img_path):
            with open(img_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                ext = Path(img_path).suffix.lstrip(".").lower()
                mime = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
                return f"data:{mime};base64,{b64}"
        return None

    # 3. HTML 템플릿 작성
    cards_html = []
    for idx, q in enumerate(questions, 1):
        q_id = q.get("id", idx)
        book = q.get("book", "")
        chapter = q.get("chapter", "")
        difficulty = q.get("difficulty", "기본형")
        date = q.get("date", "")
        question_text = q.get("question", "").replace("\n", "<br>")
        
        # 이미지 태그
        img_html = ""
        img_src = get_img_base64(q.get("image"))
        if img_src:
            img_html = f'<div class="q-img-wrap"><img src="{img_src}" class="q-img"></div>'

        # 보기 목록
        opts = q.get("options", [])
        opts_html = []
        for o_idx, opt in enumerate(opts, 1):
            is_correct = (o_idx == q.get("answer"))
            correct_badge = ' <span class="ans-mark">✔ 정답</span>' if is_correct else ''
            opt_class = 'option-item correct-opt' if is_correct else 'option-item'
            opts_html.append(f'<div class="{opt_class}"><span class="opt-num">{'①②③④'[o_idx-1]}</span> {opt}{correct_badge}</div>')
        opts_joined = "".join(opts_html)

        # 해설 및 함정 팁
        ans_num = q.get("answer", "")
        explanation = q.get("explanation", "").replace("\n", "<br>")
        trap_tip = q.get("trap_tip", "")
        trap_html = f'<div class="trap-box"><strong>⚠️ 시험장 함정 팁:</strong> {trap_tip}</div>' if trap_tip else ""

        card_str = f"""
        <div class="question-block">
            <div class="q-header">
                <div class="q-title-line">
                    <span class="q-badge">Q{idx:03d}</span>
                    <span class="q-title">{question_text}</span>
                </div>
                <div class="q-meta">
                    <span class="meta-tag">{book} &gt; {chapter}</span>
                    <span class="meta-tag">📅 {date}</span>
                    <span class="meta-tag diff-{difficulty}">난이도: {difficulty}</span>
                </div>
            </div>
            {img_html}
            <div class="options-container">
                {opts_joined}
            </div>
            <div class="solution-box">
                <div class="sol-header">📌 <strong>정답: {ans_num}번</strong></div>
                <div class="sol-body"><strong>💡 상세 해설:</strong> {explanation}</div>
                {trap_html}
            </div>
        </div>
        """
        cards_html.append(card_str)

    all_cards_str = "\n".join(cards_html)

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>1급 소방안전관리자 실전 4지선다 기출·응용 117제</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm 12mm 15mm 12mm;
            @bottom-center {{
                content: counter(page);
                font-size: 9pt;
                color: #64748b;
            }}
        }}
        body {{
            font-family: "Malgun Gothic", "맑은 고딕", Dotum, sans-serif;
            color: #1e293b;
            line-height: 1.5;
            margin: 0;
            padding: 0;
            background: #ffffff;
            font-size: 10pt;
        }}
        .cover-page {{
            text-align: center;
            padding-top: 140px;
            page-break-after: always;
        }}
        .cover-badge {{
            display: inline-block;
            background: #fee2e2;
            color: #dc2626;
            font-size: 14pt;
            font-weight: bold;
            padding: 8px 18px;
            border-radius: 20px;
            margin-bottom: 25px;
        }}
        .cover-title {{
            font-size: 28pt;
            font-weight: 900;
            color: #0f172a;
            line-height: 1.3;
            margin-bottom: 15px;
        }}
        .cover-subtitle {{
            font-size: 14pt;
            color: #475569;
            margin-bottom: 50px;
        }}
        .cover-info-box {{
            width: 70%;
            margin: 0 auto;
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 12px;
            padding: 25px;
            text-align: left;
            font-size: 11pt;
            line-height: 1.8;
        }}
        .question-block {{
            page-break-inside: avoid;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }}
        .q-header {{
            margin-bottom: 10px;
        }}
        .q-title-line {{
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 6px;
        }}
        .q-badge {{
            background: #2563eb;
            color: white;
            font-size: 9pt;
            font-weight: bold;
            padding: 2px 7px;
            border-radius: 4px;
            white-space: nowrap;
        }}
        .q-title {{
            font-size: 11pt;
            font-weight: bold;
            color: #0f172a;
            flex-grow: 1;
        }}
        .q-meta {{
            font-size: 8.5pt;
            color: #64748b;
            display: flex;
            gap: 10px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 6px;
        }}
        .meta-tag {{
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        .q-img-wrap {{
            text-align: center;
            margin: 10px 0;
        }}
        .q-img {{
            max-width: 320px;
            max-height: 220px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
        }}
        .options-container {{
            margin: 8px 0 12px 0;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }}
        .option-item {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            padding: 7px 10px;
            font-size: 9.5pt;
            line-height: 1.4;
        }}
        .correct-opt {{
            background: #f0fdf4;
            border-color: #86efac;
            color: #166534;
            font-weight: bold;
        }}
        .opt-num {{
            font-weight: bold;
            margin-right: 4px;
        }}
        .ans-mark {{
            font-size: 8pt;
            background: #22c55e;
            color: white;
            padding: 1px 5px;
            border-radius: 3px;
            margin-left: 5px;
        }}
        .solution-box {{
            background: #f0fdf4;
            border-left: 4px solid #16a34a;
            border-radius: 4px;
            padding: 10px 12px;
            font-size: 9pt;
            line-height: 1.5;
        }}
        .sol-header {{
            font-size: 10pt;
            color: #15803d;
            margin-bottom: 4px;
        }}
        .sol-body {{
            color: #334155;
            margin-bottom: 6px;
        }}
        .trap-box {{
            background: #fffbeb;
            border: 1px solid #fde68a;
            border-radius: 4px;
            padding: 6px 10px;
            color: #92400e;
            font-size: 8.5pt;
        }}
    </style>
</head>
<body>
    <div class="cover-page">
        <div class="cover-badge">🛡️ 합격 보장 핵심 교재</div>
        <div class="cover-title">1급 소방안전관리자<br>실전 4지선다 기출·응용 117제</div>
        <div class="cover-subtitle">70점 안전합격 모드 엄선 문제집 + 상세 해설집</div>
        <div class="cover-info-box">
            • <strong>수록 문항수</strong>: 총 117문항 (지엽 킬러 제외, 실전 출제 중심)<br>
            • <strong>주요 특징</strong>: 실전 사진/도면 문항 수록, 4지선다 보기 완벽 정리<br>
            • <strong>해설 수록</strong>: 전 문항 정답 번호, 상세 원리 해설, 시험장 함정 팁 포함<br>
            • <strong>출처</strong>: https://sobang.streamlit.app/
        </div>
    </div>

    {all_cards_str}
</body>
</html>
"""

    temp_html_path = os.path.abspath("temp_export_117.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"HTML 임시 파일 생성 완료: {temp_html_path}")

    output_pdf_name = "소방안전관리자1급_실전4지선다_117제.pdf"
    local_pdf_path = Path(output_pdf_name)

    # 5. Microsoft Edge Headless를 통한 고품질 PDF 인쇄
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(local_pdf_path.resolve())}",
        f"file:///{temp_html_path.replace(os.sep, '/')}"
    ]

    print("Edge Headless PDF 생성 명령 실행 중...")
    subprocess.run(cmd, check=True)
    
    if local_pdf_path.exists() and local_pdf_path.stat().st_size > 0:
        size_kb = local_pdf_path.stat().st_size // 1024
        print(f"로컬 PDF 생성 성공: {local_pdf_path.resolve()} ({size_kb} KB)")
        
        # 다운로드 폴더로 복사
        downloads_dir = Path(os.environ["USERPROFILE"]) / "Downloads"
        target_path = downloads_dir / output_pdf_name
        import shutil
        shutil.copy2(local_pdf_path, target_path)
        print(f"다운로드 폴더 복사 완료: {target_path}")
    else:
        print("PDF 생성 실패")

if __name__ == "__main__":
    generate_pdf()

