import streamlit as st
import datetime
import base64
from datetime import datetime as dt

st.set_page_config(page_title="ASOBIBA予約＋作業報告チャット", layout="centered")

# スタイル調整
st.markdown("""
    <style>
    * { font-family: 'Meiryo', sans-serif; }
    .chat-bubble {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 4px;
        max-width: 90%;
        word-wrap: break-word;
        font-family: 'Meiryo', sans-serif;
    }
    .chat-meta {
        color: #34b7f1;
        font-size: 12px;
        margin-bottom: 4px;
    }
    /* 英語UI部分を小さくグレー表示に */
    .uploadedFile {
        font-size: 10px !important;
        color: #888 !important;
        transform: scale(0.8);
        transform-origin: top left;
    }
    </style>
""", unsafe_allow_html=True)

# タイトル
st.markdown("<h1 style='text-align: center; font-size:28px;'>🏠 ASOBIBA専用アプリ</h1>", unsafe_allow_html=True)

# セッションステート初期化
if "reservations" not in st.session_state:
    st.session_state["reservations"] = {}
if "chat_logs" not in st.session_state:
    st.session_state["chat_logs"] = []

# ユーザー選択
members = ["ユーザーＡ", "ユーザーＢ"]
current_user = st.selectbox("🔰 現在ログイン中のユーザーを選んでください", members)

# 予約フォーム
st.subheader("📅 予約フォーム")
facilities = ["施設A", "施設B"]
selected_facility = st.selectbox("🏢 予約する施設を選んでください", facilities)
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

# 予約一覧
st.subheader("📝 予約一覧")
if st.session_state["reservations"]:
    for (fac, d), n in sorted(st.session_state["reservations"].items(), key=lambda x: (x[0][1], x[0][0])):
        day = dt.strptime(d, "%Y-%m-%d")
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"]
        weekday = weekday_ja[day.weekday()]
        st.write(f"✅【{fac}】{day.strftime('%m月%d日')}（{weekday}）：{n} さん")
else:
    st.info("まだ予約はありません")

# チャット
st.subheader("📩 ASOBIBA専用チャット")
with st.form(key="chat_form", clear_on_submit=True):
    message = st.text_input("✏️コメントを入力してください")

    # カスタム風ボタン
    st.markdown("""
        <style>
        .custom-upload-label {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 10px;
        }
        .custom-upload-label:hover {
            background-color: #45a049;
        }
        </style>
        <label class="custom-upload-label">
            📷 写真or画像を↓で添付
        </label>
    """, unsafe_allow_html=True)

    # 英語UI部分（縮小＋グレー化）
    image_file = st.file_uploader(
        label="",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    st.markdown('<div class="uploadedFile">Drag and drop file here<br>Limit 200MB per file • PNG, JPG, JPEG</div>', unsafe_allow_html=True)

    submitted = st.form_submit_button("送信", use_container_width=True)

    if submitted and message:
        img_data = None
        if image_file:
            img_data = base64.b64encode(image_file.read()).decode()
        st.session_state["chat_logs"].append({
            "sender": current_user,
            "text": message.replace("<", "&lt;").replace(">", "&gt;"),
            "img": img_data,
            "time": dt.now().strftime("%Y-%m-%d %H:%M")
        })

# チャットログ表示
for chat in st.session_state["chat_logs"]:
    align = "flex-end" if chat["sender"] == current_user else "flex-start"
    sender_color = "#34b7f1" if chat["sender"] == current_user else "#999999"
    ghost_notice = "👻" if not chat["img"] else ""

    st.markdown(f"""
        <div style="display: flex; justify-content: {align};">
            <div class="chat-bubble">
                <div class="chat-meta" style="color: {sender_color};">{chat['sender']}（{chat['time']}）</div>
                <div style="color: black;">{chat['text']}</div>
                {f'<img src="data:image/png;base64,{chat["img"]}" style="width:100%; margin-top:5px;">' if chat["img"] else ghost_notice}
            </div>
        </div>
    """, unsafe_allow_html=True)
