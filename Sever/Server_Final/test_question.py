from src.base.prompt_normalization import question_normalization 
from src.base.llm_model import answer_question_viT5, answer_question_vinaLlama
def main():
    history = []
    print("=== Chương trình hỏi đáp về bệnh tật ===")
    print("Nhập 'exit' để thoát chương trình.\n")

    while True:
        # Nhập câu hỏi mới
        model = input("Chọn mô hình (1:Medical ViT5, 2:Medical VinaLlama): ").strip()
        question = input("Nhập câu hỏi: ").strip()
         
        if question.lower() == "exit":
            print("Thoát chương trình.")
            break
        if model == "1":
            print("Sử dụng mô hình Medical ViT5.")
            # Gọi hàm chuẩn hóa với lịch sử
            norm_question = question_normalization(question, history, 0)
            print(f"\nCâu hỏi đã chuẩn hóa: {norm_question}\n")
            answer = answer_question_viT5(norm_question)
        elif model == "2":
            print("Sử dụng mô hình Medical VinaLlama.")
            norm_question = question_normalization(question, history, 1)
            answer = answer_question_vinaLlama(norm_question)
        else:
            print("Lựa chọn mô hình không hợp lệ. Vui lòng chọn 1 hoặc 2.")
            print("-" * 40)
            continue
        print(f"Câu trả lời: {answer}\n")
        # Lưu câu hỏi vừa nhập vào lịch sử (đầu tiên)
        history.insert(0, question)  # Thêm vào đầu danh sách
        
        if len(history) > 7:
            history = history[:7]
            
        print("-" * 40)

if __name__ == "__main__":
    main()
