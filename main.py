
import os
from fastapi import FastAPI, WebSocket
from app.api_routes import router
from app.core.broadcast import connect, disconnect


# Load .env for Telegram integration
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path)
    print(f"[DEBUG] Loaded .env from: {env_path}")
    print(f"[DEBUG] TELEGRAM_CHAT_ID at startup: {os.getenv('TELEGRAM_CHAT_ID')}")
except Exception as e:
    print(f"[WARNING] Could not load .env: {e}")


app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Sovereign SOAR API is running. See /docs for OpenAPI."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        pass
    finally:
        await disconnect(websocket)
