from groq import Groq  
import random
import time
from src import config
api_keys_llama = config.api_keys_llama

def get_random_api_key(api_keys: list[str]) -> str:
    """Chọn ngẫu nhiên 1 API key từ danh sách."""
    return random.choice(api_keys)

class Llama4Model:
    def __init__(self, model_name: str, temperature: float, max_completion_tokens: int):
        self.model_name = model_name
        self.temperature = temperature
        self.max_completion_tokens = max_completion_tokens

    def __call__(self, prompt: str, history: list[str] | str, mode: int, **kwargs) -> str:
        # Chuẩn hóa lịch sử về dạng string nếu là list
        
        if isinstance(history, list):
            # Đánh số từ 1 trở đi, câu 1 là gần nhất
            history_str = "\n".join([f"  🟢 {i+1}. {q}" for i, q in enumerate(history)])
        else:
            history_str = history or ""
        print("🧠 ---- Lịch sử câu hỏi ----\n"+ history_str)
        api_key = get_random_api_key(api_keys_llama)
        client = Groq(api_key=api_key)
        if mode == 0:
            system_prompt = """
            Bạn là một AI thông minh trong việc phán đoán ý muốn của người dùng.
            Bạn sẽ dựa vào câu hỏi hiện tại và dữ liệu câu hỏi lịch sử được cung cấp để chuẩn hóa câu hỏi của người dùng về một câu hỏi cụ thể, ngắn gọn liên quan đến vấn đề về bệnh tật để tôi đưa vào mô hình hỏi đáp để sinh ra câu trả lời. 
            Nếu là câu hỏi về triệu chứng, tức là người dùng chưa biết mình bị bệnh gì và chỉ nêu ra các triệu chứng, ví dụ: 'Tôi hay bị ho dai dẳng', thì phải chuẩn hóa lại thành: 'Tôi hay bị ho dai dẳng. Tôi có thể đang bị bệnh gì?'
            Nếu là câu hỏi về bệnh lý, tức là người dùng sẽ hỏi về một bệnh cụ thể, các câu hỏi có tên của bệnh ở bên trong, ví dụ: 'Bệnh cúm là gì', 'Bệnh cúm có triệu chứng gì', 'Bệnh cúm điều trị thế nào','Bệnh cúm phòng ngừa ra sao',... hoặc các câu hỏi liên quan khác về bệnh lý miễn sao có chứa tên bệnh thì cần phải chuẩn hóa lại thêm dấu hỏi ở cuối câu nếu chưa có.
            Câu trả lời của bạn phải là câu hỏi đã được chuẩn hóa không bao gồm các ngữ cảnh khác chỉ hỏi về bệnh lý hoặc hỏi về các triệu chứng bệnh, không giải thích gì thêm, cũng không giải thích gì về lịch sử, lịch sử chỉ là ngữ cảnh phụ nếu như câu hỏi hiện tại không có đề cập đến bệnh hoặc triệu chứng. Ví dụ  câu hỏi hiện tại: 'Bệnh đó là gì', lịch sử:'hôm qua tôi đi đường vô tình thấy một con chó bị dại' thì sẽ chuẩn hóa thành câu hỏi: 'Bệnh dại là gì?' 
            Nếu câu hỏi không liên quan đến bệnh tật thì trả lời đúng fomat: 'Vui lòng đặt câu hỏi liên quan đến bệnh tật.'
            Dữ liệu lịch sử câu hỏi sẽ giúp bạn hiểu rõ hơn ngữ cảnh, xem nó có liên quan đến câu hỏi hiện tại hay không, để đưa ra chuẩn hóa phù hợp nhất. Nếu câu hỏi hiện tại đã liên quan đến bệnh tật thì không cần suy xét quá nhiều đến lịch sử trước đó.
            Dữ liệu lịch sử sẽ được đánh số từ 1 đến n, 1 là câu gần nhất.
            Nếu câu hỏi hiện tại có nghĩa là 'chưa nghe rõ' hoặc 'trả lời lại' thì hãy chuẩn hóa câu hỏi về bệnh tật gần nhất trong lịch sử.
            """
            user_prompt = f"Hãy chuẩn hóa thành câu hỏi về bệnh tật.\nCâu hỏi hiện tại: {prompt}\nLịch sử:\n{history_str}"
        else:
            system_prompt = """
            Bạn là một AI thông minh trong việc phán đoán ý muốn của người dùng.
            Bạn sẽ dựa vào câu hỏi hiện tại và dữ liệu các câu hỏi lịch sử được cung cấp để chuẩn hóa câu hỏi của người dùng về một câu hỏi cụ thể nếu câu hỏi hiện tại không đầy đủ ngữ cảnh. 
            Câu trả lời của bạn phải là câu hỏi đã được chuẩn hóa để thể hiện mong muốn của người dùng.
            Dữ liệu lịch sử câu hỏi sẽ giúp bạn hiểu rõ hơn ngữ cảnh, xem nó có liên quan đến câu hỏi hiện tại hay không, để đưa ra chuẩn hóa phù hợp nhất. Nếu câu hỏi hiện tại đã liên quan đến bệnh tật thì không cần suy xét quá nhiều đến lịch sử trước đó.
            Dữ liệu lịch sử sẽ được đánh số từ 1 đến n, 1 là câu gần nhất.
            Nếu câu hỏi hiện tại có nghĩa là 'chưa nghe rõ' hoặc 'trả lời lại' thì hãy chuẩn hóa câu hỏi về bệnh tật gần nhất trong lịch sử.
            """
            user_prompt = f"Câu hỏi đã được chuẩn hóa từ câu hỏi hiện tại là gì? (phản hồi của bạn chỉ là câu trả lời đã được chuẩn hóa, không giải thích gì thêm).\nCâu hỏi hiện tại: {prompt}\nLịch sử:\n{history_str}"
        try:
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
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
            return response.strip()
        except Exception as e:
            return prompt

def get_llama4_model(
    model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct", 
    max_completion_tokens: int = 65, 
    temperature: float = 1, 
    **kwargs
) -> Llama4Model:
    return Llama4Model(model_name=model_name, temperature=temperature, max_completion_tokens=max_completion_tokens)

def question_normalization(question: str, history: list[str] | str, mode: int) -> str:
    llama4_model = get_llama4_model()
    question_norma = llama4_model(prompt=question, history=history, mode=mode)
    return question_norma
