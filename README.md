ffmpeg dùng để xử lý các tệp âm thanh và video, nếu chạy code mà bị báo lỗi liên quan ffmpeg thì tải chocolatey (https://chocolatey.org/install) và chạy câu lệnh `choco install ffmpeg` trong CMD hoặc Terminal.  

Chạy câu lệnh `pip install -r requirements.txt` để tải tất cả thư viện cần thiết.  

Ngoài ra để chạy được code thì phải có file .env có dạng:
```bash
api_key="your-gemini-api-key"
hubspot_token="access-token-your-hubspot"
```