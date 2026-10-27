# pic-mun — 그림 문제 이미지 모음

1급 소방안전관리자 **그림·도면 문제**에 쓰이는 이미지를 모두 이 폴더에 모아 둡니다.

- 문제 본문·보기·정답·해설은 저장소 최상위 `questions_mcq.json` 에 있습니다. (각 문항의 `"image"` 필드가 이 폴더의 파일을 가리킴)
- 웹앱(`index.html`)과 Streamlit 앱(`app.py`) 모두 이 경로의 이미지를 표시합니다.
- 새 그림 문제를 추가할 때는 이미지를 이 폴더에 넣고 `"image": "pic-mun/파일명"` 으로 연결하세요.

## 기존 그림 문제 (6장, `q_*.png`)

| id | 파일 | 단원 | 교재 |
|---|---|---|---|
| 118 | q_gauge_state.png | 소화기구 – 지시압력계 정상 상태 | p.18 |
| 119 | q_gauge_explain.png | 소화기구 – 지시압력계 설명 | p.18 |
| 120 | q_extinguisher_check.png | 소화기구 – 소화기 점검 | p.20 |
| 121 | q_dialog_extinguisher.png | 소화기구 – 대화형 | p.22 |
| 122 | q_floor_plan_placement.png | 소화기구 – 평면도 배치 | p.25 |
| 123 | q_detector_count.png | 경보설비 – 감지기 개수 계산 | p.76 |

## 교재 2권에서 잘라 만든 그림 문제 (15장, `q_b2_*.jpg`)

| id | 파일 | 단원 – 주제 | 교재 2권 |
|---|---|---|---|
| 158 | q_b2_powder_extinguisher_structure.jpg | 소화기구 – 가압식/축압식 구조 | p.17 |
| 159 | q_b2_co2_weight_check.jpg | 소화기구 – CO₂소화기 중량 판정 (계산) | p.24~25 |
| 160 | q_b2_circulation_pipe.jpg | 옥내소화전 – 순환배관 | p.37 |
| 161 | q_b2_mcc_select_switch.jpg | 옥내소화전 – 동력제어반 선택스위치 | p.44 |
| 162 | q_b2_pump_test_valves.jpg | 펌프성능시험 – 체절운전 밸브 상태 | p.47~49 |
| 163 | q_b2_relief_valve_section.jpg | 펌프성능시험 – 릴리프밸브 조정 | p.38, 47~48 |
| 164 | q_b2_pump_curve.jpg | 펌프성능시험 – 성능곡선 (계산) | p.49~50 |
| 165 | q_b2_alarm_valve_pressure_switch.jpg | 스프링클러 – 알람밸브 리타딩챔버 | p.73~74 |
| 166 | q_b2_preaction_valve.jpg | 스프링클러 – 프리액션밸브 교차회로 | p.76~77 |
| 167 | q_b2_pressure_switch_range_diff.jpg | 스프링클러 – 압력스위치 RANGE/DIFF (계산) | p.79 |
| 168 | q_b2_gas_operation_sequence.jpg | 가스계 – 작동순서 | p.87 |
| 169 | q_b2_solenoid_safety_steps.jpg | 가스계 – 솔레노이드 안전조치 순서 | p.89 |
| 170 | q_b2_p_type_receiver_panel.jpg | 경보설비 – P형 수신기 복구 순서 | p.111~112 |
| 171 | q_b2_backup_power_test.jpg | 경보설비 – 예비전원시험 판정 | p.116 |
| 172 | q_b2_detector_types.jpg | 경보설비 – 감지기 종류 | p.101~102 |

※ `q_b2_*` 이미지는 한국소방안전원 교재(2권)에서 잘라낸 것이므로 개인 학습용으로만 사용하세요.
