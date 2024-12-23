from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Optional, List, Dict
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from cachetools import TTLCache

load_dotenv()  # 添加在其他 import 之后

# 创建 FastAPI 应用
app = FastAPI(
    title="抖音视频数据 API",
    description="提供抖音用户视频数据的 API 服务",
    version="1.0.0"
)

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 从环境变量获取Cookie
DOUYIN_COOKIE = os.getenv('DOUYIN_COOKIE', 'YOUR_COOKIE_HERE')

# 基础配置
BASE_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": DOUYIN_COOKIE
}

# 创建一个TTL缓存，设置最大容量为100，过期时间为1小时
video_cache = TTLCache(maxsize=100, ttl=3600)

@app.get("/api/douyin/user_videos/{user_id}")
async def get_user_videos(
    user_id: str,
    max_cursor: int = 0,
    count: int = 10
):
    """获取指定用户的视频列表"""
    # 生成缓存键
    cache_key = f"{user_id}:{max_cursor}:{count}"
    
    # 检查缓存
    if cache_key in video_cache:
        return video_cache[cache_key]
        
    try:
        url = 'https://www.douyin.com/aweme/v1/web/aweme/post/'
        
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": user_id,
            "max_cursor": max_cursor,
            "count": count,
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10"
        }
        
        headers = BASE_HEADERS.copy()
        headers["Referer"] = f"https://www.douyin.com/user/{user_id}"
        
        # 打印请求信息
        print(f"Request URL: {url}")
        print(f"Request Headers: {headers}")
        print(f"Request Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # 打印响应信息
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text[:500]}")  # 打印前500个字符
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"抖音API请求失败: {response.status_code}",
                "data": None
            }
            
        data = response.json()
        video_list = data.get('aweme_list', [])
        
        if not video_list:
            return {
                "success": True,
                "message": "未找到视频数据",
                "data": []
            }
            
        # 处理视频数据
        processed_videos = []
        for video in video_list:
            try:
                video_info = {
                    "title": video.get('desc', '无标题'),
                    "author": video.get('author', {}).get('nickname', '未知作者'),
                    "video_id": video.get('aweme_id', ''),
                    "video_link": f"https://www.douyin.com/video/{video.get('aweme_id', '')}",
                    "create_time": video.get('create_time', 0),
                    "statistics": {
                        "likes": video.get('statistics', {}).get('digg_count', 0),
                        "comments": video.get('statistics', {}).get('comment_count', 0),
                        "shares": video.get('statistics', {}).get('share_count', 0)
                    }
                }
                processed_videos.append(video_info)
            except Exception as e:
                continue
                
        result = {
            "success": True,
            "message": f"成功获取 {len(processed_videos)} 个视频",
            "data": processed_videos
        }
        
        # 存入缓存
        video_cache[cache_key] = result
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"处理请求时出错: {str(e)}",
            "data": None
        }

# if __name__ == "__main__":
#     # 获取环境变量中的端口，默认8000
#     port = int(os.getenv('PORT', 8000))
    
#     # 启动服务
#     uvicorn.run(
#         "douyin_api:app",
#         host="0.0.0.0",
#         port=port,
#         workers=4  # 生产环境建议使用多个worker
#     ) 