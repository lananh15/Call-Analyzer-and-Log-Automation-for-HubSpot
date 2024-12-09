import requests
import time
import os
from content_analyzer import ContentAnalyzer
from audio_processing import DownloadAndAnalyzeAudio
from log_call_id import Call

BASE_URL = "https://api.hubapi.com"
ACCESS_TOKEN = os.getenv("hubspot_token")

# Stage ID và Pipeline ID
STAGE_ID = 'decisionmakerboughtin' # stage chốt giao dịch
PIPELINE_ID = 'default' # pipeline chốt deal

# Lấy danh sách deals trong pipeline và stage này
url = f"{BASE_URL}/crm/v3/objects/deals/search"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
data = {
    "filterGroups": [
        {
            "filters": [
                {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
                {"propertyName": "dealstage", "operator": "EQ", "value": STAGE_ID}
            ]
        }
    ],
    "properties": ["dealname", "dealstage"],
    "limit": 1
}

def delete_files(file_paths):
    """Xóa file nếu tồn tại"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print(f"File {file_path} does not exist.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

def analyze_and_log_call(recording_url, call_id):
    audio = DownloadAndAnalyzeAudio(recording_url)
    audio.download_audio()
    speech_to_text, result = audio.analyze_sentiment_from_audio()

    api_key = os.getenv("api_key")
    analyzer = ContentAnalyzer(api_key, result)
    analysis_result = analyzer.analyze_content(speech_to_text)
    summary = analyzer.generate_summary(analysis_result)

    log_call = Call(call_id, ACCESS_TOKEN, BASE_URL)
    log_call.log_call_description(summary)

    file_paths = ["cuoc-goi.mp3", "temp_audio.wav"]
    delete_files(file_paths)
    
def fetch_call_recordings():
    """Gửi request để lấy deals trong pipeline và stage đã chỉ định"""
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        deals = response.json()
        for deal in deals.get('results', []):
            print(f"Deal ID: {deal['id']}, Deal Name: {deal['properties']['dealname']}")

            # Lấy thông tin các cuộc gọi liên quan đến deal này
            call_url_api = f"{BASE_URL}/engagements/v1/engagements/associated/deal/{deal['id']}/paged"
            call_response = requests.get(call_url_api, headers=headers)

            if call_response.status_code == 200:
                calls_data = call_response.json()

                # Duyệt qua các cuộc gọi và kiểm tra ghi âm
                for call in calls_data.get('results', []):
                    if call.get('engagement', {}).get('type') == 'CALL':
                        call_id = call.get('engagement', {}).get('id')
                        recording_url = call.get('metadata', {}).get('recordingUrl', None)
                        description = call.get('metadata', {}).get('body', '').strip()

                        if recording_url and not description:
                            print(f"Call ID {call_id}: No description available.")
                            analyze_and_log_call(recording_url, call_id)

            else:
                print(f"Error fetching calls for Deal ID {deal['id']}: {call_response.status_code} - {call_response.text}")
    else:
        print(f"Error fetching deals: {response.status_code} - {response.text}")

if __name__ == "__main__":
    while True:
        fetch_call_recordings()
        time.sleep(120)
