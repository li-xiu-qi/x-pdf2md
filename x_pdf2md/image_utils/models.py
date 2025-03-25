from typing import Any, Dict

from paddlex import create_model

from x_pdf2md.config import get_model_config

# 全局模型字典，用于存储已加载的模型
_GLOBAL_MODELS: Dict[str, Any] = {}

def get_or_create_model(model_type: str) -> Any:
    """
    获取或创建模型，实现模型的全局注册

    Args:
        model_type: 模型类型

    Returns:
        已加载的模型实例
    """
    global _GLOBAL_MODELS

    # 如果模型已经加载，直接返回
    if model_type in _GLOBAL_MODELS and _GLOBAL_MODELS[model_type] is not None:
        return _GLOBAL_MODELS[model_type]

    # 否则，从配置中获取模型名称并加载
    model_name = get_model_config(model_type)
    try:
        model = create_model(model_name=model_name)
        _GLOBAL_MODELS[model_type] = model
        print(f"模型 {model_type} 加载成功")
        return model
    except Exception as e:
        print(f"模型 {model_type} 加载失败: {e}")
        return None
