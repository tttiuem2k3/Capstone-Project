from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import config
from src.iot.iot_routes import router as iot_router 


# --------- App - FastAPI ----------------

app = FastAPI(
    title="Hệ thống thông minh hỗ trợ hỏi đáp về bệnh tậttật",
    version="1.0",
    description="Hệ thống IoT thông minh sử dụng FastAPI",
)
app.include_router(iot_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

import logging
logging.basicConfig(level=logging.INFO)

# Kiểm tra thiết bị CUDA
try:
    import torch
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        print(f"======> Device name: {device_name}")
    else:
        logging.info("CUDA is not available. Using CPU.")
except ImportError:
    logging.info("PyTorch is not installed. Cannot check CUDA device.")

"""
Run app - local: uvicorn src.app:app --host 127.0.0.1 --port 8000 --reload 
"""