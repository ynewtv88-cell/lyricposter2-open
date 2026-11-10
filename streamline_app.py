Claude























































Streamlit app
 · 
PY
import hashlib
import io
import os
 
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
 
# ------------------------------------------------------------
# 1) 연습용 가짜 차트 (나중에 Last.fm 진짜 차트로 바뀜)
# ------------------------------------------------------------
SAMPLE_CHART = [
    {"rank": 1, "title": "Blue Harbor", "artist": "The Paper Lanterns"},
    {"rank": 2, "title": "새벽 세 시", "artist": "달빛소년"},
    {"rank": 3, "title": "Neon Rain", "artist": "Mira Vale"},
    {"rank": 4, "title": "여름의 끝", "artist": "초록버스"},
    {"rank": 5, "title": "Golden Hour Drive", "artist": "Static Bloom"},
]
 
# ------------------------------------------------------------
# 2) 연습용 "그림 설명서" 3개 (나중에 Gemini가 대신 써줌)
# ------------------------------------------------------------
DEMO_BRIEFS = [
    {
        "summary": "밤바다처럼 고요하고 쓸쓸한 노래",
        "mood": ["고요함", "그리움", "밤"],
        "imagery": ["잔잔한 바다", "멀리 보이는 등대", "별빛"],
        "palette": ["#0B1D3A", "#1F4E79", "#7FB3D5", "#F4D35E"],
    },
    {
        "summary": "도시의 밤을 달리는 신나는 노래",
        "mood": ["설렘", "속도감", "자유"],
        "imagery": ["네온사인", "빗물에 비친 불빛", "빈 도로"],
        "palette": ["#1A0933", "#7B2CBF", "#FF4D9D", "#00F5D4"],
    },
    {
        "summary": "따뜻한 햇살 같은 포근한 노래",
        "mood": ["따뜻함", "희망", "여유"],
        "imagery": ["노을", "흔들리는 풀밭", "열린 창문"],
        "palette": ["#FFB347", "#FF7F50", "#FFD1A9", "#6B4226"],
    },
]
 
 
def make_demo_brief(title: str) -> dict:
    """곡 제목에 따라 설명서 3개 중 하나를 고른다 (같은 곡은 항상 같은 결과)."""
    number = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
    return DEMO_BRIEFS[number % len(DEMO_BRIEFS)]
 
 
# ------------------------------------------------------------
# 3) 연습용 포스터 그리기 (나중에 FLUX 그림 AI로 바뀜)
# ------------------------------------------------------------
FONT_PATHS = [
    "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",  # Streamlit Cloud (packages.txt)
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",           # 맥
    "C:/Windows/Fonts/malgunbd.ttf",                        # 윈도우
]
 
 
def load_font(size: int):
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)
 
 
def hex_to_rgb(color: str):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
 
 
def make_demo_poster(brief: dict, title: str, artist: str) -> bytes:
    width, height = 768, 1024
    colors = [hex_to_rgb(c) for c in brief["palette"]]
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
 
    # 위에서 아래로 색이 바뀌는 그라데이션
    sections = len(colors) - 1
    for y in range(height):
        position = y / (height - 1) * sections
        i = min(int(position), sections - 1)
        t = position - i
        c1, c2 = colors[i], colors[i + 1]
        row = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        draw.line([(0, y), (width, y)], fill=row)
 
    # 동그라미 장식
    for n, color in enumerate(colors):
        r = 220 - n * 40
        cx, cy = width // 2, 380
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=6)
 
    # 제목과 가수 이름 (진짜 글자로 얹기)
    draw.rectangle([0, height - 230, width, height], fill=(0, 0, 0))
    draw.text((48, height - 200), title, font=load_font(64), fill=(255, 255, 255))
    draw.text((48, height - 110), artist, font=load_font(36), fill=(200, 200, 200))
    draw.text((48, 40), "DEMO POSTER", font=load_font(24), fill=(255, 255, 255))
 
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
 
 
# ------------------------------------------------------------
# 4) 화면
# ------------------------------------------------------------
st.set_page_config(page_title="Lyric2Poster", page_icon="🎨")
st.title("🎨 Lyric2Poster")
st.caption("노래 가사로 포스터를 만들어요. (지금은 연습용 데모 모드)")
 
# 1단계: 곡 고르기
st.header("1. 노래 고르기")
options = [f'{s["rank"]}위 · {s["title"]} — {s["artist"]}' for s in SAMPLE_CHART]
options.append("직접 입력하기")
choice = st.selectbox("오늘의 차트 (연습용)", options)
 
if choice == "직접 입력하기":
    title = st.text_input("노래 제목")
    artist = st.text_input("가수")
else:
    song = SAMPLE_CHART[options.index(choice)]
    title, artist = song["title"], song["artist"]
 
# 2단계: 가사 넣고 설명서 만들기
st.header("2. 그림 설명서 만들기")
with st.form("lyrics_form", clear_on_submit=True):  # 제출하면 가사 칸이 비워짐
    lyrics = st.text_area("가사를 붙여넣으세요 (저장되지 않아요)", height=150)
    submitted = st.form_submit_button("설명서 만들기")
 
if submitted:
    if not title:
        st.warning("노래 제목을 먼저 입력해 주세요.")
    elif not lyrics.strip():
        st.warning("가사를 붙여넣어 주세요.")
    else:
        st.session_state["brief"] = make_demo_brief(title)
        st.session_state["song"] = (title, artist)
        st.session_state.pop("poster", None)
    del lyrics  # 가사는 여기서 바로 버림
 
brief = st.session_state.get("brief")
if brief:
    st.success(brief["summary"])
    st.write("**분위기:** " + ", ".join(brief["mood"]))
    st.write("**그림 요소:** " + ", ".join(brief["imagery"]))
    swatches = "".join(
        f'<span style="display:inline-block;width:40px;height:40px;'
        f'background:{c};margin-right:6px;border-radius:6px"></span>'
        for c in brief["palette"]
    )
    st.markdown(swatches, unsafe_allow_html=True)
 
    # 3단계: 포스터 만들기
    st.header("3. 포스터 만들기")
    if st.button("포스터 만들기"):
        song_title, song_artist = st.session_state["song"]
        st.session_state["poster"] = make_demo_poster(brief, song_title, song_artist)
 
    poster = st.session_state.get("poster")
    if poster:
        st.image(poster, caption="AI가 만든 이미지가 아닌 데모 포스터예요.")
        st.download_button("PNG 다운로드", poster, "poster.png", "image/png")
 
Claude가 응답을 완료했습니다
