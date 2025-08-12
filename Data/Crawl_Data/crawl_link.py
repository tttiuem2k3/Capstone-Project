import requests
from bs4 import BeautifulSoup
import os
from tkinter import messagebox

# Hàm để lấy danh sách link của các bài báo về bệnh có trên trang web
def get_all_links_paper_in_main_url(main_url):
    response = requests.get(main_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_tags = soup.find_all('div', class_='col-xs-6 col-sm-4 col-md-3')
        article_dict = {}

        for article in article_tags:
            a_tag = article.find('a', href=True)
            if a_tag and a_tag.text.strip():
                title = a_tag.text.strip()
                link = a_tag['href']
                if not link.startswith("http"):
                    link = "https://tamanhhospital.vn" + link
                article_dict[title] = link

        # ✅ Lưu vào file TXT
        with open("List_disease.txt", "w", encoding="utf-8") as file:
            for title, link in article_dict.items():
                file.write(f"{title}\n")

        print(f"Đã lưu {len(article_dict)} bài viết vào 'link_all.txt'")
        return article_dict
    else:
        messagebox.showerror("Lỗi", f"Không thể truy cập trang web. Mã trạng thái: {response.status_code}")
        return {}

# Gọi hàm
main_url = "https://tamanhhospital.vn/benh-hoc-a-z/"
print(f"Đang thu thập liên kết từ trang: {main_url}")
get_all_links_paper_in_main_url(main_url)
