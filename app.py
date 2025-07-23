import streamlit as st
import datetime
import base64
from datetime import datetime as dt

st.set_page_config(page_title="ASOBIBA予約＋作業報告チャット", layout="centered")

# CSSカスタマイズ
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
    }
    .chat-meta {
        color: #34b7f1;
        font-size: 12px;
        margin-bottom: 4px;
    }
    .uploadedFile {
        color: gray !important;
        font-size: 12px !important;
        background-color: #d8f3dc !important;
        padding: 4px;
        border-radius: 5px;
        width: 90%;
    }
    </style>
""", unsafe_allow_html=True)

# セッションステート初期化
if "reservations" not in st.session_state:
    st.session_state["reservations"] = {}
if "chat_logs" not in st.session_state:
    st.session_state["chat_logs"] = []
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "ユーザーＡ"

members = ["ユーザーＡ", "ユーザーＢ"]

# タブ構成
tab1, tab2, tab3 = st.tabs(["👤 ユーザー選択", "📅 予約フォーム", "💬 チャット"])

# ユーザー選択
with tab1:
    st.markdown("<h2>🏠 ASOBIBA専用アプリ</h2>", unsafe_allow_html=True)
    st.session_state["current_user"] = st.selectbox("👤 ユーザーを選んでください", members)

# 予約ページ
with tab2:
    st.markdown("<h2>📅 予約フォーム</h2>", unsafe_allow_html=True)
    facilities = ["施設A", "施設B"]
    selected_facility = st.selectbox("🏢 予約する施設を選んでください", facilities)
    name = st.session_state["current_user"]
    date = st.date_input("希望日を選んでください", min_value=datetime.date.today())
    reservation_key = (selected_facility, str(date))
    is_reserved = st.session_state["reservations"].get(reservation_key)

    if is_reserved:
        st.warning(f"{selected_facility} はこの日すでに {is_reserved} さんが予約済です")
    else:
        if st.button("予約する", use_container_width=True):
            st.session_state["reservations"][reservation_key] = name
            st.success(f"{selected_facility} の予約を {date} に受け付けました（{name} さん）")

    st.subheader("📝 予約一覧")
    if st.session_state["reservations"]:
        for (fac, d), n in sorted(st.session_state["reservations"].items(), key=lambda x: (x[0][1], x[0][0])):
            day = dt.strptime(d, "%Y-%m-%d")
            weekday_ja = ["月", "火", "水", "木", "金", "土", "日"]
            weekday = weekday_ja[day.weekday()]
            st.write(f"✅【{fac}】{day.strftime('%m月%d日')}（{weekday}）：{n} さん")
    else:
        st.info("まだ予約はありません")

# チャットページ
with tab3:
    st.markdown("<h2>💬 専用チャット</h2>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        message = st.text_input("✏️ コメントを入力してください")

        # カスタムアップロードボタン
        st.markdown("""
            <label for="file_uploader" style="display: block; font-size: 16px; font-weight: normal; color: white; margin-top: 10px;">
                📷 写真or画像を ↓から添付可能
            </label>
        """, unsafe_allow_html=True)

        image_file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        submitted = st.form_submit_button("送信", use_container_width=True)

        if submitted and message:
            img_data = None
            if image_file:
                img_data = base64.b64encode(image_file.read()).decode()
            st.session_state["chat_logs"].append({
                "sender": st.session_state["current_user"],
                "text": message.replace("<", "&lt;").replace(">", "&gt;"),
                "img": img_data,
                "time": dt.now().strftime("%Y-%m-%d %H:%M")
            })

    # チャット表示
    for chat in st.session_state["chat_logs"]:
        align = "flex-end" if chat["sender"] == st.session_state["current_user"] else "flex-start"
        sender_color = "#34b7f1" if chat["sender"] == st.session_state["current_user"] else "#999999"
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

