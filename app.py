"""5さいの ひらがなれんしゅうアプリ。

問題は data フォルダの CSV / JSON から読み込みます。
images フォルダに画像を置くと、絵文字の代わりに自動で表示します。
"""

from __future__ import annotations

import base64
import csv
import json
import random
from pathlib import Path

import streamlit as st


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = BASE_DIR / "images"

st.set_page_config(
    page_title="ひらがな たんけんたい",
    page_icon="🌈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# iPhone の縦画面でも押しやすい、大きなボタン中心の見た目です。
st.markdown(
    """
    <style>
    :root {
      --ink:#453c53; --pink:#ff6f91; --yellow:#ffd166;
      --mint:#83dcc6; --blue:#79b8ff; --paper:#fffdf7;
    }
    .stApp {
      background:
        radial-gradient(circle at 8% 4%, #fff2a8 0 4rem, transparent 4.1rem),
        radial-gradient(circle at 96% 16%, #c9f4e8 0 5rem, transparent 5.1rem),
        linear-gradient(180deg, #fff9ed, #f7fbff);
      color:var(--ink);
    }
    .block-container {max-width:680px; padding:.35rem .7rem 1.5rem;}
    h1,h2,h3,p {text-align:center; color:var(--ink);}
    h1 {font-size:clamp(1.8rem,8vw,2.7rem); margin:.1rem 0;}
    h2 {font-size:clamp(1.25rem,5vw,1.7rem); margin:.12rem 0;}
    h3 {font-size:clamp(1.12rem,4.8vw,1.45rem)!important; margin:.1rem 0 .2rem!important;}
    div.stButton > button {
      width:100%; min-height:52px; border-radius:16px; border:3px solid #fff;
      box-shadow:0 5px 0 rgba(69,60,83,.16); font-size:1.28rem;
      font-weight:800; color:var(--ink); background:#fff;
      touch-action:manipulation;
    }
    div.stButton > button:active {transform:translateY(3px); box-shadow:0 2px 0 rgba(69,60,83,.16);}
    div[data-testid="stHorizontalBlock"] {
      display:flex!important; flex-direction:row!important;
      flex-wrap:nowrap!important; gap:.35rem;
    }
    div[data-testid="stHorizontalBlock"] > div {min-width:0!important; flex:1 1 0!important;}
    .picture {
      display:flex; justify-content:center; align-items:center; min-height:180px;
      font-size:7rem; background:#fff; border:5px solid #ffd166;
      border-radius:32px; box-shadow:0 8px 24px rgba(90,80,100,.10);
      margin:.2rem 0 .45rem;
    }
    .answer-slots {display:flex; justify-content:center; gap:.4rem; margin:.3rem 0 .45rem;}
    .slot {
      width:3.5rem; height:3.8rem; display:flex; align-items:center; justify-content:center;
      background:#fff; border:4px dashed #79b8ff; border-radius:15px;
      font-size:2rem; font-weight:900;
    }
    .slot.filled {border-style:solid; background:#eef7ff;}
    .message {padding:1rem; border-radius:22px; text-align:center; font-size:1.45rem; font-weight:900;}
    .good {background:#fff2a8; border:4px solid #ffd166;}
    .try {background:#eef7ff; border:4px solid #a8d5ff;}
    .selected-card {border:5px solid #ff6f91!important; background:#fff0f5!important;}
    .mini-card {
      min-height:95px; background:#fff; border:3px solid #dcecff; border-radius:20px;
      display:flex; flex-direction:column; justify-content:center; align-items:center;
      font-size:2.6rem; font-weight:800; text-align:center; padding:.3rem;
    }
    .mini-card img {width:100%; aspect-ratio:1; object-fit:contain; border-radius:14px;}
    .mini-card small {font-size:1rem;}
    .box {
      min-height:52px; background:#fff; border:3px dashed #83dcc6;
      border-radius:18px; padding:.3rem; text-align:center; font-size:1.5rem;
      overflow-wrap:anywhere;
    }
    .box img {width:29%; aspect-ratio:1; object-fit:contain; border-radius:8px; margin:.08rem;}
    [data-testid="stImage"] img {max-height:115px; object-fit:contain;}
    div[class*="st-key-pick_"] button {
      min-height:108px; background-size:contain; background-position:center;
      background-repeat:no-repeat; background-color:#fff;
    }
    div[class*="st-key-char_"] button {font-size:1.75rem; min-height:64px;}
    div[class*="st-key-related_"] button {font-size:1.45rem; min-height:76px;}
    div[class*="st-key-put_"] button {font-size:1.3rem; min-height:64px;}
    [data-testid="stProgressBar"] {margin-bottom:.1rem;}
    .progress-label {text-align:center; font-weight:800; margin:.2rem;}
    .celebrate {text-align:center; font-size:2.3rem; animation:bounce .7s ease-in-out infinite alternate;}
    @keyframes bounce {to {transform:translateY(-7px) rotate(2deg);}}
    header, footer, #MainMenu {visibility:hidden;}
    @media (max-width:430px) {
      .block-container {padding:.25rem .45rem 1rem;}
      div.stButton > button {min-height:48px; font-size:1.05rem; padding:.15rem;}
      .picture {min-height:105px; font-size:4.5rem;}
      .slot {width:2.8rem; height:3rem; font-size:1.6rem;}
      [data-testid="stImage"] img {max-height:105px;}
      div[class*="st-key-pick_"] button {min-height:104px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_csv(filename: str) -> list[dict]:
    """CSV を辞書のリストとして読み込みます。"""
    with (DATA_DIR / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def load_json(filename: str) -> list[dict]:
    """JSON の問題一覧を読み込みます。"""
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def load_all_data() -> tuple[list[dict], list[dict], list[dict]]:
    """問題データは小さいため、更新がすぐ反映されるよう毎回読み込みます。"""
    return (
        load_csv("name_questions.csv"),
        load_csv("related_questions.csv"),
        load_json("sorting_questions.json"),
    )


NAME_QUESTIONS, RELATED_QUESTIONS, SORTING_QUESTIONS = load_all_data()


def init_state() -> None:
    """画面をまたいで覚えておく値を、最初の1回だけ作ります。"""
    defaults = {
        "screen": "home",
        "mode": "",
        "question_index": 0,
        "correct_count": 0,
        "wrong_questions": [],
        "selected_chars": [],
        "sorting_placed": {},
        "sorting_selected": None,
        "feedback": "",
        "answered": False,
        "choice_order": [],
        "sorting_wrong": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_mode(mode: str) -> None:
    """選んだモードを1問目から始めます。"""
    st.session_state.update(
        screen=mode,
        mode=mode,
        question_index=0,
        correct_count=0,
        wrong_questions=[],
        selected_chars=[],
        sorting_placed={},
        sorting_selected=None,
        feedback="",
        answered=False,
        choice_order=[],
        sorting_wrong=[],
    )


def go_home() -> None:
    st.session_state.screen = "home"


def display_picture(image_name: str, emoji: str, caption: str = "") -> None:
    """PNG/JPG があれば画像、なければ絵文字を表示します。"""
    path = IMAGE_DIR / image_name
    if image_name and path.is_file():
        st.image(str(path), caption=caption or None, use_container_width=True)
    else:
        label = f"<small>{caption}</small>" if caption else ""
        st.markdown(f'<div class="picture">{emoji}{label}</div>', unsafe_allow_html=True)


@st.cache_data
def image_data_uri(image_name: str) -> str:
    """仕分けカードの画像をHTML内に表示できる形へ変換します。"""
    path = IMAGE_DIR / image_name
    if not image_name or not path.is_file():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def item_picture_html(item: dict) -> str:
    """画像があれば画像、なければ絵文字のHTMLを返します。"""
    uri = image_data_uri(item.get("image", ""))
    return f'<img src="{uri}" alt="{item["label"]}">' if uri else item["emoji"]


def image_choice_button(item: dict, selected: bool) -> bool:
    """仕分け画像そのものを、大きなタップボタンとして表示します。"""
    uri = image_data_uri(item.get("image", ""))
    border = "#ff6f91" if selected else "#dcecff"
    if uri:
        st.markdown(
            f"""<style>
            div.st-key-pick_{item["id"]} button {{
              background-image:url("{uri}");
              border:5px solid {border};
            }}
            div.st-key-pick_{item["id"]} button p {{display:none;}}
            </style>""",
            unsafe_allow_html=True,
        )
        label = item["label"]
    else:
        label = f'{item["emoji"]} {item["label"]}'
    return st.button(label, key=f'pick_{item["id"]}', use_container_width=True)


def progress(total: int) -> None:
    number = st.session_state.question_index + 1
    st.markdown(f'<div class="progress-label">{number} / {total}</div>', unsafe_allow_html=True)
    st.progress(number / total)


def finish_screen() -> None:
    total = 5
    st.markdown('<div class="celebrate">🌸 ⭐ 🎉 ⭐ 🌸</div>', unsafe_allow_html=True)
    st.title(f"{total}もん できたよ")
    st.markdown(
        f'<div class="message good">はなまるは<br><span style="font-size:2.4rem">'
        f'{st.session_state.correct_count}こ！</span></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("🔄 もういちど", type="primary", use_container_width=True):
        reset_mode(st.session_state.mode)
        st.rerun()
    if st.button("🏠 はじめに もどる", use_container_width=True):
        go_home()
        st.rerun()


def next_question(total: int) -> None:
    """次の問題用に、一時的な回答だけを空にします。"""
    if st.session_state.question_index + 1 >= total:
        st.session_state.screen = "finish"
    else:
        st.session_state.question_index += 1
        st.session_state.selected_chars = []
        st.session_state.sorting_placed = {}
        st.session_state.sorting_selected = None
        st.session_state.feedback = ""
        st.session_state.answered = False
        st.session_state.choice_order = []
        st.session_state.sorting_wrong = []


def home() -> None:
    st.markdown('<div class="celebrate">🌈 ✨ 🌼</div>', unsafe_allow_html=True)
    st.title("ひらがな たんけんたい")
    st.markdown("### どれで あそぶ？")
    st.write("")
    if st.button("🧩  なまえを つくろう", use_container_width=True):
        reset_mode("name")
        st.rerun()
    if st.button("🔗  なかまの ことば", use_container_width=True):
        reset_mode("related")
        st.rerun()
    if st.button("📦  わけてみよう", use_container_width=True):
        reset_mode("sorting")
        st.rerun()


def name_mode() -> None:
    questions = NAME_QUESTIONS
    q = questions[st.session_state.question_index]
    progress(len(questions))
    st.markdown("### これは なあに？")
    display_picture(q["image"], q["emoji"])

    answer = list(q["answer"])
    selected = st.session_state.selected_chars
    slots = "".join(
        f'<div class="slot {"filled" if i < len(selected) else ""}">'
        f'{selected[i] if i < len(selected) else " "}</div>'
        for i in range(len(answer))
    )
    st.markdown(f'<div class="answer-slots">{slots}</div>', unsafe_allow_html=True)

    # 入れた文字を押すと、その位置の文字を取り消せます。
    if selected and not st.session_state.answered:
        cols = st.columns(len(selected))
        for i, char in enumerate(selected):
            if cols[i].button(f"{char} ↩", key=f"remove_{i}", use_container_width=True):
                selected.pop(i)
                st.rerun()

    choices = q["choices"].split("|")
    for row_start in range(0, len(choices), 4):
        cols = st.columns(4)
        for col, char in zip(cols, choices[row_start : row_start + 4]):
            if col.button(char, key=f"char_{row_start}_{char}", disabled=st.session_state.answered):
                if len(selected) < len(answer):
                    selected.append(char)
                st.rerun()

    col1, col2 = st.columns(2)
    if col1.button("ぜんぶ けす", disabled=not selected or st.session_state.answered):
        st.session_state.selected_chars = []
        st.session_state.feedback = ""
        st.rerun()
    if col2.button("こたえる", type="primary", disabled=len(selected) != len(answer) or st.session_state.answered):
        if "".join(selected) == q["answer"]:
            st.session_state.feedback = "correct"
            st.session_state.answered = True
            st.session_state.correct_count += 1
        else:
            st.session_state.feedback = "retry"
            if q["id"] not in st.session_state.wrong_questions:
                st.session_state.wrong_questions.append(q["id"])
        st.rerun()

    if st.session_state.feedback == "correct":
        st.markdown(
            f'<div class="celebrate">🌸 ⭐ 🎉</div><div class="message good">'
            f'せいかい！<br>{q["answer"]}だよ</div>',
            unsafe_allow_html=True,
        )
        if st.button("つぎへ ➜", type="primary"):
            next_question(len(questions))
            st.rerun()
    elif st.session_state.feedback == "retry":
        st.markdown('<div class="message try">💡 もういちど<br>やってみよう</div>', unsafe_allow_html=True)


def related_mode() -> None:
    questions = RELATED_QUESTIONS
    q = questions[st.session_state.question_index]
    progress(len(questions))
    display_picture(q["image"], q["emoji"])
    st.markdown(f"### {q['question']}")

    # 問題を開いた時に1回だけ、選択肢の順番を混ぜます。
    if not st.session_state.choice_order:
        choices = q["choices"].split("|")
        random.shuffle(choices)
        st.session_state.choice_order = choices

    for row_start in range(0, len(st.session_state.choice_order), 2):
        cols = st.columns(2)
        for col, choice in zip(cols, st.session_state.choice_order[row_start : row_start + 2]):
            label = f"⭐ {choice} ⭐" if st.session_state.answered and choice == q["answer"] else choice
            if col.button(label, key=f"related_{choice}", disabled=st.session_state.answered):
                if choice == q["answer"]:
                    st.session_state.feedback = "correct"
                    st.session_state.answered = True
                    st.session_state.correct_count += 1
                else:
                    st.session_state.feedback = "retry"
                    if q["id"] not in st.session_state.wrong_questions:
                        st.session_state.wrong_questions.append(q["id"])
                st.rerun()

    if st.session_state.feedback == "correct":
        st.markdown(
            f'<div class="celebrate">🌸 ⭐ 🎉</div><div class="message good">'
            f'せいかい！<br>{q["answer"]}</div>',
            unsafe_allow_html=True,
        )
        display_picture(q["related_image"], q["related_emoji"], q["answer"])
        if st.button("つぎへ ➜", type="primary"):
            next_question(len(questions))
            st.rerun()
    elif st.session_state.feedback == "retry":
        st.markdown('<div class="message try">💡 もういちど<br>えらんでね</div>', unsafe_allow_html=True)


def sorting_mode() -> None:
    questions = SORTING_QUESTIONS
    q = questions[st.session_state.question_index]
    progress(len(questions))
    st.markdown(f"### {q['question']}")
    placed = st.session_state.sorting_placed
    wrong = st.session_state.sorting_wrong

    # 間違い直し中は、間違ったカードだけをもう一度表示します。
    available = [
        item for item in q["items"]
        if item["id"] not in placed and (not wrong or item["id"] in wrong)
    ]
    if available:
        cols = st.columns(2)
        for i, item in enumerate(available):
            with cols[i % 2]:
                if image_choice_button(item, st.session_state.sorting_selected == item["id"]):
                    st.session_state.sorting_selected = item["id"]
                    st.rerun()

    selected_id = st.session_state.sorting_selected
    if selected_id:
        item = next(item for item in q["items"] if item["id"] == selected_id)
        cols = st.columns(2)
        for col, category in zip(cols, q["categories"]):
            if col.button(category["label"], key=f"put_{category['id']}", type="primary"):
                placed[selected_id] = category["id"]
                st.session_state.sorting_selected = None
                if selected_id in wrong:
                    wrong.remove(selected_id)
                st.rerun()

    box_cols = st.columns(2)
    for col, category in zip(box_cols, q["categories"]):
        contents = [
            item_picture_html(item)
            for item in q["items"] if placed.get(item["id"]) == category["id"]
        ]
        col.markdown(
            f"<h3>{category['label']}</h3><div class='box'>{' '.join(contents) or '　'}</div>",
            unsafe_allow_html=True,
        )

    if placed and not st.session_state.answered:
        if st.button("↩ ひとつ もどす"):
            last_id = next(reversed(placed))
            placed.pop(last_id)
            st.session_state.feedback = ""
            st.rerun()
        if st.button("🔄 ぜんぶ やりなおす"):
            st.session_state.sorting_placed = {}
            st.session_state.sorting_wrong = []
            st.session_state.feedback = ""
            st.rerun()

    if len(placed) == len(q["items"]) and not st.session_state.answered:
        if st.button("こたえあわせ", type="primary"):
            incorrect = [
                item["id"] for item in q["items"]
                if placed.get(item["id"]) != item["category"]
            ]
            if incorrect:
                st.session_state.sorting_wrong = incorrect
                for item_id in incorrect:
                    placed.pop(item_id, None)
                st.session_state.feedback = "retry"
                if q["id"] not in st.session_state.wrong_questions:
                    st.session_state.wrong_questions.append(q["id"])
            else:
                st.session_state.feedback = "correct"
                st.session_state.answered = True
                st.session_state.correct_count += 1
            st.rerun()

    if st.session_state.feedback == "retry":
        st.markdown(
            '<div class="message try">💡 おしい！<br>もどった えを<br>もういちど わけよう</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.feedback == "correct":
        st.markdown(
            '<div class="celebrate">🌸 ⭐ 🎉</div><div class="message good">ぜんぶ できた！</div>',
            unsafe_allow_html=True,
        )
        if st.button("つぎへ ➜", type="primary"):
            next_question(len(questions))
            st.rerun()


init_state()

if st.session_state.screen == "home":
    home()
elif st.session_state.screen == "name":
    name_mode()
elif st.session_state.screen == "related":
    related_mode()
elif st.session_state.screen == "sorting":
    sorting_mode()
elif st.session_state.screen == "finish":
    finish_screen()

# 学習中は、いつでも最初の画面へ戻れます。
if st.session_state.screen not in {"home", "finish"}:
    st.divider()
    if st.button("🏠 はじめに もどる"):
        go_home()
        st.rerun()
