import os

# 服务器配置
HOST = "0.0.0.0"
PORT = 8100
BASE_URL = f"http://{HOST}:{PORT}"

# 上传配置
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "upload_images")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 图片名称映射文件路径
IMAGE_NAMES_FILE = os.path.join(os.path.dirname(__file__), "image_names.json")

# 图片服务器配置
IMAGE_SERVER = {
    "base_url": BASE_URL,
    'timeout': 10,
    'max_retries': 3
}
