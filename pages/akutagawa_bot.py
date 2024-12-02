from pathlib import Path
import pandas as pd
import sqlite3  # SQLite3を使用
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import openai

author_id = '000879'  # 青空文庫の作家番号
author_name = '芥川龍之介'  # 青空文庫の表記での作家名

# ページの基本設定
st.set_page_config(
    page_title="文学の読書コンパニオン",
    page_icon="📚", layout="centered",
    initial_sidebar_state="collapsed",  # サイドバーを非表示
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None
    }
)

# GitHubのリポジトリにある背景画像のURL
img_url = "https://raw.githubusercontent.com/tatsuya797/literary_ai_companion/main/image2.jpg"

# 背景画像の設定（日本の古風な雰囲気の画像に設定）
page_bg_img = f"""
<style>
    .stApp {{
        background-image: url("{img_url}");  /* 和風な背景画像 */
        background-size: cover;
        background-position: center;
        color: #f4f4f4;
    }}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# クエリパラメータを取得
query_params = st.experimental_get_query_params()
selected_title = query_params.get("title", [None])[0]  # クエリパラメータ "title" を取得

if selected_title:
    # データベース接続
    def fetch_text_content(title):
        db_file = "literary_app.db"
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        # BOT テーブルからタイトルに対応する text_content を取得
        cur.execute("SELECT text_content FROM BOT WHERE title = ?", (title,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "該当する内容が見つかりません。"

    # 選択されたタイトルに対応する内容を取得
    text_content = fetch_text_content(selected_title)

    # 結果を表示
    st.markdown(
    f"""
    <div style="
        padding: 20px; 
        margin: 10px 0; 
        background-color: #f9f9f9; 
        border-left: 5px solid #8b4513; 
        border-radius: 5px;
        font-family: 'Yu Mincho', serif; 
        font-size: 1.5rem; 
        font-weight: bold; 
        color: #333;
    ">
        📚 作品名: 『{selected_title}』
    </div>
    """,
    unsafe_allow_html=True,
)
    st.text_area("作品の内容", text_content, height=300)
else:
    st.write("作品が選択されていません。URLのクエリパラメータを確認してください。")




# Streamlit Community Cloudの「Secrets」からOpenAI API keyを取得
openai.api_key = st.secrets.OpenAIAPI.openai_api_key

# st.session_stateを使いメッセージのやりとりを保存
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": st.secrets.AppSettings.chatbot_setting} 
    ]
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0  # 合計文字数を初期化

# チャットボットとやりとりする関数
def communicate():
    # 参考となるテキスト内容
    text_content = fetch_text_content(selected_title)

    # メッセージ履歴を取得
    messages = st.session_state["messages"]

    # ユーザーの入力を追加
    user_message = {"role": "user", "content": st.session_state["user_input"]}
    messages.append(user_message)

    # 入力文字数をカウント
    st.session_state["total_characters"] += len(user_message["content"])

    # ChatGPT API 呼び出し
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは熟練した文学解説者です。以下の文章を理解し、質問に答えてください。"},
            {"role": "user", "content": f"参考文章:\n\n{text_content}"},
        ] + messages  # ユーザーのメッセージ履歴を追加
    )

    # ボットの応答を追加
    bot_message = response["choices"][0]["message"]
    messages.append(bot_message)

    # 入力欄をクリア
    st.session_state["user_input"] = ""

# 初期化: セッションステートにメッセージ履歴と合計文字数を保存
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "total_characters" not in st.session_state:
    st.session_state["total_characters"] = 0

# ユーザーインターフェイス
st.title(author_name + "チャットボット")
st.write(author_name + "の作品に基づいたチャットボットです。")

# 対話終了ボタンの表示 (10文字で出現)
if st.session_state["total_characters"] >= 10:
    if st.markdown('<button class="red-button">対話終了</button>', unsafe_allow_html=True):
        st.write("対話を終了しました。")
        # 必要に応じて処理を追加

# ユーザーのメッセージ入力（改行対応）
user_input = st.text_area(
    "メッセージを入力してください",
    key="user_input",
    height=100,
    on_change=communicate
)


# カスタム CSS を追加して左右分割のスタイルとアイコンを設定
st.markdown(
    """
    <style>
    .user-message {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        margin: 10px 0;
    }
    .bot-message {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin: 10px 0;
    }
    .message-content {
        background-color: #dcf8c6;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        text-align: left;
        white-space: pre-wrap; /* 改行をサポート */
    }
    .bot-content {
        background-color: #f1f0f0;
        color: black;
        padding: 10px;
        border-radius: 10px;
        max-width: 70%;
        text-align: left;
        white-space: pre-wrap; /* 改行をサポート */
    }
    .icon {
        font-size: 1.5rem;
        margin: 0 10px;
    }
    .red-button {
            background-color: white;
            color: red;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid red;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
        }
        .red-button:hover {
            background-color: red;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 対話履歴を表示（最新のメッセージを上に）
if st.session_state.get("messages"):
    messages = st.session_state["messages"]

    # 最新のメッセージが上に来るように逆順にループ
    for message in reversed(messages[1:]):  # システムメッセージをスキップ
        if message["role"] == "user":
            st.markdown(
                f"""
                <div class="user-message">
                    <span class="icon">😊</span>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif message["role"] == "assistant":
            st.markdown(
                f"""
                <div class="bot-message">
                    <div class="bot-content">{message["content"]}</div>
                    <span class="icon">🤖</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
