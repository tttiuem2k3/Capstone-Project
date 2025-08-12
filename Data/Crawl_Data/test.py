# # Đọc dữ liệu từ file a.txt và b.txt
# with open("List_disease.txt", "r", encoding="utf-8") as file_a:
#     a_lines = set(line.strip() for line in file_a if line.strip())

# with open("disease_list.txt", "r", encoding="utf-8") as file_b:
#     b_lines = set(line.strip() for line in file_b if line.strip())

# # Các dòng có trong b.txt nhưng không có trong a.txt
# only_in_b = b_lines - a_lines
# print("Các dòng chỉ có trong b.txt:")
# for line in only_in_b:
#     print(line)

# # Các dòng có trong a.txt nhưng không có trong b.txt
# only_in_a = a_lines - b_lines
# print("\nCác dòng chỉ có trong a.txt:")
# for line in only_in_a:
#     print(line)

import pandas as pd

def extract_and_save_disease_list(csv_path: str, output_path: str = "disease_list.txt"):
    df = pd.read_csv(csv_path)
    
    # Lấy cột title, loại bỏ trùng lặp, bỏ NA, strip khoảng trắng
    disease_list = df["Title"].dropna().apply(str.strip).unique().tolist()
    
    # Ghi vào file txt
    with open(output_path, "w", encoding="utf-8") as f:
        for disease in disease_list:
            f.write(f"{disease.lower()}\n")
    
    print(f"✅ Đã lưu {len(disease_list)} tên bệnh vào {output_path}")

extract_and_save_disease_list("disease_cleaned_final.csv")

# import pandas as pd
# # Cấu hình pandas hiển thị đầy đủ văn bản
# pd.set_option('display.max_colwidth', None)
# # Đọc file CSV (thay 'du_lieu.csv' bằng tên file thật của bạn)
# df = pd.read_csv('disease_cleaned_final.csv')

# # Lọc các dòng có title = "Ung thư tuyến tụy"
# filtered_df = df[df['Title'] == "Ung thư tuyến tụy"]

# # In ra nội dung của cột document tương ứng
# for doc in filtered_df['Document']:
#     print(doc)
