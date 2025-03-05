"""
File: element_processors.py
Description: 文档各类元素的处理器，负责将各种元素转换为Markdown格式
Author: 筱可
wechat-public: 筱可AI研习社
Date: 2025-3-5
"""

import os
import cv2
from abc import ABC, abstractmethod


class ElementProcessor(ABC):
    """元素处理器抽象基类"""

    def __init__(self, element, index, document_image_path=None, 
                 output_dir=".", images_dir="images"):
        """
        初始化元素处理器

        参数:
            element: 元素数据
            index: 元素在文档中的索引
            document_image_path: 原始文档图像路径（对于需要提取图像的元素）
            output_dir: 输出目录路径
            images_dir: 图片存储的相对目录名（相对于output_dir）
        """
        self.element = element
        self.index = index
        self.document_image_path = document_image_path
        self.label = element["label"]
        self.coordinates = element["coordinate"]
        
        # 路径参数
        self.output_dir = output_dir
        self.images_dir = images_dir
        
        # 创建图像目录（如果不存在）
        self.images_path = os.path.join(output_dir, images_dir)
        os.makedirs(self.images_path, exist_ok=True)

    @abstractmethod
    def to_markdown(self):
        """将元素转换为Markdown格式的字符串"""
        pass

    def extract_element_image(self, filename):
        """
        从原始文档图像中提取元素图像

        参数:
            filename: 输出图像文件名（不含路径）

        返回:
            tuple: (是否成功提取, 图像文件保存路径)
        """
        if not self.document_image_path:
            return False, None

        try:
            # 构建完整的输出路径
            output_filepath = os.path.join(self.images_path, filename)
            
            # 提取坐标
            x1, y1, x2, y2 = [int(coord) for coord in self.coordinates]

            # 读取原始图像
            full_image = cv2.imread(self.document_image_path)
            if full_image is None:
                return False, None

            # 裁剪元素图像
            cropped_element = full_image[y1:y2, x1:x2]

            # 保存裁剪后的图像
            cv2.imwrite(output_filepath, cropped_element)
            return True, output_filepath
        
        except Exception as e:
            print(f"提取元素图像时出错: {str(e)}")
            return False, None


class TitleProcessor(ElementProcessor):
    """标题元素处理器"""

    def __init__(self, element, index, document_image_path=None, 
                 output_dir=".", images_dir="images"):
        # 修复：移除了image_ref_style参数，确保参数与父类匹配
        super().__init__(element, index, document_image_path, 
                         output_dir, images_dir)
        # 标题层级映射
        self.title_levels = {
            "doc_title": 1,  # 一级标题
            "paragraph_title": 2,  # 二级标题
        }

    def to_markdown(self):
        """将标题元素转换为Markdown格式"""
        level = self.title_levels.get(self.label, 2)  # 默认为二级标题

        # 根据标题类型生成标题文本
        if self.label == "table_title":
            title_type = "表格"
        elif self.label == "chart_title":
            title_type = "图表"
        elif self.label == "figure_title":
            title_type = "图片"
        elif self.label == "doc_title":
            title_type = "文档标题"
        else:
            title_type = "段落标题"

        # 生成合适层级的Markdown标题，包含序号
        heading = "#" * level
        return f"{heading} {self.index+1}. {title_type}元素\n\n"


class TextProcessor(ElementProcessor):
    """文本元素处理器"""

    def to_markdown(self):
        """将文本元素转换为Markdown格式"""
        # 纯文本内容，不包含序号或元素类型
        return "正文内容\n\n"


class ImageProcessor(ElementProcessor):
    """图像元素处理器 (包括图表、表格图像等)"""

    def __init__(self, element, index, document_image_path=None, 
                 output_dir=".", images_dir="images"):
        super().__init__(element, index, document_image_path, 
                         output_dir, images_dir)
        self.image_type_map = {"image": "图片", "chart": "图表", "table": "表格"}

    def to_markdown(self):
        """将图像元素转换为Markdown格式"""
        # 确定元素类型和输出文件名
        element_type = self.label  # 例如 "image", "chart", "table"
        filename = f"{element_type}_{self.index+1}.png"

        # 尝试提取元素图像
        if self.document_image_path:
            success, _ = self.extract_element_image(filename)
            if not success:
                return f"*无法提取{self.image_type_map.get(element_type, '图像')}元素*\n\n"
            
            # 在Markdown中使用相对于MD文件的路径引用图片
            # 这样当Markdown文件位于output_dir，而图片位于output_dir/images_dir时
            # 引用路径就是images_dir/filename
            return f"![{self.image_type_map.get(element_type, '图像')}]({self.images_dir}/{filename})\n\n"
        
        return f"*缺少图像源文件*\n\n"


class FormulaProcessor(ElementProcessor):
    """公式元素处理器"""

    def to_markdown(self):
        """将公式元素转换为Markdown格式"""
        return "公式\n\n"


class TableProcessor(ElementProcessor):
    """表格元素处理器 - 后续将与表格识别模型结合"""

    def __init__(self, element, index, document_image_path=None, table_md_content=None,
                 output_dir=".", images_dir="images"):
        super().__init__(element, index, document_image_path, 
                         output_dir, images_dir)
        # 表格的Markdown内容，将由外部表格识别模型提供
        self.table_md_content = table_md_content

    def to_markdown(self):
        """将表格元素转换为Markdown格式"""
        # 如果已有表格识别结果，直接使用
        if self.table_md_content:
            return f"{self.table_md_content}\n\n"

        # 否则，使用默认图像处理方式
        # 创建一个图像处理器来处理表格图像
        image_processor = ImageProcessor(
            self.element, self.index, self.document_image_path,
            self.output_dir, self.images_dir
        )
        return image_processor.to_markdown()

    def set_table_content(self, markdown_content):
        """设置表格的Markdown内容

        参数:
            markdown_content: 表格的Markdown内容字符串
        """
        self.table_md_content = markdown_content


class ElementProcessorFactory:
    """元素处理器工厂，根据元素类型创建相应的处理器"""

    @staticmethod
    def create_processor(element, index, document_image_path=None,
                         output_dir=".", images_dir="images"):
        """
        创建合适的元素处理器

        参数:
            element: 元素数据
            index: 元素索引
            document_image_path: 文档图像路径
            output_dir: 输出目录路径
            images_dir: 图片存储的相对目录名

        返回:
            ElementProcessor: 相应类型的处理器实例
        """
        label = element["label"]

        # 根据元素类型创建相应的处理器
        if label in [
            "doc_title",
            "paragraph_title",
            "table_title",
            "chart_title",
            "figure_title",
        ]:
            return TitleProcessor(element, index, document_image_path, 
                                 output_dir, images_dir)
        elif label in ["text", "abstract"]:
            return TextProcessor(element, index, document_image_path,
                                output_dir, images_dir)
        elif label == "formula":
            return FormulaProcessor(element, index, document_image_path,
                                   output_dir, images_dir)
        elif label == "table":
            return TableProcessor(element, index, document_image_path, None,
                                 output_dir, images_dir)
        elif label in ["image", "chart"]:
            return ImageProcessor(element, index, document_image_path,
                                 output_dir, images_dir)
        else:
            # 默认使用文本处理器
            return TextProcessor(element, index, document_image_path,
                                output_dir, images_dir)
