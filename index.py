import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai

# Gemini APIキーを直接コードに記述 (非推奨)
# ★★★ ここにあなたのGemini APIキーを直接入力してください ★★★
API_KEY = "AIzaSyBrD33qBBMaOLa4F9MvvJn8_0PmFilll4g" # ← この部分をあなたの実際のキーに置き換える

# もしAPIキーがまだない、または無効なキーの場合の基本的なチェック
if not API_KEY or API_KEY == "AIzaSyBrD33qBBMaOLa4F9MvvJn8_0PmFilll4g": # YOUR_GEMINI_API_KEY_HEREは置き換え忘れがないかのチェック用
    raise ValueError("Gemini APIキーが設定されていないか、無効です。正しいキーを入力してください。")

genai.configure(api_key=API_KEY)

app = FastAPI()

# 静的ファイル（HTML, CSS, JS）を配信するための設定
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2Templates を使用してHTMLファイルを返す
templates = Jinja2Templates(directory="static")

# Geminiモデルの初期化
# 安全性設定を緩めていますが、本番環境では適切に調整してください。
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 500,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# チャット履歴を保持するためのモデル
# 実際のアプリケーションではデータベースなどに永続化することが多いですが、
# シンプルなデモのため、サーバーのメモリ上で保持します。
# 注意: これは複数のユーザー間で共有されるため、デモ用途です。
# ユーザーごとのセッション管理には、より複雑なロジックが必要です。
chat_sessions = {}

# リクエストボディの型定義
class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    トップページ（index.html）を配信します。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_gemini(chat_request: ChatRequest):
    """
    ユーザーからのメッセージを受け取り、Gemini APIで応答を生成します。
    """
    user_message = chat_request.message
    session_id = "default_session" # シンプル化のため、固定セッションIDを使用

    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])

    try:
        # Geminiにメッセージを送信し、応答を取得
        response = chat_sessions[session_id].send_message(user_message)
        return {"response": response.text}
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        raise HTTPException(status_code=500, detail="Gemini APIとの通信中にエラーが発生しました。")
