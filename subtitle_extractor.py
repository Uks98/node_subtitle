import sys
import re
import json
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
sys.stdout.reconfigure(encoding='utf-8')
# def extract_video_id(url):
#     regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
#     match = re.search(regex, url)
#     return match.group(1) if match else None
def extract_video_id(url):
    """
    유튜브 URL에서 비디오 ID를 추출하는 함수.
    긴 형식과 단축 형식을 모두 지원.
    """
    # 1. v= 파라미터가 있는 경우 우선적으로 처리
    v_param_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    v_param_match = re.search(v_param_pattern, url)
    
    if v_param_match:
        return v_param_match.group(1)
    
    # 2. 공유하기 링크 및 기타 형식 처리
    fallback_pattern = r"(?:youtu\.be\/|youtube\.com\/(?:embed\/|shorts\/|live\/|user\/\S+\/))([^#&?]{11})"
    fallback_match = re.search(fallback_pattern, url)
    
    if fallback_match:
        return fallback_match.group(1)
    
    # 3. 유효한 비디오 ID를 찾지 못한 경우
    return "qmWlTBd18v4"

def extract_subtitles(video_id, lang):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en','cn'])
        content = []
        for line in transcript:
            content.append({
                "text": line['text'],
                "offset": int(line['start'] * 1000),
                "duration": int(line['duration'] * 1000),
                "lang": lang
            })
        result = {
            "lang": lang,
            "content": content
        }
        print(json.dumps(result, ensure_ascii=False))
    except NoTranscriptFound:
        print(json.dumps({"error": "No transcript found for the selected language."}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "YouTube URL is required"}, ensure_ascii=False))
        sys.exit()

    youtube_url = sys.argv[1]
    video_id = extract_video_id(youtube_url)
    if video_id:
        extract_subtitles(video_id, ['ko', 'en'])
    else:
        print(json.dumps({"error": "Invalid YouTube URL"}, ensure_ascii=False))