#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# author：筱可
# 2023-11-08
"""
使用说明：
    该模块用于可视化文档布局分析结果，展示检测到的文本框和其他元素。
    
主要功能：
    1. 在图像上绘制标注框
    2. 为不同类型的元素显示不同颜色的标注
    3. 可选择性地显示元素的顺序编号和标签类型
    4. 将可视化结果保存为图片文件

参数说明：
    LayoutVisualizer类：
        - font_path(str): 字体文件路径
        - font_size(int): 字体大小
        
    draw_boxes方法：
        - image(np.ndarray): 原始图像数据
        - boxes(List[Dict]): 包含坐标和标签信息的检测框列表
        - show_order(bool): 是否显示排序顺序
        - show_label(bool): 是否显示标签类型
        返回值：绘制了检测框的图像(np.ndarray)
        
    save_visualization方法：
        - image_path(str): 原始图像路径
        - boxes(List[Dict]): 检测框列表
        - output_path(str): 输出图像路径
        - show_order(bool): 是否显示排序顺序
        - show_label(bool): 是否显示标签类型
        返回值：无
        
注意事项：
    - 依赖OpenCV(cv2)、NumPy、PIL库
    - 需要引入layout_config模块中的LayoutConfig配置类
    - 检测框数据结构为字典列表，每个字典必须包含'coordinate'和'label'键
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List
from layout_config import LayoutConfig


class LayoutVisualizer:
    """
    布局可视化工具类，用于在图像上绘制和标注检测到的布局元素
    """
    
    def __init__(self, font_path: str = None, font_size: int = 24):
        """
        初始化布局可视化器
        
        Args:
            font_path (str, optional): 字体文件路径，默认使用PIL默认字体
            font_size (int, optional): 字体大小，默认24
        """
        # 初始化字体对象
        self.font: ImageFont.ImageFont = ImageFont.load_default()
        if font_path:
            try:
                self.font = ImageFont.truetype(font_path, font_size)
            except Exception as e:
                print(f"无法加载指定字体，使用默认字体: {e}")
        
        # 使用配置文件中的颜色设置
        self.colors: Dict[str, tuple] = LayoutConfig.COLORS
        self.default_color: tuple = LayoutConfig.DEFAULT_COLOR
        
    def draw_boxes(self, image: np.ndarray, boxes: List[Dict], 
                  show_order: bool = True, show_label: bool = True) -> np.ndarray:
        """
        在图像上绘制排序后的检测框
        
        Args:
            image (np.ndarray): 原始图像(BGR格式)
            boxes (List[Dict]): 检测框列表，每个元素必须包含'coordinate'和'label'
            show_order (bool, optional): 是否显示排序顺序，默认为True
            show_label (bool, optional): 是否显示标签类型，默认为True
            
        Returns:
            np.ndarray: 绘制了检测框的图像(BGR格式)
        """
        # 转换为PIL图像
        image_rgb: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image: Image.Image = Image.fromarray(image_rgb)
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(pil_image)
        
        # 绘制每个元素
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box['coordinate'])
            label: str = box['label']
            score: float = box.get('score', 0)
            color: tuple = self.colors.get(label, self.default_color)
            
            # 绘制矩形框
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # 准备标注文本
            text_elements: List[str] = []
            if show_order:
                text_elements.append(f"#{i+1}")
            if show_label:
                text_elements.append(f"{label}")
                if score > 0:
                    text_elements.append(f"{score:.2f}")
            text: str = " ".join(text_elements)
            
            if text:
                # 获取文本尺寸
                text_bbox: tuple = draw.textbbox((0, 0), text, font=self.font)
                text_width: int = text_bbox[2] - text_bbox[0]
                text_height: int = text_bbox[3] - text_bbox[1]
                
                # 绘制文本背景
                draw.rectangle(
                    [x1, y1 - text_height - 8, x1 + text_width + 8, y1],  # 增加内边距
                    fill=color
                )
                
                # 绘制文本
                draw.text(
                    (x1 + 4, y1 - text_height - 4),  # 调整文本位置
                    text,
                    fill=(255, 255, 255),
                    font=self.font
                )
        
        # 转换回OpenCV格式
        result: np.ndarray = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return result

    def save_visualization(self, image_path: str, boxes: List[Dict], 
                         output_path: str,
                         show_order: bool = True,
                         show_label: bool = True) -> None:
        """
        保存布局可视化结果到文件
        
        Args:
            image_path (str): 原始图像文件路径
            boxes (List[Dict]): 检测框列表
            output_path (str): 输出图像文件路径 
            show_order (bool, optional): 是否显示排序顺序，默认为True
            show_label (bool, optional): 是否显示标签类型，默认为True
            
        Returns:
            None
            
        Raises:
            ValueError: 当无法读取输入图像时抛出
        """
        # 读取原始图像
        image: np.ndarray = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 绘制检测框
        result: np.ndarray = self.draw_boxes(image, boxes, show_order, show_label)
        
        # 保存结果
        cv2.imwrite(output_path, result)
        print(f"可视化结果已保存至: {output_path}")
