#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# author：筱可
# 2023-06-15
"""
使用说明：
本模块用于检测图像版面并对检测结果进行排序。可以直接调用detect_and_sort_layout函数处理图像文件。

主要功能：
1. 读取图像并获取图像尺寸
2. 调用layout_detect模块进行版面检测
3. 使用LayoutSorter对检测结果进行排序
4. 返回排序后的版面元素列表

参数说明：
- detect_and_sort_layout函数:
  image_path: str - 输入图片路径
  output_path: str - 布局检测结果保存路径
  threshold_left_right: float - 判定元素属于左/右栏的阈值
  threshold_cross: float - 判定元素跨栏的阈值
  返回值: List[Dict] - 排序后的版面元素列表

注意事项：
- 依赖cv2库进行图像处理
- 依赖自定义模块layout_detect和layout_sorter
- 在主函数中使用时需要确保正确设置输入和输出路径
"""

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
    image: cv2.Mat = cv2.imread(image_path)
    page_width: int = image.shape[1]
    
    # 检测版面
    layout_result: List[Dict] = detect_layout(image_path, output_path)
    
    # 创建排序器并排序
    sorter: LayoutSorter = LayoutSorter(threshold_left_right, threshold_cross)
    sorted_elements: List[Dict] = sorter.sort_layout(layout_result, page_width)
    
    return sorted_elements

if __name__ == "__main__":
    # 使用示例
    image_path: str = "formula_inline.png"
    sorted_result: List[Dict] = detect_and_sort_layout(image_path)
    print(f"检测到 {len(sorted_result)} 个已排序的版面元素")
    
    # 添加可视化
    from layout_visualizer import LayoutVisualizer
    visualizer: LayoutVisualizer = LayoutVisualizer()
    visualizer.save_visualization(
        image_path=image_path,
        boxes=sorted_result,
        output_path="output/visualization_output.png"
    )
