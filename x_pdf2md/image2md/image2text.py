"""
#### 使用说明：

1. 初始化 `ImageTextExtractor` 实例时可以传入 `api_key`、`base_url`、`prompt` 或 `prompt_path`。
2. 使用 `extract_image_text` 方法可以提取图像中的文本并转换为 Markdown 格式。

#### 主要功能：
- 初始化时可以从环境变量读取 API 密钥，或者手动传入。
- 提供了从文件读取自定义提示文本的功能。
- 支持提取图像 URL 或本地图像文件路径中的文本。
- 将提取的文本转换为 Markdown 格式，包括数学公式的格式化。
- 支持图像 URL 或 Base64 编码图像的解析。
- 提供多种模型和生成文本的细节级别设置。

#### 参数说明：

- **`ImageTextExtractor.__init__`**：
  - `api_key` (str): API 密钥，默认从环境变量读取。
  - `base_url` (str): API 基础 URL，默认值为 "https://api.siliconflow.cn/v1"。
  - `prompt` (str | None): 提示文本，优先使用传入的值。
  - `prompt_path` (str | None): 提示文本文件路径，读取指定文件中的内容作为提示文本。

- **`ImageTextExtractor._read_prompt`**：
  - `prompt_path` (str): 提示文本文件路径。
  - 返回值 (str): 读取的提示文本内容。

- **`ImageTextExtractor.extract_image_text`**：
  - `image_url` (str | None): 图像的 URL 地址。
  - `local_image_path` (str | None): 本地图像文件路径。
  - `model` (str): 使用的模型名称，默认 "Qwen/Qwen2-VL-72B-Instruct"。
  - `detail` (str): 细节级别，允许值为 'low', 'high', 'auto'，默认 "low"。
  - `prompt` (str | None): 提示文本，优先使用传入的值。
  - `temperature` (float): 生成文本的温度参数，默认 0.1。
  - `top_p` (float): 生成文本的 top_p 参数，默认 0.5。
  - 返回值 (str): 提取的 Markdown 格式文本。

- **`ImageTextExtractor._is_base64`**：
  - `s` (str): 待检查的字符串。
  - 返回值 (bool): 如果是 Base64 编码则返回 True，否则返回 False。

- **`ImageTextExtractor._get_image_extension`**：
  - `file_path` (str): 图像文件路径。
  - 返回值 (str): 图像文件的扩展名。

#### 注意事项：
- `api_key` 是必须的，可以通过环境变量或初始化时传入。
- 需要安装 `PIL` 库来获取图像的扩展名。
- 图像文件必须是有效的图像格式，如 PNG、JPG 或 TIFF。
- 如果使用 Base64 编码的图像，确保传入的字符串是有效的 Base64 编码。

#### 更多信息：
- 该类依赖于 OpenAI 的 API 服务以及环境变量中的 API 密钥。
- 提取的 Markdown 格式文本会保留图像中的结构和公式，适用于文档集成。

"""
from x_pdf2md.config import get_model_config

_prompt = """
你是一个可以识别图片的AI，你可以基于图片与用户进行友好的对话。
"""

from openai import OpenAI
from dotenv import load_dotenv
import os
import base64


def extract_markdown_content(text: str) -> str:
    """
    从文本中提取Markdown内容，自动去除markdown和html代码块标记。

    参数:
    text (str): 输入文本。

    返回:
    str: 提取的内容，如果没有找到Markdown或HTML标记，则返回原始文本。
    """
    md_start_marker = "```markdown"
    html_start_marker = "```html"
    end_marker = "```"

    # 处理markdown代码块
    md_start_index = text.find(md_start_marker)
    if md_start_index != -1:
        start_index = md_start_index + len(md_start_marker)
        end_index = text.find(end_marker, start_index)
        
        if end_index == -1:
            return text[start_index:].strip()
        return text[start_index:end_index].strip()
    
    # 处理html代码块
    html_start_index = text.find(html_start_marker)
    if html_start_index != -1:
        start_index = html_start_index + len(html_start_marker)
        end_index = text.find(end_marker, start_index)
        
        if end_index == -1:
            return text[start_index:].strip()
        return text[start_index:end_index].strip()
    
    # 如果没有找到特定标记，返回原始文本
    return text.strip() if text else None


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码的字符串。

    参数:
    image_path (str): 图像文件路径。

    返回:
    str: Base64编码的字符串。
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


