import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai

# Gemini APIキーを環境変数から取得 (Vercelでも環境変数で設定するのが推奨)
# Vercelのプロジェクト設定で 'GEMINI_API_KEY' を設定します。
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    # 開発環境で.envファイルを使用する場合
    try:
        from dotenv import load_dotenv
        load_dotenv()
        API_KEY = os.getenv("GEMINI_API_KEY")
    except ImportError:
        pass # dotenvがない場合は何もしない

    if not API_KEY:
        # Vercelでは環境変数が必須なので、設定されていない場合はエラーにする
        raise ValueError("GEMINI_API_KEY 環境変数が設定されていません。Vercelのプロジェクト設定でAPIキーを設定してください。")

genai.configure(api_key=API_KEY)

app = FastAPI()

# 静的ファイル（HTML, CSS, JS）を配信するための設定
# Vercelでは静的ファイルは `vercel.json` で直接ホストするため、
# FastAPI側での静的ファイル配信は不要ですが、ローカル開発用に残しておきます。
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2Templates は今回のシンプルな構成では直接使われませんが、ローカル開発用に残します。
templates = Jinja2Templates(directory="static")

# Geminiモデルの初期化
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
# VercelのServerless Functionsはステートレスであるため、
# 実際のデプロイ環境では chat_sessions はリクエストごとにリセットされます。
# 永続的なチャット履歴が必要な場合は、データベース（例: PlanetScale, Supabase）の導入を検討してください。
chat_sessions = {}

# リクエストボディの型定義
class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    トップページ（index.html）を配信します。
    Vercelでは静的ファイルとして`index.html`を直接ホストするため、
    このエンドポイントはVercelデプロイ時には通常はアクセスされません。
    ローカル開発用です。
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat") # VercelのAPIエンドポイントとしてパスを変更
async def chat_with_gemini(chat_request: ChatRequest):
    """
    ユーザーからのメッセージを受け取り、Gemini APIで応答を生成します。
    """
    user_message = chat_request.message
    session_id = "default_session" # シンプル化のため、固定セッションIDを使用

    # VercelのServerless Functionsはステートレスなので、
    # chat_sessionsはリクエストごとに新しいオブジェクトになります。
    # 履歴を維持したい場合は、外部データベースやキャッシュサービスが必要です。
    # ここでは単純化のため、各リクエストで新しいチャットセッションを開始します。
    chat_session_instance = model.start_chat(history=[])

    try:
        response = chat_session_instance.send_message(user_message)
        return {"response": response.text}
    except Exception as e:
        print(f"Error communicating with Gemini API: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini APIとの通信中にエラーが発生しました: {e}")
