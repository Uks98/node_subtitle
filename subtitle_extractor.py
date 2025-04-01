import sys
import re
import json
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
sys.stdout.reconfigure(encoding='utf-8')
def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

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