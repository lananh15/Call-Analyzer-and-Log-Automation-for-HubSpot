import requests
from pydub import AudioSegment
import speech_recognition as sr
import os

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Vietnamese-Sentiment-visobert'))

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)

class DownloadAndAnalyzeAudio:
    def __init__(self, recording_url):
        self.recording_url = recording_url
        self.file_name = ''

    def download_audio(self):
        # Tải file âm thanh từ URL
        response = requests.get(self.recording_url)
        self.file_name = "cuoc-goi.mp3"

        if not os.path.exists(self.file_name):
            with open(self.file_name, 'wb') as f:
                f.write(response.content)
            # print(f"File {self.file_name} tải thành công.")
        else:
            print(f"File {self.file_name} đã tồn tại. Bỏ qua bước tải.")
    
    # Chuyển đổi file MP3 sang WAV
    def convert_mp3_to_wav(self, wav_path):
        print(self.file_name)
        audio = AudioSegment.from_mp3(self.file_name)
        audio.export(wav_path, format="wav")
        # print('Đã chuyển đổi .mp3 sang .wav')

    def analyze_content(self, text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits

        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        class_scores = probabilities.squeeze().tolist()

        label_mapping = model.config.id2label  # e.g., {0: 'NEG', 1: 'NEU', 2: 'POS'}
        result = {label_mapping[i]: score for i, score in enumerate(class_scores)}
        return result

    # Phân tích cảm xúc từ file MP3
    def analyze_sentiment_from_audio(self):
        wav_file_path = "temp_audio.wav"

        try:
            # Kiểm tra và in ra thông tin file MP3 trước khi chuyển đổi
            print(f"File MP3 path: {self.file_name}")
            print(f"File MP3 exists: {os.path.exists(self.file_name)}")

            # Chuyển đổi file MP3 sang WAV
            self.convert_mp3_to_wav(wav_file_path)
            
            # Kiểm tra file WAV sau khi chuyển đổi
            print(f"WAV file path: {wav_file_path}")
            print(f"WAV file exists: {os.path.exists(wav_file_path)}")

            recognizer = sr.Recognizer()

            # Đọc file WAV
            with sr.AudioFile(wav_file_path) as source:
                audio_data = recognizer.record(source)  # Đọc toàn bộ file audio

            try:
                # Nhận dạng giọng nói từ file
                speech_to_text = recognizer.recognize_google(audio_data, language='vi-VI')
                # print(f"Recognized text: {speech_to_text}")
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
                speech_to_text = ""
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                speech_to_text = ""

            sentiment = self.analyze_content(speech_to_text)
            result = {
                'tiêu cực': sentiment.get('NEG'),
                'trung tính': sentiment.get('NEU'),
                'tích cực': sentiment.get('POS'),
            }
            print(result)
            
            return speech_to_text, result

        except Exception as ex:
            print(f"Unexpected error in analyze_sentiment_from_audio: {ex}")
            # In ra toàn bộ thông tin traceback để debug
            import traceback
            traceback.print_exc()
            
            # Trả về một tuple để tránh lỗi unpack
            return "", {}