"""
布局处理模块
负责文档版面分析和处理
"""

import cv2
import json
import os
import time
from typing import Dict, List, Any
from paddlex import create_model

from image_utils.layout_utils.layout_config import LayoutConfig


def is_box_inside(box1: List[float], box2: List[float]) -> bool:
    """
    判断box1是否在box2内部（如果box1有80%以上区域被box2包含，则视为被包含）
    
    参数:
        box1: [x1, y1, x2, y2] 格式的框坐标
        box2: [x1, y1, x2, y2] 格式的框坐标
    
    返回:
        bool: 如果box1有80%以上区域被box2包含，返回True，否则返回False
    """
    # 计算box1的面积
    area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    
    # 计算交集的坐标
    intersect_x1 = max(box1[0], box2[0])
    intersect_y1 = max(box1[1], box2[1])
    intersect_x2 = min(box1[2], box2[2])
    intersect_y2 = min(box1[3], box2[3])
    
    # 如果没有交集，直接返回False
    if intersect_x1 >= intersect_x2 or intersect_y1 >= intersect_y2:
        return False
    
    # 计算交集的面积
    intersection_area = (intersect_x2 - intersect_x1) * (intersect_y2 - intersect_y1)
    
    # 计算交集面积占box1面积的比例
    overlap_ratio = intersection_area / area_box1
    
    # 如果交集面积占box1面积的比例大于等于0.8，则视为被包含
    return overlap_ratio >= 0.8

def build_box_hierarchy(boxes: List[Dict]) -> List[Dict]:
    """
    为每个框添加包含关系，并移除嵌套在其他框内部的框
    
    参数:
        boxes: 包含框信息的字典列表，每个字典包含coordinate字段
        
    返回:
        List[Dict]: 添加了包含关系的框列表
    """
    n = len(boxes)
    is_nested = [False] * n
    
    # 为每个框添加contains属性
    for i in range(n):
        boxes[i]["contains"] = []
    
    # 检查每个框是否被其他框包含
    for i in range(n):
        box1 = boxes[i]["coordinate"]
        for j in range(n):
            if i != j:
                box2 = boxes[j]["coordinate"]
                if is_box_inside(box1, box2):
                    is_nested[i] = True
                    # 将被包含的框添加到外部框的contains列表中
                    boxes[j]["contains"].append(boxes[i])
                    break
    
    # 只保留不是嵌套框的框
    result = []
    for i in range(n):
        if not is_nested[i]:
            result.append(boxes[i])
            
    return result

def calculate_boundary_distance(box1: List[float], box2: List[float]) -> float:
    """
    计算两个框之间的最小边界距离
    
    参数:
        box1: [x1, y1, x2, y2] 格式的框坐标
        box2: [x1, y1, x2, y2] 格式的框坐标
    
    返回:
        float: 两个框之间的最小距离，如果重叠则为0
    """
    # 计算水平方向上的距离
    if box1[0] > box2[2]:  # box1在box2右侧
        horizontal_dist = box1[0] - box2[2]
    elif box2[0] > box1[2]:  # box2在box1右侧
        horizontal_dist = box2[0] - box1[2]
    else:  # 水平方向上有重叠
        horizontal_dist = 0
    
    # 计算垂直方向上的距离
    if box1[1] > box2[3]:  # box1在box2下方
        vertical_dist = box1[1] - box2[3]
    elif box2[1] > box1[3]:  # box2在box1下方
        vertical_dist = box2[1] - box1[3]
    else:  # 垂直方向上有重叠
        vertical_dist = 0
    
    # 计算欧几里得距离
    return (horizontal_dist ** 2 + vertical_dist ** 2) ** 0.5

