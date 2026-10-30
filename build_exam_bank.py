"""모의고사용 문제은행(exam_bank.json) 생성 스크립트.

기존 문제 4종(questions_mcq / questions_box / cards_75 / calc_37)을 하나의 형식으로 모으고,
실제 시험 구성(1과목 25문항 + 2과목 25문항)에 맞춰 과목·영역을 자동 분류한다.

실행: python build_exam_bank.py
문제를 추가·수정한 뒤에는 이 스크립트를 다시 실행해 exam_bank.json 을 갱신한다.
"""
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT: Path = Path(__file__).resolve().parent
OUT_PATH: Path = ROOT / "exam_bank.json"

# 영역 코드 → (과목, 영역 이름). exam.html 의 출제 기준표와 같은 코드를 쓴다.
AREAS: dict[str, tuple[int, str]] = {
    "A1": (1, "소방안전관리제도·소방관계법령"),
    "A2": (1, "건축관계법령·피난/방화시설"),
    "A3": (1, "소방학개론(연소·화재·소화)"),
    "A4": (1, "위험물·전기·가스 안전관리"),
    "A5": (1, "공사장·화기취급·종합방재실"),
    "A6": (1, "소방시설의 종류·구조·기준"),
    "B1": (2, "소방시설 점검·실습"),
    "B2": (2, "소방계획·자위소방대·교육훈련·응급처치"),
}

# 소방시설 문제 중 '점검·실습'(2과목)으로 보낼 단서
INSPECT_RE: re.Pattern[str] = re.compile(
    r"점검|시험|복구|측정|판정|실습|조작|세팅|격발|도통|지시압력계|이상 원인|고장|불량|"
    r"확인 순서|작동 순서|체절|정격|성능곡선|압력스위치|그림"
)


def norm_text(s: str) -> str:
    """중복 판별용 정규화: 공백·기호 제거."""
    return re.sub(r"[\s\W_]+", "", s)[:60]


def strip_option(o: str) -> str:
    """보기 앞의 '① ', '1. ' 같은 번호를 지운다(화면에서 다시 붙이므로)."""
    return re.sub(r"^\s*(?:[①②③④]|[1-4][\.\)])\s*", "", o).strip()


def facility_area(text: str, has_image: bool) -> str:
    """소방시설 문제를 구조(1과목) / 점검(2과목)으로 나눈다."""
    return "B1" if has_image or INSPECT_RE.search(text) else "A6"


def classify_mcq(q: dict[str, Any]) -> str:
    """questions_mcq / questions_box 의 part·chapter·subject 로 영역을 정한다."""
    meta = f"{q.get('book', '')} {q.get('part', '')} {q.get('chapter', '')} {q.get('subject', '')}"
    body = f"{q.get('question', '')} {' '.join(q.get('box', []))}"
    # '소화기'에도 '화기'가 들어 있으므로 화기취급은 구체적인 낱말로만 판별한다
    if re.search(r"화기취급|화기 취급|화기작업|용접|용단|비화기|공사장|방재실|특수가연물", meta + body):
        return "A5"
    if re.search(r"소방계획|자위소방대|교육|훈련|응급|심폐|피난계획", meta):
        return "B2"
    if re.search(r"점검표|점검 실습|점검실습|펌프성능|서식|점검실무", meta):
        return "B1"
    if re.search(r"건축|피난방화|방화구획", meta):
        return "A2"
    if re.search(r"소방학개론|화재이론|연소|소화이론", meta):
        return "A3"
    if re.search(r"제5편 위험물|전기|가스안전", meta):
        return "A4"
    if re.search(r"소방시설|설비|소화기구|경보|피난구조|제연|방염", meta):
        # 법령 편에 있는 위험물법 등은 위에서 걸러지지 않으므로 여기서 시설로 판단
        if re.search(r"관계법령|법$|법률", meta) and not re.search(r"설비", meta):
            return "A1"
        return facility_area(body, bool(q.get("image")))
    return "A1"


CARD_AREA: dict[str, str] = {
    "01": "A1", "02": "A1", "03": "A1", "04": "A1",
    "05": "A2", "06": "A3", "07": "A4", "11": "B2",
}


def classify_card(q: dict[str, Any]) -> str:
    """cards_75 는 chapter_id 로 분류한다."""
    cid = q["chapter_id"]
    if cid in CARD_AREA:
        return CARD_AREA[cid]
    if cid == "10":
        return "A5" if re.search(r"화기|Cool|비화기", q["question"]) else "B2"
    return facility_area(q["question"], False)  # 08 소화설비, 09 경보·피난·소화활동


CALC_AREA: dict[str, str] = {
    "01": "A1", "08": "A1",  # 인원 계산, 기한 계산
    "05": "A2",              # 방화구획·건폐율·용적률
    "07": "A4",              # 위험물 지정수량 배수
    "02": "A6", "03": "A6", "04": "A6",  # 소화기·감지기·유도등 개수(설치 기준)
    "06": "B1",              # 수계설비·펌프 성능
}


def make_item(src: str, q: dict[str, Any], area: str) -> dict[str, Any]:
    """공통 형식으로 변환한다."""
    box: list[str] = q.get("box") or []
    if len(box) == 3:
        qtype = "box3"   # 가·나·다 고르기
    elif len(box) >= 4:
        qtype = "box4"   # 가·나·다·라 고르기
    else:
        qtype = "mcq"    # 일반 4지선다
    subject, area_name = AREAS[area]
    return {
        "uid": f"{src}:{q['id']}",
        "source": src,
        "subject": subject,
        "area": area,
        "area_name": area_name,
        "type": qtype,
        "question": q["question"].strip(),
        "box": box,
        "options": [strip_option(o) for o in q["options"]],
        "answer": int(q["answer"]),
        "explanation": q.get("explanation", ""),
        "trap_tip": q.get("trap_tip", ""),
        "image": q.get("image", ""),
        "page_ref": q.get("page_ref", "") or q.get("title", ""),
    }


def load(name: str) -> list[dict[str, Any]]:
    with open(ROOT / name, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    bank: list[dict[str, Any]] = []
    for q in load("questions_mcq.json"):
        bank.append(make_item("mcq", q, classify_mcq(q)))
    for q in load("questions_box.json"):
        bank.append(make_item("box", q, classify_mcq(q)))
    for q in load("cards_75.json"):
        if q.get("is_duplicate"):
            continue  # 다른 세트와 겹친다고 표시된 문항은 제외
        bank.append(make_item("card", q, classify_card(q)))
    for q in load("calc_37.json"):
        bank.append(make_item("calc", q, CALC_AREA.get(q["type_id"], "A1")))

    # 지문이 사실상 같은 문제는 하나만 남긴다
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in bank:
        key = norm_text(item["question"]) + norm_text("".join(item["options"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    # 기본 검증: 보기 4개, 정답 1~4
    for item in unique:
        assert len(item["options"]) == 4 and 1 <= item["answer"] <= 4, item["uid"]

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=1)

    # 영역·유형별 보유 문항 수 보고
    print(f"문제은행 {len(unique)}문항 (중복 {len(bank) - len(unique)}개 제외) → {OUT_PATH.name}")
    by_area = Counter((i["area"], i["type"]) for i in unique)
    for code, (subj, name) in AREAS.items():
        cnt = {t: by_area[(code, t)] for t in ("mcq", "box3", "box4")}
        print(f"  {subj}과목 {code} {name}: 일반 {cnt['mcq']} / 가나다 {cnt['box3']} / 가나다라 {cnt['box4']}")


if __name__ == "__main__":
    main()
