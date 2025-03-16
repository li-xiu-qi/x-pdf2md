#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Dict, List, Union
import os
import json
from PIL import Image
import numpy as np

from ocr_utils.text_detection import text_detection
from ocr_utils.text_recogniize import recognize_text


class OCRProcessor:
    def __init__(self, det_model="PP-OCRv4_mobile_det", rec_model="PP-OCRv4_mobile_rec"):
        self.det_model = det_model
        self.rec_model = rec_model
        
    def crop_image(self, image_path: str, box_coordinates: List) -> Image.Image:
        """根据坐标裁剪图像区域"""
        image = Image.open(image_path)
        # 将坐标转换为矩形边界框
        x_coordinates = [int(point[0]) for point in box_coordinates]
        y_coordinates = [int(point[1]) for point in box_coordinates]
        left, top = min(x_coordinates), min(y_coordinates)
        right, bottom = max(x_coordinates), max(y_coordinates)
        # 裁剪图像
        cropped = image.crop((left, top, right, bottom))
        return cropped

    def process_image(self, image_path: str, save_crops: bool = True, output_dir: str = "./output/crops") -> List[Dict]:
        """
        处理图像的完整OCR流程
        Args:
            image_path: 输入图像路径
            save_crops: 是否保存裁剪后的图像
            output_dir: 裁剪图像的保存目录
        Returns:
            包含文本位置和识别结果的列表
        """
        # 创建输出目录
        if save_crops:
            os.makedirs(output_dir, exist_ok=True)
        
        # 1. 首先进行文本检测
        det_results = text_detection(image_path)
        
        all_results = []
        # 2. 对每个检测到的区域进行处理
        for idx, (poly, score) in enumerate(zip(det_results['dt_polys'], det_results['dt_scores'])):
            # 裁剪检测到的文本区域
            cropped = self.crop_image(image_path, poly)
            
            # 保存裁剪的图像（如果需要）
            if save_crops:
                crop_filename = f"text_area_{idx}_score_{score:.4f}.png"
                crop_path = os.path.join(output_dir, crop_filename)
                cropped.save(crop_path)
                temp_path = crop_path
            else:
                # 如果不保存，使用临时目录
                temp_dir = "./output/temp"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, f"temp_{idx}.png")
                cropped.save(temp_path)
            
            # 3. 对裁剪区域进行文本识别
            rec_result = recognize_text(temp_path)
            
            # 4. 整合结果
            result = {
                'position': poly,
                'detection_score': score,
                'text': rec_result['rec_text'],
                'recognition_score': rec_result['rec_score']
            }
            if save_crops:
                result['crop_path'] = crop_path
            all_results.append(result)
            
            # 清理临时文件（如果不需要保存）
            if not save_crops:
                os.remove(temp_path)
            
        return all_results

    def extract_text(self, image_path: str, as_list: bool = False, save_crops: bool = False, output_dir: str = "./output/crops") -> Union[str, List[str]]:
        """
        直接从图像中提取文本内容
        Args:
            image_path: 输入图像路径
            as_list: 是否以列表形式返回每个检测区域的文本
            save_crops: 是否保存裁剪后的图像
            output_dir: 裁剪图像的保存目录
        Returns:
            提取的文本内容，可以是字符串或字符串列表
        """
        # 调用OCR处理流程
        results = self.process_image(image_path, save_crops, output_dir)
        
        # 提取所有文本
        texts = [result['text'] for result in results]
        
        # 根据参数决定返回列表还是合并后的字符串
        if as_list:
            return texts
        else:
            return ''.join(texts)
    
    def save_results_to_json(self, results: List[Dict], output_path: str):
        """
        将OCR结果保存到JSON文件
        Args:
            results: OCR处理结果列表
            output_path: JSON文件保存路径
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 将numpy数组转换为列表以便JSON序列化
        serializable_results = []
        for result in results:
            result_copy = result.copy()
            # 检查position是否为numpy数组，如果是则转换为列表
            if hasattr(result_copy['position'], 'tolist'):
                result_copy['position'] = result_copy['position'].tolist()
            # 如果已经是列表则不需要转换
            serializable_results.append(result_copy)
            
        # 保存到JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 测试用例
    image_path = "test_text.png"  # 替换为实际的测试图像路径
    ocr = OCRProcessor()
    results = ocr.process_image(
        image_path,
        save_crops=True,
        output_dir="./output/test_crops"
    )
    
    # 保存结果到JSON文件
    json_output_path = "./output/ocr_results.json"
    ocr.save_results_to_json(results, json_output_path)
    
    # 打印识别结果
    print("\nOCR Results:")
    print("-" * 50)
    for idx, result in enumerate(results):
        print(f"Region {idx + 1}:")
        print(f"Text: {result['text']}")
        print(f"Detection Score: {result['detection_score']:.4f}")
        print(f"Recognition Score: {result['recognition_score']:.4f}")
        if 'crop_path' in result:
            print(f"Crop saved at: {result['crop_path']}")
        print("-" * 50)
    
    # 直接提取文本的示例
    text = ocr.extract_text(image_path)
    print("\nExtracted Text:")
    print("-" * 50)
    print(text)
    
    # 以列表形式获取文本
    text_list = ocr.extract_text(image_path, as_list=True)
    print("\nExtracted Text as List:")
    print("-" * 50)
    for i, t in enumerate(text_list):
        print(f"{i+1}. {t}")
