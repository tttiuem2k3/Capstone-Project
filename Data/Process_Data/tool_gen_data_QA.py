from groq import Groq  
import random

# ====== 1. Load API Keys  ======
api_keys_llama = [
    # "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"
    # "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",
    # "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"
    # "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"
    "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"
]

# Hàm chọn API key ngẫu nhiên
def get_random_api_key(api_keys):
    return random.choice(api_keys)


class Llama3Model:
    def __init__(self, model_name: str, temperature: float, max_completion_tokens: int):
        self.model_name = model_name
        self.temperature = temperature
        self.max_completion_tokens = max_completion_tokens

    def __call__(self, prompt: str, title: str,  **kwargs):
        api_key = get_random_api_key(api_keys_llama)
        client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model=self.model_name,
            messages = [
                # {
                #     "role": "system",
                #     "content": f"Bạn là một AI sinh câu hỏi-đáp tiếng việt phục vụ huấn luyện mô hình Q&A y khoa. Dựa trên tài liệu sau về bệnh '{title}', hãy sinh ra tối đa 12 cặp câu hỏi-đáp. Mỗi câu hỏi bắt buộc chứa tên bệnh '{title}'.\nNội dung các câu hỏi tập trung vào: Khái niệm bệnh, Nguyên nhân, Triệu chứng, Dấu hiệu, Biến chứng, Điều trị, Phòng ngừa và các thông tin quan trọng khác từ tài liệu.\nTrả lời dưới dạng JSON Lines, mỗi dòng 1 object: {{\"question\": \"...\", \"answer\": \"...\"}}. Chỉ trả về JSON Lines, không thêm văn bản thừa.",
                # },
                {
                    "role": "user",
                    "content": f"Bạn là một AI sinh câu hỏi-đáp tiếng việt phục vụ huấn luyện mô hình Q&A y khoa. Dựa trên tài liệu sau về bệnh '{title}': {prompt}, hãy sinh ra tối đa 12 cặp câu hỏi-đáp. Mỗi câu hỏi bắt buộc chứa tên bệnh '{title}'.\nNội dung các câu hỏi tập trung vào: Khái niệm bệnh, Nguyên nhân, Triệu chứng, Dấu hiệu, Biến chứng, Điều trị, Phòng ngừa và các thông tin quan trọng khác từ tài liệu.\nTrả lời dưới dạng JSON Lines, mỗi dòng 1 object: {{\"question\": \"...\", \"answer\": \"...\"}}. Chỉ trả về JSON Lines, không thêm văn bản thừa."
                }
            ],
            temperature=self.temperature,
            max_completion_tokens=self.max_completion_tokens,
            top_p=1,
            stream=True,
            # response_format={"type": "json_object"},
            stop=None,
        )
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response

def get_llama3_model(model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct", 
                     max_completion_tokens: int = 8192, temperature: float = 1, **kwargs):
    return Llama3Model(model_name=model_name, 
                       temperature=temperature, 
                       max_completion_tokens=max_completion_tokens)

import pandas as pd
import json
import csv

# Load mô hình
llama_model = get_llama3_model()

# Đọc file CSV đầu vào
df = pd.read_csv("disease_document.csv")  
# df = pd.read_csv("disease_document.csv").head(1)

# Đọc file đã có câu hỏi & trả lời (QA)
try:
    df_check = pd.read_csv("disease_QA_1_v2.csv")
    processed_titles = set(df_check["Title"].unique())  # Dùng tập hợp để kiểm tra nhanh
except FileNotFoundError:
    processed_titles = set()  # Nếu file chưa tồn tại thì khởi tạo rỗng

results = []

for index, row in df.iterrows():
    title = row["Title"]
    # Nếu title đã có rồi thì bỏ qua
    if title in processed_titles:
        print(f"⚠️ Bỏ qua dòng {index + 1}/{len(df)}: {title} (đã xử lý)")
        continue
    print(f"Đang xử lý dòng {index + 1}/{len(df)}: {title}")  
    document = row["Document"]

    try:
        # Gọi mô hình
        response = llama_model(document, title)

        # Parse từng dòng JSON trong response
        for line in response.strip().split("\n"):
            try:
                qa = json.loads(line)
                results.append({
                    "Title": title,
                    "Question": qa["question"],
                    "Answer": qa["answer"],
                    "Type": "Hỏi về bệnh lý"
                })
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Lỗi xử lý ở dòng {index+1} ({title}): {e}")
        continue

# Lưu kết quả thành file CSV
print("Đã xử lý xong lưu kết quả vào file disease_QA.csv...")
pd.DataFrame(results).to_csv("disease_QA_1_v2_update.csv", index=False, encoding="utf-8-sig")
