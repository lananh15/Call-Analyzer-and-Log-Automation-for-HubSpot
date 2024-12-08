import requests
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("hubspot_token")

BASE_URL = "https://api.hubapi.com"

class Call:
    def __init__(self, call_id, access_token, base_url):
        self.call_id = call_id
        self.access_token = access_token
        self.base_url = base_url

    def log_call_description(self, description):
        """Ghi log mô tả cho một cuộc gọi đã có ID"""
        url = f"{self.base_url}/engagements/v1/engagements/{self.call_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "engagement": {
                "type": "CALL",
            },
            "metadata": {
                "body": description
            }
        }
        response = requests.patch(url, json=data, headers=headers)

        if response.status_code == 200:
            print(f"Successfully updated Call ID {self.call_id} with description.")
        else:
            print(f"Failed to update Call ID {self.call_id}: {response.status_code} - {response.text}")


    def get_engagement_details(self):
        """Lấy thông tin chi tiết của cuộc gọi theo ID."""
        url = f"{self.base_url}/engagements/v1/engagements/{self.call_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print("Lỗi khi lấy thông tin chi tiết:", response.status_code, response.json())
            return None