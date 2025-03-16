#!/usr/bin/env python  
# -*- coding: utf-8 -*-
# author：筱可
# 2025-03-16

# 导入必要的库
import json
import os
from typing import List
from paddlex import create_model  # PaddleX模型创建工具
import numpy as np
import cv2

def is_same_line(box1, box2, height_threshold=0.5):
    """
    判断两个文本框是否在同一行
    Args:
        box1: 第一个文本框坐标 shape:(4,2)
        box2: 第二个文本框坐标 shape:(4,2)
        height_threshold: 判定阈值，默认为文本框高度的0.5倍
    Returns:
        bool: True表示在同一行，False表示不在同一行
    """
    box1_center = np.mean(box1, axis=0)[1]  # y坐标的中心点
    box2_center = np.mean(box2, axis=0)[1]
    box1_height = abs(max(box1[:,1]) - min(box1[:,1]))
    box2_height = abs(max(box2[:,1]) - min(box2[:,1]))
    avg_height = (box1_height + box2_height) / 2
    
    return abs(box1_center - box2_center) < avg_height * height_threshold

def merge_overlapping_boxes(boxes, scores):
    """
    合并同一行的重叠文本框
    Args:
        boxes: 所有文本框坐标列表 shape:(N,4,2)
        scores: 对应的置信度得分列表 shape:(N,)
    Returns:
        tuple: (合并后的文本框列表, 合并后的置信度列表)
    """
    # 如果只有一个或没有文本框，直接返回
    if len(boxes) <= 1:
        return boxes, scores
    
    # 将输入的文本框列表转换为numpy数组，便于后续处理    
    boxes = np.array(boxes)
    # 初始化合并后的文本框列表
    merged_boxes = []
    # 初始化合并后的得分列表
    merged_scores = []
    # 初始化标记数组，用于记录每个文本框是否已被处理
    used = [False] * len(boxes)
    
    # 遍历所有文本框
    for i in range(len(boxes)):
        # 如果当前文本框已被处理，则跳过
        if used[i]:
            continue
        
        # 获取当前文本框和其得分    
        current_box = boxes[i]
        current_score = scores[i]
        # 初始化待合并文本框的索引列表
        merged_indices = [i]
        
        # 寻找与当前文本框在同一行的其他文本框
        for j in range(i + 1, len(boxes)):
            # 如果目标文本框已被处理，则跳过
            if used[j]:
                continue
            
            # 判断两个文本框是否在同一行    
            if is_same_line(boxes[i], boxes[j]):
                merged_indices.append(j)
        
        # 如果找到了需要合并的文本框
        if len(merged_indices) > 1:
            # 将所有待合并文本框的坐标点重新整理
            merged_points = boxes[merged_indices].reshape(-1, 2)
            # 计算合并后文本框的最小x和y坐标
            x_min, y_min = np.min(merged_points, axis=0)
            # 计算合并后文本框的最大x和y坐标
            x_max, y_max = np.max(merged_points, axis=0)
            # 构建合并后的矩形文本框坐标
            merged_box = np.array([[x_min, y_min], [x_max, y_min],
                                 [x_max, y_max], [x_min, y_max]])
            # 计算合并后文本框的平均置信度得分
            merged_score = np.mean([scores[idx] for idx in merged_indices])
        else:
            # 如果没有需要合并的文本框，保持原状
            merged_box = current_box
            merged_score = current_score
        
        # 标记所有已处理的文本框    
        for idx in merged_indices:
            used[idx] = True
        
        # 将处理结果添加到输出列表    
        merged_boxes.append(merged_box)
        merged_scores.append(merged_score)
    
    # 返回合并后的文本框和对应的置信度得分
    return merged_boxes, merged_scores

def visualize_boxes(image_path, boxes, output_path="./output/merged_result.jpg"):
    """
    将检测到的文本框可视化到图像上
    Args:
        image_path: 原始图像路径
        boxes: 文本框坐标列表
        output_path: 可视化结果保存路径
    """
    image = cv2.imread(image_path)
    for box in boxes:
        box = box.astype(np.int32)
        cv2.polylines(image, [box], True, (0, 255, 0), 2)
    cv2.imwrite(output_path, image)

