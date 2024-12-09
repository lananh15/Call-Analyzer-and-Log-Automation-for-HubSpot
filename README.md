## Chuẩn bị thư viện và biến môi trường
Chạy câu lệnh dưới đây để tải các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
Chuẩn bị file .env có dạng dưới đây để thiết lập các biến môi trường được sử dụng:
```bash
api_key="your-gemini-api-key"
hubspot_token="access-token-your-hubspot"
```
**Lưu ý:** Nếu đã chuẩn bị thư viện và biến môi trường nhưng chạy gặp lỗi liên quan ffmpeg (ffmpeg dùng để xử lý các tệp âm thanh và video) thì tải chocolatey (https://chocolatey.org/install) về máy và chạy câu lệnh `choco install ffmpeg` trong CMD hoặc Terminal. 

## Thiết lập theo dõi các deal trong một stage của một pipeline cụ thể
Trong file **hubspot/polling.py**, có thiết lập chọn theo dõi các deal trong stage "Chốt giao dịch" của pipeline "Chốt deal" bằng cách dùng ID của stage và pipeline:
```python
# Stage ID và Pipeline ID
STAGE_ID = 'decisionmakerboughtin' # stage chốt giao dịch
PIPELINE_ID = 'default' # pipeline chốt deal
```
Có thể thay đổi 2 ID trên để theo dõi một stage của một pipeline cụ thể trên Hubspot của bạn. Tham khảo code dưới đây để lấy ID của stage và pipeline mà bạn muốn:
```python
import requests
import os
from dotenv import load_dotenv

# Load HubSpot token từ .env
load_dotenv()
ACCESS_TOKEN = "access-token-your-hubspot"

BASE_URL = "https://api.hubapi.com"

# Hàm lấy danh sách pipelines
def get_pipelines():
    url = f"{BASE_URL}/crm/v3/pipelines/deals"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])

def get_pipeline_stages(pipeline_id):
    url = f"{BASE_URL}/crm/v3/pipelines/deals/{pipeline_id}/stages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("results", [])

# Hàm in ra tất cả các stage có trong các pipeline
def list_pipelines():
    pipelines = get_pipelines()
    for pipeline in pipelines:
        print(f"\nPipeline ID: {pipeline['id']} - Name: {pipeline['label']}")
        stages = get_pipeline_stages(pipeline['id'])
        for stage in stages:
            print(f"Stage ID: {stage['id']} - Name: {stage['label']}")

if __name__ == "__main__":
    list_pipelines()
```
## Triển khai sử dụng
Nếu chưa tích hợp tổng đài trả về URL ghi âm cuộc gọi thì có thể chạy file **switchboard_simulator.py** là file giả lập tổng đài gửi link URL ghi âm cuộc gọi về cho deal của một stage trong pipeline cụ thể trên Hubspot (bạn có thể chỉnh sửa ID của stage và pipeline cần theo dõi trong file này).  

Cuối cùng, chạy file **hubspot/polling.py** để tiến hành theo dõi và ghi log (nếu có) cho các deal trong stage của pipeline mà bạn đã thiết lập

## Quy trình dự án
### 1. Thu thập thông tin giao dịch và cuộc gọi
Sử dụng API của HubSpot để lấy danh sách các giao dịch (deals) nằm trong một pipeline và stage cụ thể (ở đây là các deal nằm trong stage "Chốt giao dịch" của pipeline "Chốt deal"). Với mỗi deal như vậy, truy xuất danh sách các cuộc gọi liên quan (call engagements), bao gồm thông tin như: ID của cuộc gọi và URL file ghi âm của cuộc gọi.  
Tuy nhiên với các cuộc gọi đã có mô tả (đã có log) thì không cần lấy các thông tin của cuộc gọi này (chỉ lấy các cuộc gọi chưa có log để xử lý phân tích).

### 2. Tải xuống và xử lý file ghi âm
Nếu cuộc gọi chưa có nội dung mô tả và giả sử là có URL file ghi âm (giả lập tổng đài gửi về): 
- Tải file ghi âm từ URL được cung cấp và chuyển đổi file MP3 sang định dạng WAV.
- Chuyển đổi định dạng âm thanh nếu cần thiết, đảm bảo file tương thích với các công cụ phân tích âm thanh (lưu ý nếu hệ thống không có định dạng âm thanh MP3 sẵn có, thư viện pydub sẽ gọi FFmpeg để thực hiện).

### 3. Chuyển đổi giọng nói thành văn bản (Speech-to-Text)
Sử dụng thư viện SpeechRecognition cho phép tích hợp dễ dàng với nhiều API nhận diện giọng nói khác nhau, bao gồm cả Google (ở đây dùng Google Speech Recognition) để trích xuất nội dung cuộc gọi. Kết quả là một đoạn văn bản nội dung trao đổi trong cuộc gọi.

### 4. Phân tích nội dung và cảm xúc
**Bước 1:** Tách văn bản thành câu và từ, sau đó tính toán số lượng câu, số lượng từ, thời gian ước tính để đọc, chiều dài trung bình của câu và tổng chiều dài văn bản. Xác định các từ khóa quan trọng và ý chính trong cuộc gọi và đếm tần suất để trích xuất các từ khóa quan trọng từ văn bản.

**Bước 2:** Sử dụng API của Gemini để phân tích mục đích chính của cuộc hội thoại, các yêu cầu cụ thể và các cam kết cần theo dõi.

**Bước 3:** Sử dụng model 5CD-AI/Vietnamese-Sentiment-visobert (có trên Huggingface) phân tích văn bản thu được để đánh giá cảm xúc (sentiment analysis) của cuộc gọi, xác định các trạng thái tích cực, tiêu cực hoặc trung tính.

**Bước 4:** Tiếp tục dùng API của Gemini, dựa trên nội dung hội thoại, trả về mức độ quan tâm, các yếu tố ảnh hưởng đến quyết định mua hàng và khả năng khách hàng sẽ mua sản phẩm.

**Bước 4:** Cuối cùng, tạo một bản tóm tắt nội dung chính, đánh giá tổng quan về cảm xúc, các việc cần thực hiện và khả năng mua hàng của khách hàng.

### 5. Ghi log thông tin vào HubSpot
Cập nhật mô tả (description) của cuộc gọi (với call_id đã được lấy ở trên) với nội dung tóm tắt vừa được phân tích.

### 6. Tự động hóa quy trình (với cơ chế kiểm tra định kỳ polling)
Lấy danh sách các giao dịch và cuộc gọi mới chưa được xử lý trong các deal nằm trong stage "Chốt giao dịch" của pipeline "Chốt deal". Và tự động kích hoạt các bước tải xuống, phân tích và ghi log. Đảm bảo hệ thống hoạt động liên tục với khoảng thời gian kiểm tra được cấu hình (ở đây là 2 phút).

### 7. Dọn dẹp dữ liệu tạm thời
Sau khi hoàn tất xử lý, xóa các file tạm (như file âm thanh đã tải xuống) để giải phóng tài nguyên và tối ưu hóa hiệu suất.
