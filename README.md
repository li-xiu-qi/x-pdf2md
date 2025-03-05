# X-PDF2MD: PDF转Markdown工具

[![语言](https://img.shields.io/badge/语言-Python-blue)]()
[![版本](https://img.shields.io/badge/版本-0.0.0-brightgreen)]()
[![作者](https://img.shields.io/badge/作者-筱可-orange)]()

## 📚 项目简介

X-PDF2MD是一个强大的文档版面分析与转换工具（基于飞桨平台），可以将PDF文档或文档图片转换为结构化的Markdown文件。该工具结合了版面分析技术，能够准确识别文档中的各种元素（如文本、标题、表格、图像和图表等），并将其转换为格式良好的Markdown内容，保留原始文档的结构和排版。

**微信公众号**: 筱可AI研习社

## ✨ 主要功能

- 🔍 **精准版面分析**: 识别并分类文档中的各种元素
- 📊 **智能元素排序**: 根据文档左右栏布局智能排序元素
- 🖼️ **可视化结果**: 生成包含边界框和标签的可视化结果
- 📝 **Markdown转换**: 将版面分析结果转换为结构化Markdown
- 🔄 **多元素支持**: 处理文本、标题、表格、图像、图表和公式等
- 🖋️ **中文支持**: 完善的中文字体处理和渲染

## 🛠️ 安装指南

### 前提条件

- Python 3.10+
- pip包管理器

### 安装步骤

1. 克隆仓库：

```bash
git clone https://github.com/li-xiu-qi/x-pdf2md.git
cd x-pdf2md
```

2. 安装依赖：
参考：
```

#### 注意事项：
依赖PaddleX库，使用前请确保已正确安装paddlex及其依赖

1.

# cpu

python -m pip install paddlepaddle==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# gpu，该命令仅适用于 CUDA 版本为 11.8 的机器环境
python -m pip install paddlepaddle-gpu==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# gpu，该命令仅适用于 CUDA 版本为 12.3 的机器环境
python -m pip install paddlepaddle-gpu==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cu123/

---

2. 

pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0b2-py3-none-any.whl

#### 参考资料
https://paddlepaddle.github.io/PaddleX/main/installation/installation.html#1

```
<!-- ```bash
pip install -r requirements.txt
``` -->

## 📋 使用方法

### 基本使用

1. 准备输入文件（版面分析的JSON结果和对应的图像文件）
2. 运行处理程序：

```python
from visualize_boxes import DocumentElementProcessor

processor = DocumentElementProcessor(output_dir="output", images_dir="images")
processor.process_document("res.json", "visualization_result.png", "document.md")
```

### 测试程序

运行测试程序以验证功能：

```bash
python test_output.py
```

## 📁 项目结构

```
x-pdf2md/
├── visualize_boxes.py      # 主要处理类，处理版面分析结果
├── element_processors.py   # 不同元素类型的处理器
├── test_output.py          # 测试处理结果和图片引用
├── res.json                # 示例版面分析结果
├── font_info.md            # 中文字体配置说明
└── README.md               # 项目说明文档
```

## ⚙️ 配置选项

### 中文字体配置

程序会自动查找系统中的中文字体。如需自定义字体，请参考 `font_info.md`。

### 输出目录配置

可通过初始化 `DocumentElementProcessor` 时设置 `output_dir` 和 `images_dir` 参数来定制输出位置。

## 🌐 API参考

### DocumentElementProcessor

主要处理类，用于处理版面分析结果并生成输出。

```python
    # 示例使用
    layout_json_path = "res.json"
    visualization_path = "visualization_result.png"
    markdown_filename = "document.md"
    
    processor = DocumentElementProcessor()
    processor.process_document(layout_json_path, visualization_path, markdown_filename)

```

## 🔄 版本历史

- **v0.0.0** - 初始版本，未开发完成

## 👥 贡献指南

欢迎贡献代码、提交问题或建议！请通过以下方式参与：

1. Fork 项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详情请查看 LICENSE 文件

## 🙏 致谢

特别感谢所有开源社区的贡献者以及提供反馈的用户。

## 📬 联系方式

微信公众号：筱可AI研习社

---

<div align="center">
    <sub>Built with ❤️ by 筱可</sub>
</div>
