from typing import Dict, List
import cv2

from image_utils.layout_utils.layout_detect import detect_layout
from image_utils.layout_utils.layout_sorter import LayoutSorter


def detect_and_sort_layout(image_path: str,
                          output_path: str = "./layout_output/layout_detection.json",
                          threshold_left_right: float = 0.9,
                          threshold_cross: float = 0.3) -> List[Dict]:
    """
    检测图片版面并对检测结果进行排序
    
    Args:
        image_path: 输入图片路径
        output_path: 布局检测结果保存路径
        threshold_left_right: 判定元素属于左/右栏的阈值
        threshold_cross: 判定元素跨栏的阈值
        
    Returns:
        排序后的版面元素列表
    """
    # 读取图片获取宽度
    image = cv2.imread(image_path)
    page_width = image.shape[1]
    
    # 检测版面
    layout_result = detect_layout(image_path, output_path)
    
    # 创建排序器并排序
    sorter = LayoutSorter(threshold_left_right, threshold_cross)
    sorted_elements = sorter.sort_layout(layout_result, page_width)
    
    return sorted_elements

if __name__ == "__main__":
    # 使用示例
    image_path = "formula_inline.png"
    sorted_result = detect_and_sort_layout(image_path)
    print(f"检测到 {len(sorted_result)} 个已排序的版面元素")
    
    # 添加可视化
    from layout_visualizer import LayoutVisualizer
    visualizer = LayoutVisualizer()
    visualizer.save_visualization(
        image_path=image_path,
        boxes=sorted_result,
        output_path="output/visualization_output.png"
    )
