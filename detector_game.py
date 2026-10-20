# -*- coding: utf-8 -*-
"""
소방 열감지기 기준면적 3-Step 매칭 게임 컴포넌트
(부착높이·구조 -> 감지기 종류 -> 기준면적 숫자 3연타 체인 암기)
"""

import streamlit as st
import streamlit.components.v1 as components
import os

def render_detector_game(height=780):
    """열감지기 기준면적 인터랙티브 매칭 게임 렌더링"""
    st.subheader("🔥 열감지기 기준면적 3-Step 체인 매칭 게임")
    st.caption("부착높이·구조 ➔ 감지기 종류 ➔ 기준면적(㎡)을 순서대로 선택하여 화재안전기준(NFPC 203) 수치를 완벽 정복하세요!")
    
    html_path = os.path.join(os.path.dirname(__file__), "detector_game.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=height, scrolling=True)
    else:
        st.error("detector_game.html 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    st.set_page_config(page_title="열감지기 게임", layout="wide")
    render_detector_game()
