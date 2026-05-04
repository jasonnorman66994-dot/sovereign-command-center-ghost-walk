from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/alerts")
async def receive_alert(request: Request):
    data = await request.json()
    print("[SIEM RECEIVED ALERT]", data)
    return {"status": "received"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)