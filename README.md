# 🤖 Hệ Thống Thông Minh Hỗ Trợ Hỏi Đáp Về Bệnh Tật

> Ứng dụng AI và IoT để xây dựng một hệ thống hỏi đáp tự động về bệnh tật bằng giọng nói, hỗ trợ người dùng tiếp cận thông tin y tế nhanh chóng, chính xác và thân thiện.

---

## ▶️ Video Demo
📺 Video demo hệ thống xem [tại đây](https://youtu.be/j2nC14IqkZw)

---

## 📜 Giới thiệu

Dự án **Hệ thống thông minh hỗ trợ hỏi đáp về bệnh tật** được thiết kế nhằm:
- Cung cấp **thông tin y tế chính xác** qua giao tiếp ngôn ngữ tự nhiên ( tổng hợp từ ~ 1000 loại bệnh phổ biến ở Việt Nam).
- Hỗ trợ mọi loại người dùng đặc biệt là **người dùng cao tuổi, người tàn tật, người có hạn chế về việc di chuyển** hoặc khó khăn trong việc sử dụng thiết bị công nghệ hoặc khi tra cứu thông tin y tế trực tuyến.
- Tích hợp **AI xử lý ngôn ngữ tự nhiên (NLP)**, **mô hình ngôn ngữ lớn (LLM)** và **phần cứng IoT** để tạo nên trải nghiệm tương tác mượt mà và tiện dụng.

---

## 🔧 Tính năng chính

- **Nhận diện giọng nói (STT)**: Chuyển đổi lời nói của người dùng thành văn bản.
- **Hỏi đáp tự động (QA)**: Sử dụng các mô hình AI như **VinaLLaMA 2.7B** và **ViT5** được fine-tune để trả lời câu hỏi.
- **Phát lại giọng nói (TTS)**: Đọc to câu trả lời cho người dùng.
- **Giao diện phần cứng trực quan**: Màn hình TFT LCD, đèn LED thông báo trạng thái, micro thu âm, loa phát âm thanh.
- **Kết nối IoT**: Tích hợp ESP32, giao tiếp với server qua FastAPI.

---

## 🛠️ Kiến trúc hệ thống

![Sơ đồ kiến trúc hệ thống](./Image/1.JPG)

Hệ thống gồm:
1. **Thiết bị phần cứng** (ESP32 + màn hình + micro + loa + Led).
2. **Server xử lý AI** (Mô hình NLP).
3. **Các API dịch vụ hỗ trợ** (Speech-to-Text, Text-to-Speech).

---

## 🧠 Công nghệ sử dụng

- **Ngôn ngữ lập trình**: Python, C++ (Arduino ESP32)
- **Framework**: FastAPI
- **Mô hình AI**: VinaLLaMA 2.7B, ViT5
- **Kỹ thuật tối ưu**: QLoRA, Fine-tuning, Prompt Tuning
- **Phần cứng**:
  - ESP32
  - Micro INMP441
  - Màn hình TFT LCD 2.4 inch
  - Loa mini
  - LED NeoPixel WS2812
  - 
---

## 🖼️ Hình ảnh minh họa
(Chèn hình ảnh từ báo cáo tại đây)

---

## 📊 Kết quả

| Mô hình | BLEU ↑ | ROUGE-2 ↑ | ROUGE-L ↑ |
|---------|--------|-----------|-----------|
| ViT5    | 0.92   | 0.88      | 0.90      |
| VinaLLaMA 2.7B | **0.9493** | **0.91**  | **0.93** |

---

## 💻 Hướng dẫn cài đặt & chạy

1. **Clone dự án**
   ```bash
   git clone https://github.com/username/medical-qa-ai.git
   cd medical-qa-ai
2. **Cài đặt môi trường**
   ```bash
   pip install -r requirements.txt
3. **Chạy server**
   ```bash
   uvicorn main:app --reload

---

##  📞 Liên hệ
- 📧 Email: tttiuem2k3@gmail.com
- 👥 Linkedin: [Thịnh Trần](https://www.linkedin.com/in/thinh-tran-04122k3/)
- 💬 Zalo - phone: +84 329966939 hoặc +84 336639775

---


   