class ImageTextExtractor:
    """
    图像文本提取器类，用于将图像内容转换为 Markdown 格式的文本。
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.siliconflow.cn/v1",
        prompt: str | None = None,
        prompt_path: str | None = None,
    ):
        """
        初始化 ImageTextExtractor 实例。

        :param api_key: API 密钥，如果未提供则从环境变量中读取
        :param base_url: API 基础 URL
        :param prompt: 提示文本
        :param prompt_path: 提示文本文件路径
        """
        load_dotenv()
        self.api_key: str = api_key or os.getenv("API_KEY")

        if not self.api_key:
            raise ValueError("API key is required")

        self.client: OpenAI = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )
        self._prompt: str = (
            prompt or self._read_prompt(prompt_path)  or _prompt
        )

    def _read_prompt(self, prompt_path: str) -> str:
        """
        从文件中读取提示文本。

        :param prompt_path: 提示文本文件路径
        :return: 提示文本内容
        """
        if not prompt_path.endswith((".md", ".txt")):
            raise ValueError("Prompt file must be a .md or .txt file")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def extract_image_text(
        self,
        image_url: str = None,
        local_image_path: str = None,
        model: str = None,
        detail: str = "low",
        prompt: str = None,
        temperature: float = 0.1,
    ) -> str:
        """
        提取图像中的文本并转换为 Markdown 格式。

        :param image_url: 图像的 URL
        :param local_image_path: 本地图像文件路径
        :param model: 使用的模型名称
        :param detail: 细节级别，允许值为 'low', 'high', 'auto'
        :param prompt: 提示文本
        :param temperature: 生成文本的温度参数
        :param top_p: 生成文本的 top_p 参数
        :return: 提取的 Markdown 格式文本
        """
        if model is None:
            model = get_model_config('vlm')
        if not image_url and not local_image_path:
            raise ValueError("Either image_url or local_image_path is required")

        if image_url and not (
            image_url.startswith("http://")
            or image_url.startswith("https://")
            or self._is_base64(image_url)
        ):
            raise ValueError(
                "Image URL must be a valid HTTP/HTTPS URL or a Base64 encoded string"
            )

        if local_image_path:
            if not os.path.exists(local_image_path):
                raise FileNotFoundError(f"The file {local_image_path} does not exist.")
            image_extension: str = self._get_image_extension(local_image_path)
            with open(local_image_path, "rb") as image_file:
                base64_image: str = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/{image_extension};base64,{base64_image}"

        if detail not in ["low", "high", "auto"]:
            raise ValueError(
                "Invalid detail value. Allowed values are 'low', 'high', 'auto'"
            )

        if detail == "auto":
            detail = "low"

        prompt = prompt or self._prompt

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": detail},
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                stream=True,
                temperature=temperature,
            )

            result: str = ""
            for chunk in response:
                chunk_message: str = chunk.choices[0].delta.content
                result += chunk_message
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {e}")

    def _is_base64(self, s: str) -> bool:
        """
        检查字符串是否为 Base64 编码。

        :param s: 待检查的字符串
        :return: 如果是 Base64 编码则返回 True，否则返回 False
        """
        try:
            if isinstance(s, str):
                if s.strip().startswith("data:image"):
                    return True
                return base64.b64encode(base64.b64decode(s)).decode("utf-8") == s
            return False
        except Exception:
            return False

    def _get_image_extension(self, file_path: str) -> str:
        """
        获取图像文件的扩展名。

        :param file_path: 图像文件路径
        :return: 图像文件的扩展名
        """
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                return img.format.lower()
        except Exception as e:
            raise ValueError(f"Failed to determine image format: {e}")

