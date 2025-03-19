# x-pdf2md

![alt text](assets/images/d99084735737c77dc3d3304cb78a411f.png)
一个将PDF文档转换为Markdown的高级工具包，支持自动提取文本、识别公式、表格和图像。

## 功能特点

- PDF文档页面转换为图像
- 基于深度学习的版面分析
- 数学公式识别并转换为LaTeX格式
- 表格提取并转换为HTML格式
- 图像自动通过多模态模型描述并上传到自定义的服务端
- 多栏文本智能识别与重排版

## 安装

### 1. 安装特殊依赖

本项目依赖于PaddlePaddle和PaddleX进行深度学习模型推理，这些依赖需要单独安装：

#### CPU版本

```bash
# 首先安装PaddlePaddle CPU版本
pip install paddlepaddle==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# 然后安装PaddleX
pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0rc0-py3-none-any.whl
```

#### GPU版本（CUDA 11.8）

```bash
# 安装PaddlePaddle GPU版本
pip install paddlepaddle-gpu==3.0.0rc0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# 然后安装PaddleX
pip install https://paddle-model-ecology.bj.bcebos.com/paddlex/whl/paddlex-3.0.0rc0-py3-none-any.whl
```

### 安装开发依赖

```bash
# 安装开发依赖
pip install -r requirements.txt

```

#### 其他CUDA版本

如果需要支持其他CUDA版本，请参考[PaddlePaddle官方安装指南](https://www.paddlepaddle.org.cn/install/quick)选择合适的安装命令。

## 使用方法

### 作为Python包导入

#### 快速转换方法

```python
import os
from pathlib import Path

from x_pdf2md.convert import convert_pdf_to_markdown


def test_convert_pdf():
    """
    处理x_pdf2md/tests/test.pdf文件，并输出结果到output目录
    """
    # 获取当前模块所在目录
    current_module_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建项目根目录路径
    project_root = os.path.dirname(current_module_dir)
    
    # 构建PDF文件路径（使用tests目录下的测试文件）
    pdf_path = os.path.join(project_root, "x_pdf2md", "tests", "test_x_pdf2md.pdf")
    
    # 构建输出目录路径
    output_dir = os.path.join(os.getcwd(), "output")
    
    # 确保PDF文件存在
    if not os.path.exists(pdf_path):
        print(f"错误：找不到测试PDF文件: {pdf_path}")
        print(f"请确保在 x_pdf2md/tests 目录中存在 test.pdf 文件")
        return False
    
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"开始处理PDF文件: {pdf_path}")
    
    try:
        # 调用转换函数
        output_path = convert_pdf_to_markdown(
            pdf_path=pdf_path,
            output_dir=output_dir,
            start_page=0,
            end_page=None,  # 处理所有页面
            dpi=300,
            upload_images=False,  # 默认不上传图片
            output_md_path=os.path.join(output_dir, "test_result.md")
        )
        
        print(f"PDF转换成功！输出文件路径: {output_path}")
        return True
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    # 当直接运行此文件时执行转换
    test_convert_pdf()
```

#### 图片上传服务

启动本地图片上传服务器：

```bash
# 进入项目目录
cd x_pdf2md/remote_image

# 启动服务
python image_serve.py
```

服务启动后，访问 <http://localhost:8100> 可以使用Web界面上传和管理图片。

## 开源协议

本项目使用 [BSD 开源协议](./LICENSE)。
