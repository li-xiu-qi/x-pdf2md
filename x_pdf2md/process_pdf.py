import os
from pathlib import Path
from x_pdf2md.format_res import format_pdf_regions
from x_pdf2md.pdf_utils.pdf2image import pdf_to_images
from x_pdf2md.image_utils.process_page import process_page_layout
from x_pdf2md.image_utils.layout_config import LayoutConfig
from x_pdf2md.image_utils.region_image import RegionImage
from typing import List, Optional
from tqdm import tqdm


def process_pdf_document(
    pdf_path: str,
    output_dir: str,
    start_page: int = 0,
    end_page: Optional[int] = None,
    dpi: int = 300,
    threshold_left_right: float = 0.9,
    threshold_cross: float = 0.3,
) -> List[List[RegionImage]]: 
    """
    处理PDF文档：将PDF转换为图像，并对每页进行版面分析和区域裁剪

    参数:
        pdf_path: PDF文件路径
        output_dir: 输出目录路径
        start_page: 起始页码（从0开始）
        end_page: 结束页码（包含），如果为None则处理所有页面
        dpi: PDF转图像的分辨率
        threshold_left_right: 判定左右栏的阈值
        threshold_cross: 判定跨栏的阈值

    返回:
        List[List[RegionImage]]: 每页的RegionImage对象列表
    """
    # 创建输出目录
    pdf_name = Path(pdf_path).stem
    output_dir = os.path.abspath(output_dir)
    temp_images_dir = os.path.join(output_dir, f"{pdf_name}_images")
    os.makedirs(temp_images_dir, exist_ok=True)

    # 将PDF转换为图像
    print("正在将PDF转换为图像...")
    image_paths = pdf_to_images(
        pdf_path=pdf_path,
        output_dir=temp_images_dir,
        start_page=start_page,
        end_page=end_page,
        dpi=dpi,
    )

    # 处理每个页面的布局
    print("正在分析和裁剪页面...")
    all_page_regions = []
    for i, image_path in enumerate(tqdm(image_paths, desc="处理页面")):
        page_num = i + 1
        page_dir = os.path.join(output_dir, f"{pdf_name}_page_{page_num}")
        os.makedirs(page_dir, exist_ok=True)

        # 处理页面布局并获取区域信息
        regions = process_page_layout(
            image_path=image_path,
            output_dir=page_dir,
            page_number=page_num,
            threshold_left_right=threshold_left_right,
            threshold_cross=threshold_cross,
        )

        all_page_regions.append(regions)

    return all_page_regions
