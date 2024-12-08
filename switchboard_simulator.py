from mutagen.mp3 import MP3
from io import BytesIO
import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("hubspot_token")

# Endpoint API tạo cuộc gọi
url = "https://api.hubapi.com/engagements/v1/engagements"

recording_url = "https://ia600805.us.archive.org/3/items/gia-lap-cuoc-goi_202411/gia-lap-cuoc-goi.mp3"

def download_get_duration(recording_url):
    # Tải file âm thanh từ URL
    response = requests.get(recording_url)
    # Đọc metadata để lấy thời lượng (giay)
    audio = MP3(BytesIO(response.content))
    duration_seconds = int(audio.info.length)

    file_name = "cuoc-goi.mp3"

    if not os.path.exists(file_name):
        with open(file_name, 'wb') as f:
            f.write(response.content)
        # print(f"File {file_name} tải thành công.")
    else:
        print(f"File {file_name} đã tồn tại. Bỏ qua bước tải.")

    return str(duration_seconds * 1000)

def delete_files(file_paths):
    # Xóa file nếu tồn tại
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print(f"File {file_path} does not exist.")
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

data = {
    "engagement": {
        "active": True,
        "type": "CALL",
        "timestamp": int(time.time() * 1000),  # Thời gian cuộc gọi
        "ownerId": 1521059153, # Anh Ngô Hoàng Lan
    },
    "associations": {
        "contactIds": [66216837419],
        "dealIds": [28697947754],
    },
    "metadata": {
        # "body": "This is a note describing the details of the call.",
        "toNumber": "+1234567890",
        "fromNumber": "+0987654321",
        "status": "COMPLETED",
        "recordingUrl": recording_url,
        "direction": "OUTBOUND",
        "durationMilliseconds": download_get_duration(recording_url),   # Thời lượng tính bằng mili giây
    },
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Cuộc gọi đã được tạo thành công:", response.json())
    file_paths = ["cuoc-goi.mp3"]
    delete_files(file_paths)
else:
    print("Lỗi:", response.status_code, response.json())
