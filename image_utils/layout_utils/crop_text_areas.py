#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# author：筱可
# 2025-03-10
"""
使用说明：
1. 将图像文件和对应的JSON检测结果文件放在指定目录
2. 设置相应的输入输出路径
3. 运行脚本即可获得裁剪后的文本区域图像

主要功能：
1. 读取原始图像和文本检测结果JSON文件
2. 支持矩形和多边形两种裁剪方式
3. 将检测到的文本区域裁剪并保存

参数说明：
TextAreaCropper类方法：
- crop_text_areas: 处理图像和JSON检测结果，裁剪文本区域
返回值：无

注意事项：
1. 依赖库：opencv-python, numpy
2. JSON文件需包含dt_polys和dt_scores字段
3. 确保具有目录的写入权限
"""

import os
import json
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class TextCropper(ABC):
    """文本区域裁剪抽象基类"""
    
    @abstractmethod
    def crop(self, image: np.ndarray, polygon: np.ndarray) -> np.ndarray:
        """裁剪图像中的文本区域
        
        Args:
            image: 原始图像
            polygon: 文本区域多边形坐标
            
        Returns:
            裁剪后的图像区域
        """
        pass

class PolyCropper(TextCropper):
    """多边形裁剪实现类 - 支持透明背景"""
    
    def crop(self, image: np.ndarray, polygon: np.ndarray) -> np.ndarray:
        # 计算外接矩形
        x, y, w, h = cv2.boundingRect(polygon)
        
        # 调整多边形坐标为相对于裁剪区域的坐标
        shifted_polygon = polygon - np.array([x, y])
        
        # 创建透明背景的图像(BGRA)
        cropped = np.zeros((h, w, 4), dtype=np.uint8)
        
        # 将原始图像复制到透明图像的BGR通道
        if len(image.shape) == 3:  # BGR图像
            cropped[:, :, 0:3] = image[y:y+h, x:x+w]
        else:  # 灰度图像
            for i in range(3):
                cropped[:, :, i] = image[y:y+h, x:x+w]
        
        # 创建alpha通道掩码
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [shifted_polygon], 255)
        
        # 将掩码应用到alpha通道
        cropped[:, :, 3] = mask
        
        return cropped

class TextAreaCropper:
    """文本区域处理器"""
    
    def __init__(self, cropper: TextCropper):
        """初始化文本区域处理器
        
        Args:
            cropper: 裁剪策略实现
        """
        self.cropper = cropper
    
    def crop_text_areas(self, image_path: str, json_path: str, output_dir: str, output_format: str = 'png', bg_color: tuple = (255, 255, 255)) -> None:
        """裁剪图像中检测到的文本区域

        Args:
            image_path: 原始图像路径
            json_path: 检测结果JSON文件路径
            output_dir: 裁剪结果保存目录
            output_format: 输出图像格式，支持'png'(带透明度)和'jpg'(无透明度)等，默认为'png'
            bg_color: 当使用不支持透明度的格式时的背景颜色(BGR格式)，默认为白色

        Returns:
            无返回值，结果保存到指定目录
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 读取原始图像
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图像: {image_path}")
            return
        
        # 读取JSON文件中的检测结果
        with open(json_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # 获取检测框列表
        boxes = result.get('boxes', [])
        
        # 处理每个检测到的区域
        for i, box in enumerate(boxes):
            # 获取坐标和其他信息
            coords = box.get('coordinate', [])
            if not coords:
                continue
            
            # 将坐标转换为多边形格式
            x1, y1, x2, y2 = map(float, coords)
            poly = np.array([[x1, y1], [x2, y1], [x2, y2], [x1, y2]], np.int32)
            
            # 使用选择的裁剪策略裁剪图像
            cropped = self.cropper.crop(image, poly)
            
            # 获取区域类型和置信度
            label = box.get('label', 'unknown')
            score = box.get('score', 0)
            
            # 生成输出文件名 - 添加序号
            output_filename = f"{i}_{label}_{score:.4f}.{output_format.lower()}"
            output_path = os.path.join(output_dir, output_filename)
            
            # 根据输出格式处理图像
            if output_format.lower() != 'png' and len(cropped.shape) == 3 and cropped.shape[2] == 4:
                # 如果不是PNG格式，而且图像有Alpha通道，需要处理透明度
                # 创建纯色背景
                background = np.ones((cropped.shape[0], cropped.shape[1], 3), dtype=np.uint8)
                background[:] = bg_color
                
                # 提取Alpha通道作为掩码
                alpha = cropped[:, :, 3] / 255.0
                alpha = alpha[:, :, np.newaxis]
                
                # 将前景与背景混合
                foreground = cropped[:, :, :3]
                merged = cv2.convertScaleAbs(foreground * alpha + background * (1 - alpha))
                
                cv2.imwrite(output_path, merged)
            else:
                cv2.imwrite(output_path, cropped)
            
            print(f"已保存{label}区域 {i+1}: {output_path}")

if __name__ == "__main__":
    # 设置输入输出路径
    image_path = "page_layout.png"
    json_path = "./4_output/res.json"
    output_dir = "./test_cropped_output"
    
    # 创建文本区域处理器并执行裁剪
    processor = TextAreaCropper(PolyCropper())
    
    # 使用默认PNG格式（带透明背景）
    processor.crop_text_areas(image_path, json_path, output_dir, output_format='png')
