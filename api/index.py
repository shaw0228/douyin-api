from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

@app.get("/api")
async def root():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/test")
async def test():
    cookie = os.getenv('DOUYIN_COOKIE')
    return {
        "status": "ok",
        "cookie_exists": bool(cookie),
        "cookie_length": len(cookie) if cookie else 0
    }

@app.get("/api/douyin/{user_id}")
async def get_douyin_data(user_id: str):
    try:
        url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'
        cookie = os.getenv('DOUYIN_COOKIE')
        
        if not cookie:
            return JSONResponse(
                status_code=500,
                content={"error": "Cookie not found"}
            )
        
        headers = {
            "Accept": "application/json",
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            "Referer": f"https://www.douyin.com/user/{user_id}"
        }
        
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": user_id,
            "count": "10"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json()
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.api_route("/api/{path_name:path}", methods=["GET"])
async def catch_all(path_name: str):
    return {"status": "error", "message": f"Path /api/{path_name} not found"} 