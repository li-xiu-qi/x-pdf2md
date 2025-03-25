from .remote_image_config import BASE_URL, IMAGE_SERVER
import requests
from typing import Optional, Tuple
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

logger = logging.getLogger(__name__)

class ImageUploader:
    """图片上传处理类"""

    def __init__(self, server_url: str = None, max_retries: int = 3, timeout: int = 10):
        """
        初始化图片上传器
        
        参数:
            server_url: 图片服务器的URL，如果不提供则使用配置文件中的设置
            max_retries: 最大重试次数
            timeout: 请求超时时间(秒)
        """
        self.server_url = server_url or IMAGE_SERVER['base_url']
        self.server_url = self.server_url.rstrip('/')
        self.timeout = timeout
        
        # 配置重试策略
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
    def get_absolute_url(self, relative_path: str) -> Optional[str]:
        """
        将相对路径转换为完整的URL地址
        
        参数:
            relative_path: 图片的相对路径
            
        返回:
            str: 完整的URL地址
            None: 如果输入路径为None
        """
        if relative_path is None:
            return None
        if relative_path.startswith(('http://', 'https://')):
            return relative_path
        return f"{self.server_url}/{relative_path.lstrip('/')}"
    
    def upload(self, image_path: str) -> Optional[str]:
        """上传图片到服务器"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"文件不存在: {image_path}")
                return None

            # 获取文件名
            filename = os.path.basename(image_path)
            
            with open(image_path, 'rb') as f:
                # 使用元组格式指定文件名
                files = {
                    'file': (filename, f, 'image/jpeg')  
                }
                logger.info(f"正在上传文件 {image_path} 到 {self.server_url}/image_upload")
                response = self.session.post(
                    f"{self.server_url}/image_upload",
                    files=files,
                    timeout=self.timeout
                )
                
            if response.status_code == 200:
                result = response.json()
                url = result.get('url')
                if url:
                    # 服务器返回的是相对路径 'images/xxx.jpg'，需要拼接完整URL
                    absolute_url = f"{self.server_url}/{url}"
                    logger.info(f"上传成功，URL: {absolute_url}")
                    return absolute_url
                else:
                    logger.error("服务器返回的URL为空")
                    return None
            else:
                logger.error(
                    f"上传失败: HTTP {response.status_code}\n"
                    f"响应内容: {response.text}\n"
                    f"请求URL: {self.server_url}/image_upload"
                )
                return None
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"服务器连接失败: {str(e)}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"上传图片时发生错误: {str(e)}")
            return None

    def check_server(self) -> Tuple[bool, str]:
        """检查服务器是否可用"""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                return True, "服务器运行正常"
            return False, f"服务器返回异常状态码: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, f"无法连接到服务器 {self.server_url}"
        except Exception as e:
            return False, f"检查服务器时发生错误: {str(e)}"


# 使用当前目录下的car.png作为测试图片
if __name__ == "__main__":
    # 配置日志输出
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    uploader = ImageUploader(server_url="http://localhost:8100")  # 明确指定服务器地址
    print(f"使用服务器地址: {uploader.server_url}")
    
    # 首先检查服务器状态
    status, message = uploader.check_server()
    if not status:
        print(f"服务器检查失败: {message}")
        exit(1)
        
    print("服务器连接正常，开始上传图片...")
    image_url = uploader.upload("car.png")
    if image_url:
        print(f"图片上传成功，URL为: {image_url}")
    else:
        print("图片上传失败，请检查日志获取详细信息")