#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author：筱可
# 2023-11-06
"""
使用说明：
    通过调用recognize_formula函数传入公式图片路径，识别其中的数学公式并返回LaTeX格式结果。

主要功能：
    1. 加载公式识别模型PP-FormulaNet-L
    2. 对输入的图像进行公式识别
    3. 将识别结果保存为JSON并返回公式文本

参数说明：
    recognize_formula函数：
        input_path: str - 输入图像路径
        output_dir: str - 输出目录，默认为"./UniMERNet_output/"
        model_name: str - 模型名称，默认为"PP-FormulaNet-L"
        返回值: str - 识别出的LaTeX格式公式

注意事项：
    - 需要预先安装paddlex库
    - 首次运行时会自动下载预训练模型
    - 输出目录需要有写入权限
"""

import json
from typing import Dict, Any, List
from paddlex import create_model


def recognize_formula(input_path: str, output_dir: str = "./UniMERNet_output/", model_name: str = "PP-FormulaNet-L") -> str:
    """
    识别图像中的公式
    
    参数:
        input_path: 输入图像路径
        output_dir: 输出目录，默认为"./UniMERNet_output/"
        model_name: 模型名称，默认为"PP-FormulaNet-L"
    
    返回:
        str: 识别出的LaTeX格式公式
    """
    # 创建模型实例
    model = create_model(model_name=model_name)
    # 预测图像内容
    output: List[Any] = model.predict(input=input_path, batch_size=1)
    
    # 保存结果到JSON文件
    for res in output:
        res.save_to_json(save_path=f"{output_dir}res.json")

    # 读取JSON文件获取识别结果
    with open(f"{output_dir}res.json", 'r') as f:
        results: Dict[str, Any] = json.load(f)
        
    rec_formula: str = results["rec_formula"]
    
    return rec_formula


# 使用示例
if __name__ == "__main__":
    results: str = recognize_formula("formula.png")
    print(f"识别结果: {results}")
    
    
# 公式识别结果说明文档

## 结果JSON格式解析

# 公式识别模块 (PP-FormulaNet-L) 输出的JSON文件结构说明：

# ```json
# {
#     "input_path": "general_formula_rec_001.png",  // 输入图像的文件路径
#     "page_index": null,                           // 页面索引，若输入为单页则为null
#     "rec_formula": "\\zeta_{0}(\\nu)=-\\frac{\\nu\\varrho^{-2\\nu}}{\\pi}\\int_{\\mu}^{\\infty}d\\omega\\int_{C_{+}}d z\\frac{2z^{2}}{(z^{2}+\\omega^{2})^{\\nu+1}}\\check{\\Psi}(\\omega;z)e^{i\\epsilon z}\\quad,"  // 识别出的LaTeX格式公式
# }
# ```

# ## 字段说明

# - **input_path**: 输入的图像文件名或路径，标识被识别的源图像
# - **page_index**: 对于多页文档，表示当前公式所在的页码；对于单页图像，该值为null
# - **rec_formula**: 模型识别结果，以LaTeX格式表示的数学公式

# ## 当前识别结果

# 当前识别的公式是一个复杂的数学表达式，通过PP-FormulaNet-L模型转换为LaTeX代码。这个公式的数学表示为：

# $$\zeta_{0}(\nu)=-\frac{\nu\varrho^{-2\nu}}{\pi}\int_{\mu}^{\infty}d\omega\int_{C_{+}}d z\frac{2z^{2}}{(z^{2}+\omega^{2})^{\nu+1}}\check{\Psi}(\omega;z)e^{i\epsilon z}\quad,$$

# ## 使用说明

# 识别结果可以直接复制到支持LaTeX的编辑器中使用，如Overleaf、MathJax支持的网站或Word的公式编辑器中。

# ## 模型信息

# 该结果由PP-FormulaNet-L模型生成，这是百度飞桨视觉团队开发的公式识别模型，基于Vary_VIT_B骨干网络，适用于简单印刷公式、复杂印刷公式、手写公式等多种场景。
