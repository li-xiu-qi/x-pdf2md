import os
import sys
import pdfplumber
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
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 使用pdfplumber打开PDF
        with pdfplumber.open(pdf_path) as pdf:
            # 检查页码是否有效
            if page_number < 0 or page_number >= len(pdf.pages):
                raise ValueError(f"页码 {page_number} 超出范围。PDF共有 {len(pdf.pages)} 页。")
            
            # 获取指定页面
            page = pdf.pages[page_number]
            
            # 将页面转换为图像
            img = page.to_image(resolution=dpi)
            
            # 保存图像
            img.save(output_path, format="PNG")
        
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
        # 使用pdfplumber获取PDF总页数
        with pdfplumber.open(pdf_path) as pdf:
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


# 如果需要命令行使用，保留此部分；否则可以删除
if __name__ == "__main__":
    
    pdf_path = "./test_x_pdf2md.pdf"
    output_dir = "./output"
          # 转换PDF到图像
    image_paths = pdf_to_images(
        pdf_path=pdf_path,
        output_dir=output_dir,
        dpi=300
    )