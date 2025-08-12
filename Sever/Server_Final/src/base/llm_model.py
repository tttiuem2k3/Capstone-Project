# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
# from src import config

# model_ViT5_path = config.model_viT5_path  

# # Load mô hình và tokenizer
# tokenizer = AutoTokenizer.from_pretrained(model_ViT5_path)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_ViT5_path)

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print(f"\n======> Load Model ViT5-base to device: {device}\n")
# model.to(device)

# def answer_question_viT5(question, max_input_length=69, max_output_length=125):
#     inputs = tokenizer(
#         question,
#         return_tensors="pt",
#         truncation=True,
#         padding="max_length",
#         max_length=max_input_length
#     ).to(device)
    
#     with torch.no_grad():
#         output_ids = model.generate(
#             **inputs,
#             max_length=max_output_length,
#             num_beams=4,
#             early_stopping=True,
#             no_repeat_ngram_size=3,       
#             repetition_penalty=1.2    
#         )
    
#     answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
#     return answer

# ====== Mô hình thứ nhất: ViT5-base ======
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from src import config

model_ViT5_path = config.model_viT5_path  

tokenizer_viT5 = AutoTokenizer.from_pretrained(model_ViT5_path)
model_viT5 = AutoModelForSeq2SeqLM.from_pretrained(model_ViT5_path)

device_viT5 = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n======> Load Model Medical ViT5-base to device: {device_viT5}\n")
model_viT5.to(device_viT5)

def answer_question_viT5(question, max_input_length=69, max_output_length=125):
    inputs = tokenizer_viT5(
        question,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=max_input_length
    ).to(device_viT5)
    
    with torch.no_grad():
        output_ids = model_viT5.generate(
            **inputs,
            max_length=max_output_length,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,       
            repetition_penalty=1.2    
        )
    
    answer = tokenizer_viT5.decode(output_ids[0], skip_special_tokens=True)
    return answer

# ====== Mô hình thứ hai: Medical VinaLLaMA-2.7b-chat ======
from peft import (
    PeftConfig,
    PeftModel,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer as AutoTokenizerLlama,
    BitsAndBytesConfig,
)
import re

PEFT_MODEL = config.model_vinaLlama_path

peft_config = PeftConfig.from_pretrained(PEFT_MODEL)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

base_model_llama = AutoModelForCausalLM.from_pretrained(
    peft_config.base_model_name_or_path,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

tokenizer_llama = AutoTokenizerLlama.from_pretrained(PEFT_MODEL, trust_remote_code=True)
tokenizer_llama.pad_token = tokenizer_llama.eos_token
tokenizer_llama.padding_side = "right"

model_llama = PeftModel.from_pretrained(base_model_llama, PEFT_MODEL)
device_llama = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"======> Load Model Medical VinaLLaMA-2.7b to device: {device_llama}\n")

def build_prompt_llama(question):
    return (
        "<s>### Hướng dẫn:\n"
        "Bạn là một trợ lý y tế AI đáng tin cậy. Hãy trả lời các câu hỏi về y tế, bệnh học, chăm sóc sức khỏe bằng tiếng Việt một cách ngắn gọn, dễ hiểu, và chính xác. "
        "Nếu câu hỏi nằm ngoài chuyên môn hoặc chưa có đủ dữ liệu khoa học, hãy trả lời rằng 'Hiện tại tôi chưa có đủ thông tin để trả lời câu hỏi này.'\n"
        "### Câu hỏi:\n"
        f"{question}\n"
        "### Câu trả lời:\n"
    )

def extract_answer_llama(full_text):
    match = re.search(r'### Câu trả lời:\n(.+?)(###|$)', full_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return full_text.strip()

def ensure_complete_sentence_llama(answer):
    sentences = re.split(r'(?<=[.!?])\s+', answer.strip())
    if len(sentences) > 1:
        return ' '.join(sentences[:-1])  # loại bỏ câu cuối nếu nó chưa hoàn chỉnh
    return answer

def answer_question_vinaLlama(question, max_new_tokens=100):
    prompt = build_prompt_llama(question)
    inputs = tokenizer_llama(prompt, return_tensors="pt").to(device_llama)
    with torch.no_grad():
        outputs = model_llama.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.5,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            eos_token_id=tokenizer_llama.eos_token_id
        )

    full_answer = tokenizer_llama.decode(outputs[0], skip_special_tokens=True)
    extracted_answer = extract_answer_llama(full_answer)
    final_answer = ensure_complete_sentence_llama(extracted_answer)
    return final_answer