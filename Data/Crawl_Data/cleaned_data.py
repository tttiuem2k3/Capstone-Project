import pandas as pd

# Đọc file CSV
df = pd.read_csv('disease_cleaned_final.csv')

# Hàm làm sạch văn bản trong cột 'Document'
def remove_empty_lines(text):
    if pd.isna(text):
        return text
    # Tách văn bản thành từng dòng, loại bỏ dòng trống, rồi ghép lại
    lines = text.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip() != '']
    return '\n'.join(non_empty_lines)

# Áp dụng hàm cho toàn bộ cột 'Document'
df['Document'] = df['Document'].apply(remove_empty_lines)

# Ghi ra file mới
df.to_csv('disease_cleaned_final1.csv', index=False, encoding='utf-8')

print("Đã loại bỏ dòng trống trong nội dung văn bản và lưu vào 'disease_cleaned.csv'")
