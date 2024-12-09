from langchain_google_genai import ChatGoogleGenerativeAI
from datetime import datetime
from textblob import TextBlob
import re
from collections import Counter

class GeminiHandler:
    def __init__(self, api_key):
        self.gemini_handler = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-pro")

    def invoke(self, messages):
        return self.gemini_handler.invoke(messages)

class ContentAnalyzer(GeminiHandler):
    def __init__(self, api_key, result):
        super().__init__(api_key)
        self.result = result

    def analyze_content(self, transcription):
        """Phân tích nội dung từ transcription"""
        basic_analysis = self.basic_analysis(transcription)
        sentiment_topics = self.analyze_sentiment_and_topics(transcription)
        keywords = self.extract_keywords(transcription)
        intent = self.analyze_intent(transcription)

        purchase_intent = self.analyze_purchase_intent(transcription)

        analysis_result = {
            "basic_analysis": basic_analysis,
            "sentiment_and_topics": sentiment_topics,
            "keywords": keywords,
            "intent": intent,
            "purchase_intent": purchase_intent,
            "timestamp": datetime.now().isoformat()
        }

        return analysis_result

    def basic_analysis(self, text):
        """Phân tích cơ bản về text"""
        # Tách câu đơn giản bằng dấu chấm và chấm hỏi
        sentences = re.split('[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Tách từ đơn giản bằng khoảng trắng
        words = text.split()

        return {
            "sentence_count": len(sentences),
            "word_count": len(words),
            "estimated_duration_minutes": len(words) / 150,
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "text_length": len(text)
        }

    def analyze_purchase_intent(self, text):
        """Phân tích khả năng mua hàng từ nội dung hội thoại"""
        try:
            prompt = f"""
            Vui lòng phân tích khả năng mua hàng của khách hàng dựa trên đoạn hội thoại sau và trả về với chính xác các thông tin:
            1. Mức độ quan tâm đến sản phẩm
            2. Yếu tố thúc đẩy quyết định mua hàng (giá cả, tính năng, chất lượng, bảo hành, v.v.)
            3. Khả năng khách hàng sẽ mua sản phẩm (đánh giá từ 1 đến 10)

            Hội thoại: {text}
            """

            response = self.gemini_handler.invoke(prompt)

            return response.content

        except Exception as e:
            print(f"Error in purchase intent analysis: {str(e)}")
            return {
                "interest_level": "low",
                "factors_influencing_purchase": ["unknown"],
                "purchase_probability": 0
            }

    def analyze_sentiment_and_topics(self, text):
        """Phân tích sentiment và topics"""
        try:
            prompt = f"""
            Vui lòng phân tích đoạn hội thoại sau và trả về với chính xác các thông tin:
            1. Sentiment:
               - Nhãn (tích cực/tiêu cực/trung tính)
               - Điểm (-1 đến 1)
               - Lý do đánh giá
            2. Chủ đề chính:
               - Liệt kê 3-5 chủ đề chính
               - Mức độ quan trọng của mỗi chủ đề (1-10)
            3. Tổng quan cảm xúc:
               - Các cảm xúc chính được thể hiện
               - Mức độ mạnh yếu của cảm xúc

            Hội thoại: {text}
            Biết rằng đoạn hội thoại trên có điểm cảm xúc là:
            Tiêu cực: {self.result['tiêu cực']}, Trung tính: {self.result['trung tính']}, Tích cực: {self.result['tích cực']}
            """

            response = self.gemini_handler.invoke(prompt)

            return response.content

        except Exception as e:
            print(f"Error in sentiment and topics analysis: {str(e)}")
            blob = TextBlob(text)
            return {
                "sentiment": {
                    "label": "neutral",
                    "score": blob.sentiment.polarity,
                    "reason": "Automatic fallback analysis"
                },
                "topics": [{"topic": "unknown", "importance": 5}],
                "emotional_overview": {
                    "emotions": ["unknown"],
                    "intensity": "medium"
                }
            }

    def extract_keywords(self, text):
        """Trích xuất từ khóa quan trọng"""
        words = re.findall(r'\b\w+\b', text.lower())

        # Đếm tần suất
        word_freq = Counter(words)

        # Lấy top từ khóa
        keywords = {}
        for word, freq in word_freq.most_common(15):
            if len(word) > 3:  # Chỉ lấy từ có độ dài > 3
                score = freq * (1 + len(word) / 100)
                keywords[word] = {
                    "frequency": freq,
                    "importance_score": round(score, 2)
                }

        return keywords

    def analyze_intent(self, text):
        """Phân tích intent của cuộc hội thoại"""
        try:
            prompt = f"""
            Phân tích ý định trong đoạn hội thoại sau và trả về với các thông tin:
            1. Mục đích chính của cuộc hội thoại
            2. Các yêu cầu hoặc đề nghị cụ thể được đưa ra
            3. Các cam kết hoặc hứa hẹn
            4. Các việc cần theo dõi hoặc thực hiện tiếp
            5. Mức độ khẩn cấp/ưu tiên của các việc cần làm

            Hội thoại: {text}
            Biết rằng đoạn hội thoại trên có điểm cảm xúc là:
            Tiêu cực: {self.result['tiêu cực']}, Trung tính: {self.result['trung tính']}, Tích cực: {self.result['tích cực']}
            """

            response = self.gemini_handler.invoke(prompt)

            return response.content

        except Exception as e:
            print(f"Error in intent analysis: {str(e)}")
            return {
                "error": "Could not analyze intent",
                "main_purpose": "unknown",
                "requests": [],
                "commitments": [],
                "action_items": []
            }

    def generate_summary(self, analysis_result):
        """Tạo báo cáo tổng hợp"""
        try:
            prompt = f"""
            Dựa trên kết quả phân tích sau, tạo bản tổng hợp ngắn gọn bằng tiếng Việt:
            {analysis_result}

            Hãy tạo nội dung với các mục dưới đây:
            1. Tóm tắt nội dung chính (3-5 điểm)
            2. Đánh giá tổng quan (sentiment, mức độ hiệu quả của cuộc hội thoại)
            3. Các việc cần thực hiện (sắp xếp theo độ ưu tiên)
            4. Đề xuất cải thiện (nếu có)
            5. Khả năng mua hàng của khách hàng (mức độ quan tâm và khả năng mua sản phẩm)

            Vui lòng format theo đúng với các mục dưới đây (ví dụ mẫu đi kèm):
            1. Tóm tắt nội dung chính
                - [Điểm 1]
                - [Điểm 2]
                - ...
            2. Đánh giá tổng quan
                - Sentiment:
                - Mức độ hiệu quả:
                - Lý do:
            3. Các việc cần thực hiện
                - [Việc cần làm 1]
                - [Việc cần làm 2]
                - ...
            4. Đề xuất cải thiện
                - Đề xuất 1
            5. Khả năng mua hàng của khách hàng
                - Mức độ quan tâm:
                - Khả năng mua:
                - Lý do:
            """

            response = self.gemini_handler.invoke(prompt)
            summary = response.content.replace('**', '').replace('*', '')
            formatted_summary = ContentAnalyzer.format_summary(summary)

            return formatted_summary
        
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {"error": "Could not generate summary"}
        
    @staticmethod
    def format_summary(summary):
        try:
            content_main = summary.split('Đánh giá tổng quan')[0].strip()
            content_overview = summary.split('Đánh giá tổng quan')[1].split('Các việc cần thực hiện')[0].strip()
            tasks = summary.split('Các việc cần thực hiện')[1].split('Đề xuất cải thiện')[0].strip()
            suggestions = summary.split('Đề xuất cải thiện')[1].split('Khả năng mua hàng của khách hàng')[0].strip()
            purchase_ability = summary.split('Khả năng mua hàng của khách hàng')[1].strip()
        except IndexError:
            # Xử lý khi thiếu một phần nào đó
            content_main = content_overview = tasks = suggestions = purchase_ability = ''

        # Hàm loại bỏ số đánh thứ tự ở cuối mỗi mục
        def remove_numbered_items(content):
            return re.sub(r'\s?\d+\.', '', content).strip()  # Xóa số và dấu chấm ở cuối

        # Tạo HTML cho các phần
        html = f"""
            <h3>📋 Tóm Kết Cuộc Gọi</h3>

            <div class="summary-section">
                <h4>🔍 Tóm Tắt Nội Dung Chính</h4>
                <ul>
                    {''.join(f'<li>{remove_numbered_items(item)}</li>' for item in content_main.split('- ')[1:] if item.strip())}
                </ul>
            </div>

            <div class="summary-section">
                <h4>📊 Đánh Giá Tổng Quan</h4>
                <p>{remove_numbered_items(content_overview)}</p>
            </div>

            <div class="summary-section">
                <h4>✅ Các Việc Cần Thực Hiện</h4>
                <ul>
                    {''.join(f'<li>{remove_numbered_items(item)}</li>' for item in tasks.split('- ')[1:] if item.strip())}
                </ul>
            </div>

            <div class="summary-section">
                <h4>💡 Đề Xuất Cải Thiện</h4>
                <p>{remove_numbered_items(suggestions)}</p>
            </div>

            <div class="summary-section">
                <h4>💰 Khả Năng Mua Hàng</h4>
                <p>{remove_numbered_items(purchase_ability)}</p>
            </div>
        """
        return html