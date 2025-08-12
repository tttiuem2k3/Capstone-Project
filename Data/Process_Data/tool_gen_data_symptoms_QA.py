from groq import Groq  
import random

api_keys_llama = [
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
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là một AI thông minh để tạo ra các câu hỏi và câu trả lời cho câu hỏi đó dựa trên dữ liệu về bệnh được cung cấp. Các câu hỏi và câu trả lời cho câu hỏi về bệnh được tạo ra bằng cách hỏi các câu hỏi ở các ngữ cảnh khác nhau liên quan đến triệu chứng của bệnh có trong dữ liệu được cung cấp. Phản hồi của bạn bắt buộc ở dạng JSON với cấu trúc như sau: {\"question\": \"Câu hỏi\", \"answer\": \"Câu trả lời\"}\n{\"question\": \"Câu hỏi\", \"answer\": \"Câu trả lời\"}\n{\"question\": \"Câu hỏi\", \"answer\": \"Câu trả lời\"}\n{...câu hỏi và câu trả lời khác...}",
                },
                {
                    "role": "user",
                    "content": "Tạo các câu hỏi và câu trả lời về các triệu chứng để dẫn đến bệnh "+str(title)+" có trong dữ liệu sau: " + str(prompt)
                }
            ],
            temperature=self.temperature,
            max_completion_tokens=self.max_completion_tokens,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ""
        for chunk in completion:
            response += chunk.choices[0].delta.content or ""
        return response

def get_llama3_model(model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct", 
                     max_completion_tokens: int = 8192, temperature: float = 2, **kwargs):
    return Llama3Model(model_name=model_name, 
                       temperature=temperature, 
                       max_completion_tokens=max_completion_tokens)

import pandas as pd
import json
import csv

# Load mô hình
llama_model = get_llama3_model()

# Đọc file CSV đầu vào
df = pd.read_csv("disease_cleaned_final.csv")  
# df = pd.read_csv("disease_cleaned_final.csv").head(3)

# Đọc file đã có câu hỏi & trả lời (QA)
try:
    df_check = pd.read_csv("disease_QA.csv")
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
                    "Answer": qa["answer"]
                })
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Lỗi xử lý ở dòng {index+1} ({title}): {e}")
        continue

# Lưu kết quả thành file CSV
print("Đã xử lý xong lưu kết quả vào file disease_QA.csv...")
pd.DataFrame(results).to_csv("disease_QA_2.csv", index=False, encoding="utf-8-sig")

import pandas as pd

# Đọc file gốc
df = pd.read_csv("ViMedical_Disease.csv")

# Tạo cột mới
df["Title"] = df["Disease"]
df["Answer"] = "Bạn có thể đang bị bệnh " + df["Disease"] + "."
df["Type"] = "Hỏi về triệu chứng"

# Làm sạch xuống dòng trong 'Question'
df["Question"] = df["Question"].astype(str).str.replace(r'[\r\n]+', ' ', regex=True)

# Chọn cột cần xuất
df_final = df[["Title", "Question", "Answer", "Type"]]

# Lưu file
df_final.to_csv("disease_symptoms.csv", index=False, encoding="utf-8-sig")

import pandas as pd

# Đọc file
df_summary = pd.read_csv("disease_symptoms.csv")

# Đếm số lần xuất hiện mỗi giá trị trong cột Title
title_counts = df_summary["Title"].value_counts()

# Ghi ra file txt
with open("title_in_symptoms.txt", "w", encoding="utf-8") as f:
    for title, count in title_counts.items():
        f.write(f"{title}\n")


