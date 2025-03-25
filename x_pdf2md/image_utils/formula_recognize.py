#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
公式识别模块 - 从图像中识别数学公式并转换为LaTeX格式
"""

import json
import os
from typing import Optional, Dict, Any

from x_pdf2md.image_utils.models import get_or_create_model



def recognize_formula(input_path: str, output_path: Optional[str] = None) -> str:
    """
    识别图像中的数学公式
    
    Args:
        input_path: 输入图像路径
        output_path: 输出结果保存路径(可选)
    
    Returns:
        str: LaTeX格式的公式文本
    """
    print(f"处理公式图片: {input_path}")
    
    # 确保输出目录存在
    output_dir = "./UniMERNet_output/" if output_path is None else os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取或创建模型
    model = get_or_create_model('formula')
    

    if model is None:
        raise Exception("模型加载失败")

    output = model.predict(input=input_path, batch_size=1)

    for res in output:
        res_path = output_path or f"{output_dir}/res.json"
        res.save_to_json(save_path=res_path)

        # 读取json文件
        with open(res_path, 'r') as f:
            results = json.load(f)

    rec_formula = results.get("rec_formula", "")

    # 如果公式为空，返回一个默认值
    if not rec_formula:
        return ""

    return rec_formula




if __name__ == "__main__":
    # 测试公式识别
    test_image = "image.png"
    latex = recognize_formula(test_image)
    print(f"识别结果: {latex}")
