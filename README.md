# x-pdf2md

一个强大的工具，用于将PDF文档转换为Markdown格式，同时保留文档的结构和布局。

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

## 安装

### 前提条件

- Python 3.7+
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

基本用法：

```bash
python process_pdf.py --output output_directory --output-md result.md
```

### 参数说明

- `-o, --output`: 输出目录路径
- `-s, --start_page`: 起始页码（从0开始）
- `-e, --end_page`: 结束页码
- `-d, --dpi`: 图像分辨率，默认300
- `--threshold_lr`: 左右栏阈值，默认0.9
- `--threshold_cross`: 跨栏阈值，默认0.3
- `--no-filter`: 不过滤区域
- `--upload`: 启用图片上传
- `--output-md`: Markdown输出文件路径，默认output.md

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
├── .env                   # 环境变量配置
└── README.md              # 项目文档
```

## 示例

将PDF转换为Markdown并上传图像：

```bash
python process_pdf.py -o output_dir --upload --output-md result.md
```

## 注意事项

- 确保API密钥设置正确以使用VLM功能
- 对于大型PDF，建议增加内存分配
- 处理速度取决于PDF复杂度和页数

## 贡献

欢迎提交问题和拉取请求以改进此项目。