def text_detection(image_path, output_path="./output/res.json", model="PP-OCRv4_mobile_det", 
                  visualize=False) -> None:
    """
    执行文本检测的主函数
    Args:
        image_path: 输入图像路径
        output_path: 检测结果JSON保存路径
        model: 使用的PaddleOCR模型名称
        visualize: 是否生成可视化结果
    Returns:
        dict: 包含文本检测结果的字典，格式如下：
            {
                'input_path': str,  # 输入图像路径
                'page_index': int,  # 页面索引（如果有）
                'dt_polys': List[List[List[float]]],  # 文本框坐标
                'dt_scores': List[float]  # 置信度得分
            }
    """
    # 创建输出目录
    os.makedirs("./output", exist_ok=True)
    
    # 初始化模型
    model = create_model(model_name=model)

    # 执行预测
    output = model.predict(image_path, batch_size=1)

    # 处理每个检测结果
    for res in output:
        # 将原始结果保存为JSON
        res.save_to_json(output_path)
        
        # 读取JSON结果进行后处理
        with open(output_path, 'r', encoding='utf-8') as f:
            detection_result = json.load(f)
        
        # 提取文本框和置信度
        boxes = np.array(detection_result['dt_polys'])  # 转换为numpy数组便于处理
        scores = np.array(detection_result['dt_scores'])
        
        # 执行文本框合并
        merged_boxes, merged_scores = merge_overlapping_boxes(boxes, scores)
        
        # 更新检测结果，将numpy数组转换回列表
        detection_result['dt_polys'] = [box.tolist() if isinstance(box, np.ndarray) else box 
                                      for box in merged_boxes]
        detection_result['dt_scores'] = [float(score) if isinstance(score, np.ndarray) else score 
                                       for score in merged_scores]
        
        # 保存处理后的结果
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(detection_result, f, indent=4, ensure_ascii=False)
        
        # 生成可视化结果（如果需要）
        if visualize:
            visualize_boxes(image_path, boxes, "./output/original_result.jpg")  # 原始检测框
            visualize_boxes(image_path, merged_boxes, "./output/merged_result.jpg")  # 合并后的检测框
        
    return detection_result

# 主程序入口
if __name__ == "__main__":
    # 对测试图像执行文本检测
    res = text_detection(image_path = "test_fomula_text_block.png")
    
    
# 文本检测结果说明

# 以下是OCR文本检测的JSON结果，包含了检测到的文本区域及其相关信息：

# ```json
# {
#     "input_path": "general_ocr_001.png",  // 输入图像的文件路径
#     "page_index": null,  // 页面索引，null表示不适用或单页面文档
#     "dt_polys": [  // 检测到的文本多边形区域，每个区域由四个坐标点[x,y]组成
#         [[73, 552], [453, 542], [454, 575], [74, 585]],  // 第1个文本区域的四个顶点坐标
#         [[17, 506], [515, 486], [517, 535], [19, 555]],  // 第2个文本区域的四个顶点坐标
#         [[189, 457], [398, 449], [399, 482], [190, 490]],  // 第3个文本区域的四个顶点坐标
#         [[41, 412], [484, 387], [486, 433], [43, 457]],  // 第4个文本区域的四个顶点坐标
#         [[510, 32], [525, 32], [525, 49], [510, 49]]  // 第5个文本区域的四个顶点坐标
#     ],
#     "dt_scores": [  // 每个检测区域的置信度得分，值范围0-1，越高表示越可信
#         0.7650322239059382,  // 第1个区域的置信度
#         0.7197010251844577,  // 第2个区域的置信度
#         0.8289373546662983,  // 第3个区域的置信度 (最高置信度)
#         0.7989932734846841,  // 第4个区域的置信度
#         0.7363050443898626   // 第5个区域的置信度
#     ]
# }
# ```

# ## 字段说明

# - **input_path**: 输入的图像文件路径
# - **page_index**: 多页文档的页码索引，null表示单页或不适用
# - **dt_polys**: 检测到的文本区域多边形，每个区域由4个点的坐标表示，按顺时针或逆时针排列
# - **dt_scores**: 对应每个文本区域的检测置信度，值越大表示检测结果越可靠

