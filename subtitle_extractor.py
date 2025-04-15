# import sys
# import re
# import json
# import time
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
# sys.stdout.reconfigure(encoding='utf-8')
# def extract_video_id(url):
#     """
#     유튜브 URL에서 비디오 ID를 추출하는 함수.
#     긴 형식과 단축 형식을 모두 지원.
#     """
#     # 1. v= 파라미터가 있는 경우 우선적으로 처리
#     v_param_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
#     v_param_match = re.search(v_param_pattern, url)
    
#     if v_param_match:
#         return v_param_match.group(1)
    
#     # 2. 공유하기 링크 및 기타 형식 처리
#     fallback_pattern = r"(?:youtu\.be\/|youtube\.com\/(?:embed\/|shorts\/|live\/|user\/\S+\/))([^#&?]{11})"
#     fallback_match = re.search(fallback_pattern, url)
    
#     if fallback_match:
#         return fallback_match.group(1)
    
#     # 3. 유효한 비디오 ID를 찾지 못한 경우
#     return ""

# def extract_subtitles(video_id, lang):
#     try:
#         transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en','cn'])
#         content = []
#         # time.sleep(2)
#         for line in transcript:
#             content.append({
#                 "text": line['text'],
#                 "offset": int(line['start'] * 1000),
#                 "duration": int(line['duration'] * 1000),
#                 "lang": lang
#             })
#         result = {
#             "lang": lang,
#             "content": content
#         }
#         print(json.dumps(result, ensure_ascii=False))
#     except NoTranscriptFound:
#         print(json.dumps({"error": "No transcript found"}, ensure_ascii=False))
#     except Exception as e:
#         print(json.dumps({"error": str(e)}, ensure_ascii=False))

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print(json.dumps({"error": "YouTube URL is required"}, ensure_ascii=False))
#         sys.exit()

#     youtube_url = sys.argv[1]
#     video_id = extract_video_id(youtube_url)
#     if video_id:
#         extract_subtitles(video_id, ['ko', 'en'])
#     else:
#         print(json.dumps({"error": "Invalid YouTube URL"}, ensure_ascii=False))

import sys
import re
import json
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    RequestBlocked,  # v1.0.0+에서 직접 임포트
    NoTranscriptFound
)
import os
from dotenv import load_dotenv
from youtube_transcript_api.proxies import WebshareProxyConfig
from tenacity import retry, stop_after_attempt, wait_exponential

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()
# Webshare Residential 프록시 설정 (대시보드 계정 정보 입력)
YT_API = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username= os.getenv("PROXY_USERNAME"),
        proxy_password=os.getenv("PROXY_PASSWORD"),
        domain_name="p.webshare.io",
    )
)

def extract_video_id(url):
    """유튜브 URL에서 비디오 ID 추출"""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/|youtube\.com\/(?:embed\/|shorts\/|live\/|user\/\S+\/))([^#&?]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def extract_subtitles(video_id, lang='ko'):
    """자막 추출 핵심 로직 (재시도 메커니즘 포함)"""
    try:
        transcript = YT_API.fetch(
            video_id,
            languages=[lang, 'en', 'cn'],
            preserve_formatting=False
        )
        
        return {
            "lang": lang,
            "content": [
                {
                    "text": line.text,
                    "offset": int(line.start * 1000),
                    "duration": int(line.duration * 1000)
                } for line in transcript
            ]
        }
        
    except RequestBlocked as e:
        return {"error": f"IP 차단됨: {str(e)}"}
    except NoTranscriptFound:
        return {"error": "해당 언어 자막 없음"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "YouTube URL 필수"}, ensure_ascii=False))
        sys.exit(1)

    video_id = extract_video_id(sys.argv[1])
    if not video_id:
        print(json.dumps({"error": "유효하지 않은 YouTube URL"}, ensure_ascii=False))
        sys.exit(1)
        
    result = extract_subtitles(video_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))