import os
import sys
import pdfplumber
from PyPDF2 import PdfReader
from PIL import Image
from pathlib import Path
from tqdm import tqdm

def pdf_page_to_image(pdf_path, page_number, output_path, dpi=300):
    """
    将PDF中的指定页面提取为高分辨率图片。
    
    参数:
        pdf_path (str): PDF文件路径
        page_number (int): 要提取的页码（从0开始索引）
        output_path (str): 输出图片的保存路径
        dpi (int): 分辨率（每英寸点数），数值越高质量越好
    
    返回:
        str: 已保存图片的路径
    """
    try:
        # 检查页码是否有效
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            if page_number < 0 or page_number >= len(pdf.pages):
                raise ValueError(f"页码 {page_number} 超出范围。PDF共有 {len(pdf.pages)} 页。")
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 使用pdfplumber打开PDF并提取特定页面
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_number]
            
            # 将页面渲染为图像
            img = page.to_image(resolution=dpi)
            pil_img = img.original
            
            # 保存图像
            pil_img.save(output_path)
        
        return output_path
    
    except Exception as e:
        print(f"提取PDF页面时出错: {e}")
        return None

def pdf_to_images(pdf_path, output_dir, start_page=0, end_page=None, dpi=300):
    """
    将PDF文件转换为一系列图像
    
    参数:
        pdf_path (str): PDF文件路径
        output_dir (str): 输出图像的目录
        start_page (int): 起始页码（从0开始索引）
        end_page (int): 结束页码（包含），如果为None则处理所有页面
        dpi (int): 分辨率
    
    返回:
        list: 已生成图像的路径列表
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    pdf_name = Path(pdf_path).stem
    
    try:
        # 获取PDF总页数
        with open(pdf_path, 'rb') as f:
            pdf = PdfReader(f)
            total_pages = len(pdf.pages)
        
        # 如果未指定结束页码，则处理所有页面
        if end_page is None:
            end_page = total_pages - 1
        
        # 验证页码范围
        if start_page < 0 or start_page >= total_pages:
            raise ValueError(f"起始页码 {start_page} 无效。PDF共有 {total_pages} 页。")
        
        if end_page < start_page or end_page >= total_pages:
            raise ValueError(f"结束页码 {end_page} 无效。PDF共有 {total_pages} 页。")
        
        # 存储图像路径
        image_paths = []
        
        # 处理每个页面
        page_range = range(start_page, end_page + 1)
        for page_num in tqdm(page_range, desc="转换PDF页面为图像"):
            # 设置输出图像路径
            output_image = os.path.join(output_dir, f"{pdf_name}_page_{page_num+1}.png")
            
            # 转换页面为图像
            result = pdf_page_to_image(pdf_path, page_num, output_image, dpi)
            
            if result:
                image_paths.append(result)
        
        return image_paths
        
    except Exception as e:
        print(f"处理PDF时出错: {e}")
        return []

# 直接调用示例（可以直接在其他代码中导入并使用这些函数）
def convert_example():
    """示例函数：直接调用pdf_to_images进行转换"""
    pdf_path = "example.pdf"  # 替换为实际的PDF路径
    output_dir = "./outputs"  # 替换为实际的输出目录
    
    # 转换PDF到图像
    image_paths = pdf_to_images(
        pdf_path=pdf_path,
        output_dir=output_dir,
        dpi=300
    )
    
    print(f"成功转换 {len(image_paths)} 页PDF到图像")
    return image_paths

# 如果需要命令行使用，保留此部分；否则可以删除
if __name__ == "__main__":
    import argparse
    
    # 简化的命令行界面
    parser = argparse.ArgumentParser(description="PDF转图像工具")
    parser.add_argument("-p", "--pdf", required=True, help="输入PDF文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出图像目录")
    parser.add_argument("-s", "--start_page", type=int, default=0, help="起始页码（从0开始索引）")
    parser.add_argument("-e", "--end_page", type=int, default=None, help="结束页码（包含）")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="图像分辨率")
    
    try:
        args = parser.parse_args()
        
        # 批量处理页面
        image_paths = pdf_to_images(
            pdf_path=args.pdf,
            output_dir=args.output,
            start_page=args.start_page,
            end_page=args.end_page,
            dpi=args.dpi
        )
        print(f"成功转换 {len(image_paths)} 页PDF到图像")
    
    except Exception as e:
        print(f"发生错误: {e}")
        print("\n正确用法示例:")
        print("  python test.py -p test.pdf -o ./outputs")
        sys.exit(1)