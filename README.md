# x-pdf2md

![alt text](assets/images/d99084735737c77dc3d3304cb78a411f.png)
一个基于paddle平台版面检测，公式识别等模型及多模态模型构建的强大的工具，用于将PDF文档转换为Markdown格式，同时保留文档的结构和布局。

## 功能特点

- PDF到图像的转换
- 智能页面布局分析
- 自动区域识别（文本、表格、图像、公式等）
- OCR文本提取
- 图表描述生成
- 表格内容提取
- 公式识别
- 支持图像上传到远程服务器
- 生成格式美观的Markdown文档

## 后续计划

- [ ] 使用批处理优化处理效率
- [ ] 支持非OCR模式，灵活处理图片和文本
- [ ] 支持更灵活的模型切换以及模式选择

## 安装

### 前提条件

- Python 3.10
- 安装依赖包：

```bash
pip install -r requirements.txt
```

### 配置

在`.env`文件中配置必要的API密钥（用于VLM功能）：

```
API_KEY=your_api_key_here
```

## 使用方法

### 命令行调用

基本用法：

```bash
python process_pdf.py -p input.pdf --output output_directory --output-md result.md
```

### 通过Python脚本调用

您也可以在自己的Python代码中直接调用x-pdf2md的核心功能：

```python
from process_pdf import process_pdf_document
from format_res import format_pdf_regions
from remote_image import default_uploader

# 1. 处理PDF文档，获取区域列表
regions = process_pdf_document(
    pdf_path="your_document.pdf",
    output_dir="output_directory",
    start_page=0,          # 起始页码（从0开始）
    end_page=None,         # 可选，结束页码
    dpi=300,               # 图像分辨率
    threshold_left_right=0.9,  # 左右栏阈值
    threshold_cross=0.3,   # 跨栏阈值
)

# 2. 格式化区域为Markdown
# 如果不需要上传图片，可以传入None，默认使用default_uploader上传到本地的8100端口
formatted_pages = format_pdf_regions(
    page_regions=regions, 
    image_uploader=default_uploader  # 或传入None不上传图片
)

# 3. 将结果保存到Markdown文件
output_path = "result.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n\n---\n\n".join(formatted_pages))

print(f"Markdown文件已保存到: {output_path}")
```

#### 自定义图片上传器

如果需要使用自定义的图片上传功能，可以实现自己的上传类：

```python
from remote_image.image_uploader import ImageUploader

class MyCustomUploader(ImageUploader):
    def upload(self, image_path: str) -> str:
        # 实现自定义上传逻辑
        # 返回上传后的URL
        return "https://example.com/image.jpg"

# 使用自定义上传器
my_uploader = MyCustomUploader()
formatted_pages = format_pdf_regions(regions, my_uploader)
```

### 启动和使用图片服务

如果您希望将图片存储在远程服务器上而不是使用本地路径，需要启动内置的图片服务。这对于需要在不同设备上查看生成的Markdown文档特别有用。

#### 1. 配置图片服务

在`remote_image/remote_image_config.py`中配置服务参数：

```python
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
```

#### 2. 启动图片服务

```bash
# 进入项目目录
cd x-pdf2md

# 启动图片服务
python -m remote_image.image_serve
```

服务启动后，您可以访问 <http://localhost:8100> 查看图片管理界面。

#### 3. 在PDF处理时启用图片上传

命令行方式：

```bash
python process_pdf.py -p your_document.pdf -o output_dir --upload --output-md result.md
```

Python脚本方式：

```python
from process_pdf import process_pdf_document
from format_res import format_pdf_regions
from remote_image import default_uploader

# 确保先启动图片服务
regions = process_pdf_document(
    pdf_path="your_document.pdf",
    output_dir="output_directory"
)

# 使用默认上传器(将图片上传到配置的服务器)
formatted_pages = format_pdf_regions(
    page_regions=regions, 
    image_uploader=default_uploader
)

# 保存结果
with open("result.md", "w", encoding="utf-8") as f:
    f.write("\n\n---\n\n".join(formatted_pages))
```

#### 4. 图片服务API

图片服务提供以下API：

- `POST /image_upload` - 上传图片
- `GET /api/images` - 获取已上传图片列表
- `GET /images/{filename}` - 访问上传的图片
- `GET /health` - 健康检查

### 参数说明

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `-p, --pdf` | PDF文件路径 | - |
| `-o, --output` | 输出目录路径 | - |
| `-s, --start_page` | 起始页码（从0开始） | 0 |
| `-e, --end_page` | 结束页码 | None |
| `-d, --dpi` | 图像分辨率 | 300 |
| `--threshold_lr` | 左右栏阈值 | 0.9 |
| `--threshold_cross` | 跨栏阈值 | 0.3 |
| `--no-filter` | 不过滤区域 | False |
| `--upload` | 启用图片上传 | False |
| `--output-md` | Markdown输出文件路径 | output.md |

## 项目结构

```
x-pdf2md/
├── process_pdf.py         # 主程序入口
├── format_res.py          # 格式化处理模块
├── pdf_utils/             # PDF处理工具
├── image_utils/           # 图像处理工具
│   ├── layout_utils/      # 布局分析工具
├── ocr_utils/             # OCR处理模块
├── image2md/              # 图像到Markdown转换工具
├── remote_image/          # 远程图像上传工具
│   ├── image_serve.py     # 图片服务器
│   ├── image_uploader.py  # 图片上传抽象类
│   └── remote_image_config.py # 图片服务配置
├── .env                   # 环境变量配置
└── README.md              # 项目文档
```

## 示例

将PDF转换为Markdown并上传图像：

```bash
python process_pdf.py -p document.pdf -o output_dir --upload --output-md result.md
```

## 注意事项

- 确保API密钥设置正确以使用VLM功能
- 对于大型PDF，建议增加内存分配
- 处理速度取决于PDF复杂度和页数
- 使用图片服务需确保配置的端口未被占用
- 如果需要在公网访问图片服务，请设置适当的安全措施

## 贡献

欢迎提交问题和拉取请求以改进此项目。
