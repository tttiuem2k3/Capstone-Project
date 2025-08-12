import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def get_clean_text_content(url, baibaothu):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Tìm khối nội dung chính
            content_div = soup.find('div', id='ftwp-postcontent')
            if not content_div:
                print(f"Bài báo thứ {baibaothu}: Không tìm thấy khối nội dung chính!")
                return None
            
            # Xoá tất cả các div có class "content_insert"
            for insert_div in content_div.find_all('div', class_='content_insert'):
                insert_div.decompose()
            
            for mucluc in content_div.find_all('div', class_='ftwp-in-post ftwp-float-center'):
                mucluc.decompose()
                
            allowed_tags = ['p','h2', 'h3', 'h4', 'h5', 'ul']
            content_lines = []

            for tag in content_div.find_all(allowed_tags, recursive=True):
                text = tag.get_text()
                if text:
                    content_lines.append(text)

            content = '\n'.join(content_lines)
            if content.strip() =="":
                print(f"Bài báo thứ {baibaothu}: Không có nội dung!")
                return None
            return content
        else:
            print(f"Không thể truy cập bài báo thứ {baibaothu}. Mã trạng thái: {response.status_code}")
            return None
    except Exception as e:
        print(f"Bài báo thứ {baibaothu} bị lỗi xử lý URL: {e}")
        return None
# Hàm main
def save_data():
    
    
    # Tên file CSV lưu bài báo
    csv_file = 'disease.csv'
    # csv_file2 = 'disease2.csv'
    # Kiểm tra nếu file CSV đã tồn tại, chưa tồn tại thì tạo mới
    if os.path.exists(csv_file):
        df_existing = pd.read_csv(csv_file, encoding='utf-8')
    else:
        df_existing = pd.DataFrame(columns=['Title', 'Document', 'Source'])
    
    articles = {}
    with open("link_all.txt", "r", encoding="utf-8") as file:
        for line in file:
            if "|" in line:
                title, link = line.strip().split(" | ")
                articles[title] = link
                
    print(f"Đã tìm thấy {len(articles)} bài viết.")
    print(f"Đang thu thập dữ liệu......\n")
    baibaothu=1
    for title, link in articles.items():
        # if baibaothu % 100 == 0:
        #     print(f"Tiến độ: {baibaothu}/{len(articles)}")
        # Kiểm tra xem link đã tồn tại trong CSV chưa
        if link in df_existing['Source'].values:
            # print(f"Bài báo thứ {baibaothu} đã tồn tại trong dữ liệu => bỏ qua")
            baibaothu+=1
            continue
        
        print(f"Bài báo thứ {baibaothu} crawl: {link}")
        content = get_clean_text_content(link,baibaothu)
        
        if content == None:
            baibaothu+=1
            continue
        
        # print(f"Bài báo thứ {baibaothu} đã được crawl: {title} -- {content[0:40]}")
        
        # Tạo DataFrame với dữ liệu mới
        df_new = pd.DataFrame({
            'Title': [title],
            'Document': [content],
            'Source': [link],  # Lưu trực tiếp link bài viết
            })
                   
        # Kết hợp dữ liệu hiện có với dữ liệu mới
        df_existing = pd.concat([df_existing, df_new], ignore_index=True)
        baibaothu+=1
        

    #Lưu dữ liệu vào file CSV với encoding utf-8
    # df_existing.to_csv(csv_file, index=False, encoding='utf-8')
    # print(f"Dữ liệu đã được lưu vào {csv_file}")

save_data()