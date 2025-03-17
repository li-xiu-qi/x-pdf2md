import os
from pathlib import Path
from format_res import format_pdf_regions
from pdf_utils.pdf2image import pdf_to_images
from image_utils.process_page import process_page_layout
from image_utils.layout_config import LayoutConfig
from image_utils.region_image import RegionImage
from remote_image import default_uploader
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





if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PDF文档处理工具")
    parser.add_argument("-p", "--pdf", required=True, help="输入PDF文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出目录路径")
    parser.add_argument(
        "-s", "--start_page", type=int, default=0, help="起始页码（从0开始）"
    )
    parser.add_argument("-e", "--end_page", type=int, default=None, help="结束页码")
    parser.add_argument("-d", "--dpi", type=int, default=300, help="图像分辨率")
    parser.add_argument("--threshold_lr", type=float, default=0.9, help="左右栏阈值")
    parser.add_argument("--threshold_cross", type=float, default=0.3, help="跨栏阈值")
    parser.add_argument(
        "--no-filter", action="store_false", dest="filter_regions", help="不过滤区域"
    )
    parser.add_argument("--upload", action="store_true", help="启用图片上传")
    parser.add_argument("--output-md", type=str, default="output.md", help="Markdown输出文件路径")
    args = parser.parse_args()

    # 初始化图片上传器（如果需要）
    image_uploader = None
    if args.upload:
        image_uploader = default_uploader

    pdf = args.pdf
    output_dir = args.output
    start_page = args.start_page
    end_page = args.end_page
    dpi = args.dpi
    threshold_lr = args.threshold_lr
    threshold_cross = args.threshold_cross
    filter_regions = args.filter_regions

    # 处理PDF
    regions = process_pdf_document(
        pdf_path=pdf,
        output_dir=output_dir,
        start_page=start_page,
        end_page=end_page,
        dpi=dpi,
        threshold_left_right=threshold_lr,
        threshold_cross=threshold_cross,
    )

    # 格式化结果
    formatted_pages = format_pdf_regions(regions, image_uploader)


    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(formatted_pages))
    print(f"Markdown文件已保存到: {args.output_md}")

    total_pages = len(regions)
    total_regions = sum(len(page_regions) for page_regions in regions)
    print(f"处理完成！共处理 {total_pages} 页，生成 {total_regions} 个区域图片")
