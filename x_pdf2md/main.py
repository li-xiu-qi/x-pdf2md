#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
命令行入口点 - 处理命令行参数并调用相应功能
"""

import argparse
import os
from typing import Optional, List, Union
from x_pdf2md.process_pdf import process_pdf_document
from x_pdf2md.format_res import format_pdf_regions
from x_pdf2md.remote_image import default_uploader
from x_pdf2md.config import update_config, get_config, DEFAULT_CONFIG


def convert_pdf_to_markdown(
    pdf_path: str,
    output_dir: str = "output",
    start_page: int = 0,
    end_page: Optional[int] = None,
    dpi: int = DEFAULT_CONFIG["DEFAULT_DPI"],  # 使用配置中的默认值
    threshold_left_right: float = DEFAULT_CONFIG["THRESHOLD_LEFT_RIGHT"],  # 使用配置中的默认值
    threshold_cross: float = DEFAULT_CONFIG["THRESHOLD_CROSS"],  # 使用配置中的默认值
    upload_images: bool = False,
    output_md_path: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,  # 从config中获取，不设默认值
) -> Union[str, List[str]]:
    """
    将PDF文档转换为Markdown
    
    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录路径，默认为"output"
        start_page: 起始页码（从0开始），默认为0
        end_page: 结束页码（包含），如果为None则处理所有页面
        dpi: PDF转图像的分辨率，默认为300
        threshold_left_right: 判定左右栏的阈值，默认为0.9
        threshold_cross: 判定跨栏的阈值，默认为0.3
        upload_images: 是否上传图片，默认为False
        output_md_path: Markdown输出文件路径，如果为None则不保存文件
        api_key: API密钥，可选，默认从config获取
        base_url: API基础URL，可选，默认从config获取
        
    Returns:
        如果提供了output_md_path，返回保存的文件路径；否则返回Markdown内容的列表
    """
    # 更新配置
    config_updates = {}
    if api_key:
        config_updates["API_KEY"] = api_key
    if base_url:
        config_updates["BASE_URL"] = base_url
    if dpi and dpi != DEFAULT_CONFIG["DEFAULT_DPI"]:
        config_updates["DEFAULT_DPI"] = dpi
    if threshold_left_right is not None and threshold_left_right != DEFAULT_CONFIG["THRESHOLD_LEFT_RIGHT"]:
        config_updates["THRESHOLD_LEFT_RIGHT"] = threshold_left_right
    if threshold_cross is not None and threshold_cross != DEFAULT_CONFIG["THRESHOLD_CROSS"]:
        config_updates["THRESHOLD_CROSS"] = threshold_cross
    
    if config_updates:
        update_config(config_updates)
    
    # 处理PDF
    regions = process_pdf_document(
        pdf_path=pdf_path,
        output_dir=output_dir,
        start_page=start_page,
        end_page=end_page,
        dpi=dpi,
        threshold_left_right=threshold_left_right,
        threshold_cross=threshold_cross,
    )

    # 初始化图片上传器（如果需要）
    image_uploader = None
    if upload_images:
        image_uploader = default_uploader

    # 格式化结果
    formatted_pages = format_pdf_regions(regions, image_uploader)
    
    # 创建输出目录（如果需要）
    if output_md_path:
        output_dir = os.path.dirname(os.path.abspath(output_md_path))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # 保存为Markdown文件
        with open(output_md_path, "w", encoding="utf-8") as f:
            f.write("\n\n---\n\n".join(formatted_pages))
        
        # 输出处理统计
        total_pages = len(regions)
        total_regions = sum(len(page_regions) for page_regions in regions)
        print(f"处理完成！共处理 {total_pages} 页，生成 {total_regions} 个区域图片")
        print(f"Markdown文件已保存到: {output_md_path}")
        
        return output_md_path
    
    # 如果没有指定输出路径，则直接返回格式化后的内容
    return formatted_pages


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="PDF文档处理工具")
    parser.add_argument("-p", "--pdf", required=True, help="输入PDF文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出目录路径")
    parser.add_argument(
        "-s", "--start_page", type=int, default=0, help="起始页码（从0开始）"
    )
    parser.add_argument("-e", "--end_page", type=int, default=None, help="结束页码")
    parser.add_argument("-d", "--dpi", type=int, default=DEFAULT_CONFIG["DEFAULT_DPI"], 
                        help=f"图像分辨率，默认为{DEFAULT_CONFIG['DEFAULT_DPI']}")
    parser.add_argument("--threshold_lr", type=float, default=DEFAULT_CONFIG["THRESHOLD_LEFT_RIGHT"], 
                        help=f"左右栏阈值，默认为{DEFAULT_CONFIG['THRESHOLD_LEFT_RIGHT']}")
    parser.add_argument("--threshold_cross", type=float, default=DEFAULT_CONFIG["THRESHOLD_CROSS"], 
                        help=f"跨栏阈值，默认为{DEFAULT_CONFIG['THRESHOLD_CROSS']}")
    parser.add_argument(
        "--no-filter", action="store_false", dest="filter_regions", help="不过滤区域"
    )
    parser.add_argument("--upload", action="store_true", help="启用图片上传")
    parser.add_argument("--output-md", type=str, default="output.md", help="Markdown输出文件路径")
    
    # 添加API和模型配置参数
    parser.add_argument("--api-key", type=str, help="API密钥")
    parser.add_argument("--base-url", type=str, default=DEFAULT_CONFIG["BASE_URL"], 
                        help=f"API基础URL，默认为{DEFAULT_CONFIG['BASE_URL']}")
    parser.add_argument("--formula-model", type=str, default=DEFAULT_CONFIG["FORMULA_MODEL"], 
                        help=f"公式识别模型名称，默认为{DEFAULT_CONFIG['FORMULA_MODEL']}")
    parser.add_argument("--ocr-det-model", type=str, default=DEFAULT_CONFIG["OCR_DET_MODEL"], 
                        help=f"OCR检测模型名称，默认为{DEFAULT_CONFIG['OCR_DET_MODEL']}")
    parser.add_argument("--ocr-rec-model", type=str, default=DEFAULT_CONFIG["OCR_REC_MODEL"], 
                        help=f"OCR识别模型名称，默认为{DEFAULT_CONFIG['OCR_REC_MODEL']}")
    parser.add_argument("--layout-model", type=str, default=DEFAULT_CONFIG["LAYOUT_MODEL"], 
                        help=f"版面分析模型名称，默认为{DEFAULT_CONFIG['LAYOUT_MODEL']}")
    
    args = parser.parse_args()

    # 更新模型配置
    config_updates = {}
    if args.formula_model != DEFAULT_CONFIG["FORMULA_MODEL"]:
        config_updates["FORMULA_MODEL"] = args.formula_model
    if args.ocr_det_model != DEFAULT_CONFIG["OCR_DET_MODEL"]:
        config_updates["OCR_DET_MODEL"] = args.ocr_det_model
    if args.ocr_rec_model != DEFAULT_CONFIG["OCR_REC_MODEL"]:
        config_updates["OCR_REC_MODEL"] = args.ocr_rec_model
    if args.layout_model != DEFAULT_CONFIG["LAYOUT_MODEL"]:
        config_updates["LAYOUT_MODEL"] = args.layout_model
    
    if config_updates:
        update_config(config_updates)

    # 调用转换函数
    convert_pdf_to_markdown(
        pdf_path=args.pdf,
        output_dir=args.output,
        start_page=args.start_page,
        end_page=args.end_page,
        dpi=args.dpi,
        threshold_left_right=args.threshold_lr,
        threshold_cross=args.threshold_cross,
        upload_images=args.upload,
        output_md_path=args.output_md,
        api_key=args.api_key,
        base_url=args.base_url
    )


if __name__ == "__main__":
    main()
