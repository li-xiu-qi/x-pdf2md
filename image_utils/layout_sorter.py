#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.threshold_left_right = threshold_left_right
        self.threshold_cross = threshold_cross
    
    def sort_layout(self, layout_result: Union[str, dict], page_width: float) -> List[Dict]:
        """
        对版面检测结果进行排序
        
        Args:
            layout_result: JSON文件路径或者包含检测结果的字典
            page_width: 页面宽度,必须提供
            
        Returns:
            排序后的元素列表
        """
        # 加载检测结果
        if isinstance(layout_result, str):
            with open(layout_result, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            result = layout_result
            
        # 获取元素列表
        elements = result.get('boxes', [])
        return self._sort_elements(elements, page_width)
    
    def _sort_elements(self, elements: List[Dict], page_width: float) -> List[Dict]:
        """
        对元素按照左右栏进行排序
        
        Args:
            elements: 元素列表
            page_width: 页面宽度,必须提供
            
        Returns:
            排序后的元素列表
        """
        # 筛选有效元素
        valid_elements = [
            elem for elem in elements 
            if "coordinate" in elem and len(elem["coordinate"]) == 4
        ]
        
        if not valid_elements:
            return []
            
        page_center_x = page_width / 2
        left_column = []
        right_column = []
        
        # 分配元素到左右栏
        for elem in valid_elements:
            x1, _, x2, _ = elem["coordinate"]
            elem_width = x2 - x1
            
            # 计算左右覆盖比例
            left_part = max(0, min(x2, page_center_x) - x1)
            right_part = max(0, x2 - max(x1, page_center_x))
            
            left_ratio = left_part / elem_width if elem_width > 0 else 0
            right_ratio = right_part / elem_width if elem_width > 0 else 0
            
            # 根据覆盖比例分配
            if left_ratio >= self.threshold_left_right:
                left_column.append(elem)
            elif right_ratio >= self.threshold_left_right:
                right_column.append(elem)
            elif left_ratio > self.threshold_cross and right_ratio > self.threshold_cross:
                left_column.append(elem)
            else:
                elem_center_x = (x1 + x2) / 2
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
    sorter = LayoutSorter()
    
