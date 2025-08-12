import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import warnings
import logging
logging.getLogger("httpx").setLevel(logging.CRITICAL)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8888,
        reload=True,
        log_level="warning",
        access_log=False
    )
