#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
区域图像类 - 表示文档中的一个区域及其属性
"""

import os
import cv2
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class RegionImage:
    """表示文档中的一个区域及其属性"""
    
    # 区域位置和尺寸
    x: int                             # 左上角x坐标
    y: int                             # 左上角y坐标
    width: int                         # 宽度
    height: int                        # 高度
    page_number: int                   # 页码
    region_index: int                  # 区域索引
    
    # 区域属性
    label: str = "text"                # 区域标签类型
    content: str = ""                  # 区域内容
    image_path: Optional[str] = None   # 区域图像保存路径
    confidence: float = 1.0            # 置信度
    
    # 其他属性
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """获取边界框 (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    @property
    def area(self) -> int:
        """计算区域面积"""
        return self.width * self.height
    
    def save_image(self, image: np.ndarray, output_dir: str) -> str:
        """
        保存区域图像
        
        Args:
            image: 完整页面图像
            output_dir: 输出目录
            
        Returns:
            str: 保存的图像路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 裁剪区域
        region_img = image[self.y:self.y+self.height, self.x:self.x+self.width]
        
        # 生成保存路径
        filename = f"page_{self.page_number}_region_{self.region_index}_{self.label}.png"
        save_path = os.path.join(output_dir, filename)
        
        # 保存图像
        cv2.imwrite(save_path, region_img)
        
        # 更新图像路径
        self.image_path = save_path
        
        return save_path
