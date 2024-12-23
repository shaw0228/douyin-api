from http.client import HTTPSConnection
import json
from urllib.parse import urlencode

def handler(request):
    """
    Vercel Serverless Function 处理函数
    """
    try:
        # 从请求中获取user_id
        params = request.query
        user_id = params.get('user_id', '')
        
        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "success": False,
                    "message": "请提供用户ID",
                    "data": None
                })
            }

        # 基础配置
        host = 'www.douyin.com'
        path = '/aweme/v1/web/aweme/post/'
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        
        # Cookie值（从环境变量获取）
        cookie_val = 'UIFID_TEMP=0173c8f974a1c07577a40e1ddb6347b1804450ad458bea7bd35bf3d7a8ab5901076bee86ba6af4084d3c3e0e7d477b2e05f1e5f53aa75ac59d37eea942a54a11b503e9de987342dcc418219ee801c913'
        
        # 请求参数
        douyin_params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "sec_user_id": user_id,
            "max_cursor": "0",
            "count": "10",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10"
        }
        
        # 请求头
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": cookie_val,
            "Referer": f"https://www.douyin.com/user/{user_id}",
            "User-Agent": ua,
            "Host": host
        }

        # 构建完整路径
        full_path = f"{path}?{urlencode(douyin_params)}"
        
        # 创建HTTPS连接
        conn = HTTPSConnection(host, timeout=10)
        
        try:
            # 发送请求
            conn.request("GET", full_path, headers=headers)
            response = conn.getresponse()
            
            if response.status != 200:
                return {
                    "statusCode": response.status,
                    "body": json.dumps({
                        "success": False,
                        "message": f"抖音API请求失败: {response.status}",
                        "data": None
                    })
                }
            
            # 读取响应数据
            data = json.loads(response.read().decode('utf-8'))
            video_list = data.get('aweme_list', [])
            
            if not video_list:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "success": True,
                        "message": "未找到视频数据",
                        "data": []
                    })
                }
            
            # 处理视频数据
            processed_videos = []
            for video in video_list[:5]:  # 只处理前5个视频
                try:
                    video_info = {
                        "title": video.get('desc', '无标题'),
                        "author": video.get('author', {}).get('nickname', '未知作者'),
                        "video_id": video.get('aweme_id', ''),
                        "video_link": f"https://www.douyin.com/video/{video.get('aweme_id', '')}",
                        "stats": {
                            "likes": video.get('statistics', {}).get('digg_count', 0),
                            "comments": video.get('statistics', {}).get('comment_count', 0)
                        }
                    }
                    processed_videos.append(video_info)
                except Exception:
                    continue
            
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "message": f"成功获取 {len(processed_videos)} 个视频",
                    "data": processed_videos
                }, ensure_ascii=False)
            }
            
        finally:
            conn.close()
            
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "success": False,
                "message": f"处理请求时出错: {str(e)}",
                "data": None
            })
        } 