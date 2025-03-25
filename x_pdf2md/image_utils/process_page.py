from typing import List, Dict
import os
import json

from x_pdf2md.image_utils.crop_text_areas import PolyCropper, TextAreaCropper
from x_pdf2md.image_utils.detect_and_sort import detect_and_sort_layout
from x_pdf2md.image_utils.region_image import RegionImage


def process_page_layout(
        image_path: str,
        output_dir: str,
        page_number: int = 1,
        layout_json_path: str = None,
        threshold_left_right: float = 0.9,
        threshold_cross: float = 0.3
) -> List[RegionImage]:
    """
    处理页面布局：检测并排序版面，然后按顺序裁剪保存各区域

    Args:
        image_path: 输入图片路径
        output_dir: 输出目录路径
        layout_json_path: 布局检测结果保存路径（可选）
        threshold_left_right: 判定左右栏的阈值
        threshold_cross: 判定跨栏的阈值

    Returns:
        List[RegionImage]: 包含区域信息的RegionImage对象列表
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 如果未指定layout_json_path，在output_dir中创建临时文件
    if layout_json_path is None:
        layout_json_path = os.path.join(output_dir, "temp_layout.json")

    # 检测并排序版面
    sorted_elements = detect_and_sort_layout(
        image_path,
        layout_json_path,
        threshold_left_right,
        threshold_cross
    )

    # 将排序后的元素写入JSON文件
    with open(layout_json_path, 'w', encoding='utf-8') as f:
        json.dump({"boxes": sorted_elements}, f, ensure_ascii=False, indent=2)

    # 创建裁剪处理器
    cropper = TextAreaCropper(PolyCropper())

    # 裁剪并保存区域
    region_images = []
    cropper.crop_text_areas(
        image_path,
        layout_json_path,
        output_dir,
        output_format='png'
    )

    # 获取裁剪后的图片信息（按排序顺序）
    for i, element in enumerate(sorted_elements):
        label = element.get('label', 'unknown')
        score = element.get('score', 0)
        box = element.get('box', [])
        filename = f"{i}_{label}_{score:.4f}.png"
        cropped_path = os.path.join(output_dir, filename)
        contains = element.get('contains', [])
        if os.path.exists(cropped_path):
            region = RegionImage(
                image_path=cropped_path,
                label=label,
                score=score,
                page_number=page_number,
                region_index=i,
                original_box=box,
                contains=contains
            )
            region_images.append(region)

    return region_images


if __name__ == "__main__":
    # 使用示例
    image_path = "car.png"
    output_dir = "./processed_output"

    cropped_images = process_page_layout(image_path, output_dir)
    print(f"处理完成，共生成 {len(cropped_images)} 个区域图片")
    for i, path in enumerate(cropped_images, 1):
        print(f"区域 {i}: {path}")
