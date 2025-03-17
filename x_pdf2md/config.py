#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块 - 集中管理项目配置
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 默认配置
DEFAULT_CONFIG = {
    # API配置
    "API_KEY": os.getenv("API_KEY", ""),  # 从环境变量获取API密钥
    "BASE_URL": os.getenv("BASE_URL", "https://api.siliconflow.cn/v1"),  # API基础URL

    # 图片服务配置
    "IMAGE_HOST": os.getenv("HOST", "0.0.0.0"),  # 图片服务器主机
    "IMAGE_PORT": int(os.getenv("PORT", "8100")),  # 图片服务器端口
    "UPLOAD_DIR": os.getenv("UPLOAD_DIR", "./uploads"),  # 图片上传目录

    # 模型配置
    "FORMULA_MODEL": os.getenv("FORMULA_MODEL", "PP-FormulaNet-L"),  # 公式识别模型
    "OCR_DET_MODEL": os.getenv("OCR_DET_MODEL", "PP-OCRv4_mobile_det"),  # OCR检测模型
    "OCR_REC_MODEL": os.getenv("OCR_REC_MODEL", "PP-OCRv4_mobile_rec"),  # OCR识别模型
    "LAYOUT_MODEL": os.getenv("LAYOUT_MODEL", "PP-DocLayout-L"),  # 版面分析模型 (更新为PP-DocLayout-L)

    # 处理配置
    "DEFAULT_DPI": int(os.getenv("DEFAULT_DPI", "300")),  # 默认DPI
    "THRESHOLD_LEFT_RIGHT": float(os.getenv("THRESHOLD_LEFT_RIGHT", "0.9")),  # 左右栏阈值
    "THRESHOLD_CROSS": float(os.getenv("THRESHOLD_CROSS", "0.3")),  # 跨栏阈值
}

# 运行时配置(可覆盖默认配置)
_runtime_config = {}

def get_config() -> Dict[str, Any]:
    """
    获取当前配置(默认配置+运行时配置)
    
    Returns:
        Dict: 合并后的配置字典
    """
    config = DEFAULT_CONFIG.copy()
    config.update(_runtime_config)
    return config

def set_config(key: str, value: Any) -> None:
    """
    设置运行时配置
    
    Args:
        key: 配置键名
        value: 配置值
    """
    _runtime_config[key] = value

def update_config(config_dict: Dict[str, Any]) -> None:
    """
    批量更新运行时配置
    
    Args:
        config_dict: 配置字典
    """
    _runtime_config.update(config_dict)

def get_api_key() -> str:
    """获取API密钥"""
    return get_config()["API_KEY"]

def get_base_url() -> str:
    """获取API基础URL"""
    return get_config()["BASE_URL"]

def get_model_config(model_type: str) -> str:
    """
    获取特定类型的模型配置
    
    Args:
        model_type: 模型类型，如'formula', 'ocr_det', 'ocr_rec', 'layout'
        
    Returns:
        str: 模型名称
    """
    model_map = {
        'formula': 'FORMULA_MODEL',
        'ocr_det': 'OCR_DET_MODEL',
        'ocr_rec': 'OCR_REC_MODEL',
        'layout': 'LAYOUT_MODEL'
    }
    
    key = model_map.get(model_type)
    if not key:
        raise ValueError(f"未知的模型类型: {model_type}")
    
    return get_config()[key]
