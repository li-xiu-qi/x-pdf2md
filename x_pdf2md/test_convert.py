"""
测试文件，用于直接处理x_pdf2md/tests目录下的test.pdf文件
使用方法：
python -m x_pdf2md.test_convert
"""

import os
from pathlib import Path
from .main import convert_pdf_to_markdown


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
    print("\n如果仍然无法正常运行，请尝试以下方法：")
    print("1. 确保已经安装所有依赖:")
    print("   pip install -e .")
    print("2. 确保x_pdf2md/tests目录下有test.pdf文件")
    print("3. 检查Python环境和PaddlePaddle安装状态")
