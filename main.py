import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai

# ★★★ Gemini APIキーを直接記述 ★★★
# この場所にあなたの実際のGemini APIキーを「AIzaSyBrD33qBBMaOLa4F9MvvJn8_0PmFilll4g」
# の部分と置き換えてください。
API_KEY = "AIzaSyBrD33qBBMaOLa4F9MvvJn8_0PmFilll4g"

# APIキーが空でないか、あるいはデフォルトのままではないかを確認
if not API_KEY or API_KEY == "AIzaSyBrD33qBBMaOLa4F9MvvJn8_0PmFilll4g":
    raise ValueError("Gemini APIキーが正しく設定されていません。`main.py`の`API_KEY`変数をあなたの実際のキーに置き換えてください。")

genai.configure(api_key=API_KEY)

app = FastAPI()

# 静的ファイル（HTML, CSS, JS）を配信するための設定
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2Templates を使用してHTMLファイルを返す設定
# 今回のシンプルな例では直接HTMLを返すため必須ではありませんが、拡張性を考慮して含めます。
templates = Jinja2Templates(directory="static")

# Geminiモデルの初期化
# 安全性設定を緩めていますが、本番環境ではユースケースに応じて適切に調整してください。
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

# チャット履歴を保持するための辞書。
# これはサーバーのメモリ上に保存されるため、サーバーが再起動すると履歴は失われます。
# また、複数のユーザーがアクセスした場合、履歴が混同される可能性があります。
# 本番環境では、ユーザーセッションごとにデータベースなどでの永続化を検討してください。
chat_sessions = {}

# リクエストボディのデータ構造を定義
class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    アプリケーションのルートURLにアクセスした際に、静的ファイル内のindex.htmlを返します。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_gemini(chat_request: ChatRequest):
    """
    ユーザーからのチャットメッセージを受け取り、Gemini APIに送信して応答を取得します。
    """
    user_message = chat_request.message
    # デモ用の固定セッションID。
    # 実際にはユーザーごとの認証情報などからユニークなIDを生成します。
    session_id = "default_session"

    # セッションが存在しない場合、新しいチャットセッションを開始
    if session_id not in chat_sessions:
        chat_sessions[session_id] = model.start_chat(history=[])

    try:
        # Geminiモデルにメッセージを送信し、応答を取得
        response = chat_sessions[session_id].send_message(user_message)
        # 応答テキストをクライアントに返す
        return {"response": response.text}
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        # API通信エラーが発生した場合、HTTP 500エラーを返す
        raise HTTPException(status_code=500, detail="Gemini APIとの通信中にエラーが発生しました。")