def merge_formula_numbers(boxes: List[Dict]) -> List[Dict]:
    """
    将公式序号框融合到最近的公式框中，优先考虑序号左侧的公式框
    
    参数:
        boxes: 包含框信息的字典列表
        
    返回:
        List[Dict]: 处理后的框列表，原始列表不会被修改
    """
    # 识别所有公式框和公式序号框
    formula_boxes = [box for box in boxes if box.get("label") == "formula"]
    formula_number_boxes = [box for box in boxes if box.get("label") == "formula_number"]
    
    # 如果没有公式序号框或公式框，直接返回原列表的副本
    if not formula_number_boxes or not formula_boxes:
        return boxes.copy()
    
    # 创建结果列表，首先加入除了公式框和公式序号框外的所有框
    result_boxes = []
    formula_ids = [id(box) for box in formula_boxes]
    formula_number_ids = [id(box) for box in formula_number_boxes]
    
    # 复制非公式和非公式序号的框到结果列表
    for box in boxes:
        if id(box) not in formula_ids and id(box) not in formula_number_ids:
            result_boxes.append(box.copy())
    
    # 处理公式框，为每个公式框创建副本
    processed_formula_boxes = []
    for formula_box in formula_boxes:
        new_formula_box = formula_box.copy()
        new_formula_box["formula_numbers"] = []
        processed_formula_boxes.append(new_formula_box)
    
    # 对于每个公式序号框，找到最合适的公式框并融合
    for number_box in formula_number_boxes:
        number_coord = number_box["coordinate"]
        
        # 计算公式序号框的左边缘和中心点
        number_left = number_coord[0]
        number_center_y = (number_coord[1] + number_coord[3]) / 2
        
        # 定义垂直容忍度（公式中心点和序号中心点的垂直距离允许范围）
        vertical_tolerance = (number_coord[3] - number_coord[1]) * 2  # 序号高度的2倍
        
        # 筛选出垂直方向上大致对齐的公式框
        aligned_formulas = []
        for formula_box in processed_formula_boxes:
            formula_coord = formula_box["coordinate"]
            formula_center_y = (formula_coord[1] + formula_coord[3]) / 2
            
            # 检查垂直方向上是否对齐
            if abs(formula_center_y - number_center_y) <= vertical_tolerance:
                aligned_formulas.append(formula_box)
        
        # 先尝试找位于序号左侧的公式框（公式在左，序号在右）
        left_side_formulas = []
        for formula_box in aligned_formulas:
            formula_coord = formula_box["coordinate"]
            formula_right = formula_coord[2]  # 公式框的右边缘
            
            # 如果公式框的右边缘在序号框的左边缘的左侧或接近（允许少量重叠）
            if formula_right <= number_left + (number_coord[2] - number_left) * 0.2:  # 允许20%的重叠
                left_side_formulas.append(formula_box)
        
        closest_formula = None
        
        # 如果找到了位于序号左侧的公式框
        if left_side_formulas:
            # 选择最近的一个（公式右边缘离序号左边缘最近的）
            min_distance = float('inf')
            for formula_box in left_side_formulas:
                formula_coord = formula_box["coordinate"]
                formula_right = formula_coord[2]
                
                distance = number_left - formula_right
                
                if distance < min_distance:
                    min_distance = distance
                    closest_formula = formula_box
        
        # 如果没有找到位于序号左侧的公式框，则在所有垂直对齐的公式框中选择距离最近的
        elif aligned_formulas:
            min_distance = float('inf')
            for formula_box in aligned_formulas:
                formula_coord = formula_box["coordinate"]
                formula_center_x = (formula_coord[0] + formula_coord[2]) / 2
                number_center_x = (number_coord[0] + number_coord[2]) / 2
                
                distance = abs(formula_center_x - number_center_x)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_formula = formula_box
        
        # 如果仍然没有找到合适的公式框，退回到使用边界距离
        else:
            min_distance = float('inf')
            for formula_box in processed_formula_boxes:
                formula_coord = formula_box["coordinate"]
                
                # 使用边界距离替代中心点距离
                distance = calculate_boundary_distance(formula_coord, number_coord)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_formula = formula_box
        
        if closest_formula:
            # 融合公式框和公式序号框
            # 取两个框的并集作为新的公式框
            closest_formula["coordinate"] = [
                min(closest_formula["coordinate"][0], number_coord[0]),
                min(closest_formula["coordinate"][1], number_coord[1]),
                max(closest_formula["coordinate"][2], number_coord[2]),
                max(closest_formula["coordinate"][3], number_coord[3])
            ]
            
            # 添加公式序号的详细信息
            closest_formula["formula_numbers"].append({
                "coordinate": number_coord,
                "score": number_box.get("score", 0),
                "text": number_box.get("text", "")
            })
    
    # 将处理后的公式框添加到结果列表
    result_boxes.extend(processed_formula_boxes)
    
    return result_boxes

def detect_layout(image_path: str, output_path: str = "./layout_output/layout_detection.json",model_name= "PP-DocLayout-L") -> Dict:
    """
    检测文档版面布局

    参数:
        image_path: 图像路径
        output_dir: 输出目录

    返回:
        版面分析结果
    """
    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置json输出路径
    json_path = output_path if output_path.endswith(".json") else os.path.join(output_dir, "layout_detection.json")

    model = create_model(model_name=model_name)
    output = model.predict(image_path, batch_size=1, layout_nms=True)

    # 保存结果到JSON
    for res in output:
        res.save_to_json(save_path=json_path)
        res.save_to_img("./output/layout_result.jpg")

    # 读取JSON文件
    with open(json_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    
    # 过滤掉不需要处理的标签
    result["boxes"] = [box for box in result["boxes"] if box.get("label") not in LayoutConfig.FILTER_LABELS]
    
    # 合并公式和公式序号
    result["boxes"] = merge_formula_numbers(result["boxes"])
    
    # 构建框层次结构
    result["boxes"] = build_box_hierarchy(result["boxes"])
    # json dump到文件，使用json_path并在文件后面加入final标记
    final_json_path = json_path.replace(".json", "_final.json")
    print("Final JSON path:", final_json_path)
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


if __name__ == "__main__":
    image_path = "./formula_inline.png"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    # 测试文档版面分析
    result = detect_layout(image_path=image_path, output_path=os.path.join(output_dir, "layout_detection.json"))



# 布局检测结果分析

## 检测信息

# - 输入图片：layout.png
# - 检测项目：页面布局元素
# - 总检测框数：13

# ## 检测结果详情

# 检测到的元素类型统计：

# - 表格(table): 2个
# - 正文(text): 5个
# - 表格标题(table_title): 2个
# - 段落标题(paragraph_title): 4个

# ```json
# {
#     // 输入图片路径
#     "input_path": "layout.png",
#     "page_index": null,
#     "boxes": [
#         // 表格区域 1
#         {
#             "cls_id": 8,
#             "label": "table",
#             "score": 0.9866,  // 置信度 98.66%
#             "coordinate": [74.31, 105.71, 321.99, 299.11]  // [x1, y1, x2, y2]
#         },
#         // 正文区域 1
#         {
#             "cls_id": 2,
#             "label": "text",
#             "score": 0.9860,  // 置信度 98.60%
#             "coordinate": [34.66, 349.91, 358.34, 611.34]  // [x1, y1, x2, y2]
#         },
#        ……
#     ]
# }
# ```

# ## 注意事项

# 1. coordinate 坐标格式为 [x1, y1, x2, y2]，表示检测框的左上角和右下角坐标
# 2. score 表示检测结果的置信度，范围 0-1
# 3. cls_id 对应关系：
#    - 0: paragraph_title
#    - 2: text
#    - 8: table
#    - 9: table_title
#    - 7: formula
#    - 19: formula_number
