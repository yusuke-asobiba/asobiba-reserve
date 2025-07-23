import streamlit as st
import datetime
import base64
from streamlit.components.v1 import html as components_html

st.set_page_config(page_title="ASOBIBA予約＋作業報告チャット", layout="centered")

st.markdown("""
    <style>
    * { font-family: 'Meiryo', sans-serif; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; font-size:28px;'>🏠 ASOBIBA専用アプリ</h1>", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if "reservations" not in st.session_state:
    st.session_state["reservations"] = {}
if "chat_logs" not in st.session_state:
    st.session_state["chat_logs"] = []

# --- 会員選択 ---
members = ["ユーザーＡ", "ユーザーＢ"]
current_user = st.selectbox("🔰 現在ログイン中のユーザーを選んでください", members)

# --- 施設選択 ---
facilities = ["施設A", "施設B"]
selected_facility = st.selectbox("🏢 予約する施設を選んでください", facilities)

# --- 予約フォーム ---
st.subheader("📅 予約フォーム")
name = current_user
date = st.date_input("希望日を選んでください", min_value=datetime.date.today())
reservation_key = (selected_facility, str(date))
is_reserved = st.session_state["reservations"].get(reservation_key)

if is_reserved:
    st.warning(f"{selected_facility} はこの日すでに {is_reserved} さんが予約済です")
else:
    if st.button("予約する", use_container_width=True):
        st.session_state["reservations"][reservation_key] = name
        st.success(f"{selected_facility} の予約を {date} に受け付けました（{name} さん）")

# --- 予約一覧 ---
from datetime import datetime as dt
st.subheader("📝 予約一覧")
if st.session_state["reservations"]:
    for (fac, d), n in sorted(st.session_state["reservations"].items(), key=lambda x: (x[0][1], x[0][0])):
        day = dt.strptime(d, "%Y-%m-%d")
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekday_ja[day.weekday()]
        st.write(f"✅【{fac}】{day.strftime('%m月%d日')}（{weekday}）：{n} さん")
else:
    st.info("まだ予約はありません")

# --- 作業報告チャット ---
st.subheader("📩 ASOBIBA専用チャット")

# 入力フォーム
with st.form(key="chat_form", clear_on_submit=True):
    message = st.text_input("✏️コメントを入力してください")
    image_file = st.file_uploader("🖼️画像を添付出来ます", type=["png", "jpg", "jpeg"])
    submitted = st.form_submit_button("送信", use_container_width=True)

    if submitted and message:
        img_data = None
        if image_file:
            img_data = base64.b64encode(image_file.read()).decode()
        st.session_state["chat_logs"].append({
            "sender": current_user,
            "text": message,
            "img": img_data,
            "time": dt.now().strftime("%Y-%m-%d %H:%M")
        })

# チャット表示（👻除霊済み・フォント強制Meiryoに）
for chat in st.session_state["chat_logs"]:
    is_self = chat["sender"] == current_user
    align = "flex-end" if is_self else "flex-start"
    bg_color = "#dcf8c6" if is_self else "#ffffff"
    sender_color = "#34b7f1" if is_self else "#999999"
    bubble_style = f"""
        background-color: {bg_color};
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        max-width: 90%;
        word-wrap: break-word;
        font-family: 'Meiryo', sans-serif;
    """
    sender_style = f"color: {sender_color}; font-size: 12px; margin-bottom: 2px; font-family: 'Meiryo', sans-serif;"
    safe_text = chat["text"].replace("<", "&lt;").replace(">", "&gt;")

    html_block = f"""
    <div style="display: flex; justify-content: {align}; font-family: 'Meiryo', sans-serif;">
        <div style="{bubble_style}">
            <div style="{sender_style}">{chat['sender']}（{chat['time']}）</div>
            <div style="color: black;">{safe_text}</div>
            {'<img src="data:image/png;base64,' + chat['img'] + '" style="width:100%; margin-top:5px;">' if chat['img'] else ''}
        </div>
    </div>
    """

    components_html(html_block, height=600, scrolling=True)
