#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：筱可
# 2023-06-30
"""
使用说明：

该模块用于处理PDF版面检测结果中的元素排序，按照左右栏布局对元素进行分类和重排序。

主要功能：
1. 解析版面检测的JSON结果
2. 根据坐标信息将元素分配到左右栏
3. 按照垂直位置对每个栏内的元素进行排序
4. 将排序后的左右栏元素合并输出

参数说明：
- LayoutSorter类:
  - threshold_left_right: 元素归属左/右栏的阈值
  - threshold_cross: 判定元素跨栏的阈值
  - sort_layout(): 接收版面检测结果和页面宽度，返回排序后的元素列表

注意事项：
- 需要正确提供页面宽度以便计算左右栏分界
- 输入的版面检测结果必须包含元素坐标信息
"""

import json
from typing import List, Dict, Optional, Union

class LayoutSorter:
    """版面布局元素排序处理器"""
    
    def __init__(self, 
                 threshold_left_right: float = 0.9,
                 threshold_cross: float = 0.3):
        """
        初始化排序器
        
        Args:
            threshold_left_right: 判定元素属于左/右栏的阈值(0-1)，默认0.9
            threshold_cross: 判定元素跨栏的阈值(0-1)，默认0.3
        """
        self.threshold_left_right: float = threshold_left_right
        self.threshold_cross: float = threshold_cross
    
    def sort_layout(self, layout_result: Union[str, dict], page_width: float) -> List[Dict]:
        """
        对版面检测结果进行排序
        
        Args:
            layout_result: JSON文件路径或者包含检测结果的字典
            page_width: 页面宽度,必须提供
            
        Returns:
            List[Dict]: 排序后的元素列表
        """
        # 加载检测结果
        result: dict = {}
        if isinstance(layout_result, str):
            with open(layout_result, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            result = layout_result
            
        # 获取元素列表
        elements: List[Dict] = result.get('boxes', [])
        return self._sort_elements(elements, page_width)
    
    def _sort_elements(self, elements: List[Dict], page_width: float) -> List[Dict]:
        """
        对元素按照左右栏进行排序
        
        Args:
            elements: 元素列表
            page_width: 页面宽度,必须提供
            
        Returns:
            List[Dict]: 排序后的元素列表
        """
        # 筛选有效元素
        valid_elements: List[Dict] = [
            elem for elem in elements 
            if "coordinate" in elem and len(elem["coordinate"]) == 4
        ]
        
        if not valid_elements:
            return []
            
        page_center_x: float = page_width / 2
        left_column: List[Dict] = []
        right_column: List[Dict] = []
        
        # 分配元素到左右栏
        for elem in valid_elements:
            x1: float = elem["coordinate"][0]
            y1: float = elem["coordinate"][1]
            x2: float = elem["coordinate"][2]
            y2: float = elem["coordinate"][3]
            elem_width: float = x2 - x1
            
            # 计算左右覆盖比例
            left_part: float = max(0, min(x2, page_center_x) - x1)
            right_part: float = max(0, x2 - max(x1, page_center_x))
            
            left_ratio: float = left_part / elem_width if elem_width > 0 else 0
            right_ratio: float = right_part / elem_width if elem_width > 0 else 0
            
            # 根据覆盖比例分配
            if left_ratio >= self.threshold_left_right:
                left_column.append(elem)
            elif right_ratio >= self.threshold_left_right:
                right_column.append(elem)
            elif left_ratio > self.threshold_cross and right_ratio > self.threshold_cross:
                left_column.append(elem)
            else:
                elem_center_x: float = (x1 + x2) / 2
                if elem_center_x <= page_center_x:
                    left_column.append(elem)
                else:
                    right_column.append(elem)
                    
        # 按垂直位置排序
        left_column.sort(key=lambda e: e["coordinate"][1])
        right_column.sort(key=lambda e: e["coordinate"][1])
        
        return left_column + right_column
    

if __name__ == "__main__":
    # 使用示例
    sorter: LayoutSorter = LayoutSorter()

