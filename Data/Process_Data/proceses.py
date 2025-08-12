import pandas as pd
from sklearn.model_selection import train_test_split

# Đọc file CSV tổng
df = pd.read_csv('disease_QA_v2.csv')  # Thay 'data.csv' bằng tên file của bạn

# Xáo trộn toàn bộ dữ liệu trước khi chia
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

train_df = df.copy()
# Tính toán số mẫu cho val và test
total_samples = len(df)
print(f"Tổng số mẫu: {total_samples}")
val_size = int(total_samples * 0.10)
test_size = int(total_samples * 0.05)

# Chia test set trước
test_df = df.iloc[:test_size]
remaining_df = df.iloc[test_size:]

# Chia tiếp val set từ phần còn lại
val_df = remaining_df.iloc[:val_size]

# Xuất ra file CSV riêng biệt
train_df.to_csv('disease_QA_v2_train.csv', index=False, encoding="utf-8-sig")
val_df.to_csv('disease_QA_v2_val.csv', index=False, encoding="utf-8-sig")
test_df.to_csv('disease_QA_v2_test.csv', index=False, encoding="utf-8-sig")

print(f"Số mẫu train: {len(train_df)}")
print(f"Số mẫu val: {len(val_df)}")
print(f"Số mẫu test: {len(test_df)}")
