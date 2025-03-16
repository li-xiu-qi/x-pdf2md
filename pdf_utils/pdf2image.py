import fitz
import os
from PIL import Image
import io
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
    # 基于DPI计算缩放因子（PDF的基础分辨率为72 DPI）
    zoom = dpi / 72
    
    try:
        # 打开PDF文件
        pdf_document = fitz.open(pdf_path)
        
        # 检查页码是否有效
        if page_number < 0 or page_number >= len(pdf_document):
            raise ValueError(f"页码 {page_number} 超出范围。PDF共有 {len(pdf_document)} 页。")
        
        # 获取请求的页面
        page = pdf_document.load_page(page_number)
        
        # 创建用于高分辨率渲染的矩阵
        mat = fitz.Matrix(zoom, zoom)
        
        # 将页面渲染为像素图（图像）
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # 转换为PIL图像
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # 保存图像
        img.save(output_path)
        
        # 关闭PDF
        pdf_document.close()
        
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
        # 打开PDF文件获取页数
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        pdf_document.close()
        
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

if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="PDF转图像工具")
    parser.add_argument("-p", "--pdf", required=True, help="输入PDF文件路径")
    parser.add_argument("-o", "--output", required=True, help="输出图像目录")
    parser.add_argument("-s", "--start_page", type=int, default=0, help="起始页码（从0开始索引）")
    parser.add_argument("-e", "--end_page", type=int, default=None, help="结束页码（包含）")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="图像分辨率")
    
    args = parser.parse_args()
    
    pdf = args.pdf
    output = args.output
    start_page = args.start_page
    end_page = args.end_page
    dpi = args.dpi
    
    # 批量处理页面
    image_paths = pdf_to_images(
        pdf_path=pdf,
        output_dir=output,
        start_page=start_page,
        end_page=end_page,
        dpi=dpi
    )
    print(f"成功转换 {len(image_paths)} 页PDF到图像")