from dataclasses import dataclass


@dataclass
class RegionImage:
    """表示文档中的一个区域图片"""
    image_path: str  # 图片文件路径
    label: str  # 区域标签 (如 'text', 'title' 等)
    score: float  # 检测置信度分数
    page_number: int  # 页码
    region_index: int  # 区域在页面中的序号
    original_box: list  # 原始边界框坐标 [x1,y1,x2,y2]
    content: str = None  # 识别出的内容
    contains: list = None  # 包含的区域

    def __str__(self) -> str:
        return f"RegionImage(label={self.label}, page={self.page_number}, index={self.region_index}, path={self.image_path})"
