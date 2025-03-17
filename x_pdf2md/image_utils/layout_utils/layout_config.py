from typing import Dict, List, Tuple

class LayoutConfig:
    # 可视化颜色配置 (RGB格式)
    COLORS: Dict[str, Tuple[int, int, int]] = {
        # 标题类
        'doc_title': (255, 0, 128),     # 品红色
        'paragraph_title': (255, 0, 0),  # 红色
        'figure_title': (128, 0, 255),   # 紫色
        'table_title': (255, 140, 0),    # 深橙色
        'chart_title': (0, 215, 255),    # 浅青色
        
        # 正文类
        'text': (0, 255, 0),             # 绿色
        'abstract': (0, 255, 191),       # 绿松石色
        'aside_text': (152, 251, 152),   # 浅绿色
        'footnote': (144, 238, 144),     # 淡绿色
        
        # 图表类
        'image': (0, 0, 255),            # 蓝色
        'chart': (0, 255, 255),          # 青色
        'table': (255, 165, 0),          # 橙色
        
        # 公式和数字类
        'formula': (255, 255, 0),        # 黄色
        'formula_number': (255, 215, 0),  # 金色
        'number': (218, 165, 32),        # 金麦色
        
        # 页眉页脚类
        'header': (169, 169, 169),       # 深灰色
        'footer': (192, 192, 192),       # 浅灰色
    }
    DEFAULT_COLOR: Tuple[int, int, int] = (128, 128, 128)  # 灰色，用于未定义颜色的标签

    # 需要进一步处理的标签 (白名单)
    PROCESS_LABELS: List[str] = [
        'paragraph_title', 'image', 'text', 
        'abstract', 'figure_title', 'formula',
        'table_title', 'doc_title','table', 
        'chart', 'chart_title','formula_number'
    ]
    
    # 需要过滤掉的标签 (黑名单)
    FILTER_LABELS: List[str] = [
        'footnote', 'header', 'footer',  
        'aside_text', 'number'
    ]
    
    # 已知的所有标签及其ID (用于检测未知标签)
    KNOWN_LABELS: Dict[int, str] = {
        0: 'paragraph_title',
        1: 'image',
        2: 'text',
        3: 'number',
        4: 'abstract',
        6: 'figure_title',
        7: 'formula',
        8: 'table',
        9: 'table_title',
        11: 'doc_title',
        12: 'footnote',
        13: 'header',
        15: 'footer',
        17: 'chart_title',
        18: 'chart',
        19: 'formula_number',
        22: 'aside_text',
    }
