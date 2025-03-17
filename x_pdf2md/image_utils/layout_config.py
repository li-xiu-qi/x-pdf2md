#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
布局配置类 - 用于存储和管理版面分析的配置参数
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class LayoutConfig:
    """版面分析配置类"""
    
    # 区域类型标签
    REGION_LABELS = [
        "text",            # 普通文本
        "formula",         # 数学公式
        "table",           # 表格
        "image",           # 图像
        "figure",          # 图表
        "chart",           # 图形图表
        "doc_title",       # 文档标题
        "paragraph_title", # 段落标题
        "abstract",        # 摘要
        "figure_title",    # 图标题
        "table_title",     # 表标题
        "chart_title"      # 图表标题
    ]
    
    # 布局分析参数
    min_region_height: int = 20        # 最小区域高度
    min_region_width: int = 40         # 最小区域宽度
    line_spacing: int = 10             # 行间距
    paragraph_spacing: int = 20        # 段落间距
    column_spacing: int = 50           # 栏间距
    
    # 文本检测参数
    text_detection_threshold: float = 0.7  # 文本检测置信度阈值
    
    def __post_init__(self):
        """初始化后处理"""
        # 创建标签到索引的映射
        self.label_to_index = {label: i for i, label in enumerate(self.REGION_LABELS)}
        self.index_to_label = {i: label for i, label in enumerate(self.REGION_LABELS)}
    
    def get_label_index(self, label: str) -> int:
        """获取标签对应的索引"""
        return self.label_to_index.get(label, -1)
    
    def get_label_by_index(self, index: int) -> str:
        """根据索引获取标签"""
        return self.index_to_label.get(index, "unknown")
