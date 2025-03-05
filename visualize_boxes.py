"""
文件: visualize_boxes.py
描述: 处理版面分析结果并生成可视化输出和Markdown文件
作者: 筱可
微信公众号: 筱可AI研习社
日期: 2025-3-6
"""

import os
import json
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageColor
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from element_processors import ElementProcessorFactory


class DocumentElementProcessor:
    """文档元素处理器，处理版面分析结果并生成可视化和Markdown"""

    def __init__(self, output_dir="output", images_dir="images", font_path=None):
        """
        初始化文档元素处理器
        
        参数:
            output_dir: 输出根目录
            images_dir: 图像保存的子目录名
            font_path: 中文字体路径，如果为None将尝试查找系统字体
        """
        self.output_dir = output_dir
        self.images_dir = images_dir
        self.font_path = self._find_chinese_font() if font_path is None else font_path
        
        # 创建输出目录
        self.images_full_path = os.path.join(output_dir, images_dir)
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.images_full_path, exist_ok=True)
        
        # 元素类型颜色映射
        self.colors = {
            "text": (0, 0, 255),       # 红色
            "title": (255, 0, 0),      # 蓝色
            "table": (0, 255, 0),      # 绿色
            "image": (255, 255, 0),    # 青色
            "chart": (255, 0, 255),    # 品红
            "paragraph_title": (128, 0, 128),  # 紫色
            "table_title": (255, 165, 0),     # 橙色
            "chart_title": (128, 128, 0),     # 橄榄色
            "formula": (0, 128, 128),  # 墨绿色
            "abstract": (165, 42, 42)   # 棕色
        }
        
        # 默认颜色
        self.default_color = (128, 128, 128)  # 灰色
    
    def _find_chinese_font(self):
        """查找系统中可用的中文字体"""
        # 尝试常见的中文字体路径
        font_paths = [
            # Windows 字体
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            # Linux 字体
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            # macOS 字体
            "/System/Library/Fonts/PingFang.ttc",
            # 当前目录
            "SimHei.ttf",
            "simsun.ttc"
        ]
        
        # 尝试查找系统中的中文字体
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        # 如果找不到中文字体，尝试使用matplotlib的默认字体
        fonts = [f for f in fm.findSystemFonts() if os.path.basename(f).startswith(("sim", "Song", "Noto", "PingFang"))]
        if fonts:
            return fonts[0]
        
        print("警告：未找到中文字体，可能导致中文显示不正常")
        return None

    def process_document(self, layout_json_path, visualization_output_path, markdown_filename):
        """
        处理文档版面分析结果
        
        参数:
            layout_json_path: 版面分析JSON文件路径
            visualization_output_path: 可视化输出图像路径
            markdown_filename: 输出的Markdown文件名
            
        返回:
            bool: 处理成功返回True，否则返回False
        """
        try:
            # 读取版面分析结果
            with open(layout_json_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            # 获取原始图像路径
            document_image_path = layout_data.get("input_path")
            page_width = None
            
            if document_image_path and os.path.exists(document_image_path):
                # 读取图像获取宽度
                img = cv2.imread(document_image_path)
                if img is not None:
                    page_width = img.shape[1]  # 图像宽度
            else:
                print(f"警告：图像文件 {document_image_path} 不存在，将只处理元素结构")
                document_image_path = None
            
            # 处理元素
            elements = self._sort_elements(layout_data.get("boxes", []), page_width)
            
            # 生成可视化结果
            if document_image_path:
                self._visualize_elements(document_image_path, elements, visualization_output_path)
            
            # 生成Markdown文件
            self._generate_markdown(elements, document_image_path, markdown_filename)
            
            return True
        
        except Exception as e:
            print(f"处理文档时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _sort_elements(self, elements, page_width=None):
        """
        对元素按照左右栏进行排序：
        1. 根据元素在页面左右的覆盖比例判断其归属
        2. 如果元素90%以上位于页面左侧，归为左栏
        3. 如果元素90%以上位于页面右侧，归为右栏
        4. 如果元素横跨中线且两侧各占30%以上，归为左栏
        5. 左栏和右栏元素分别按垂直位置排序
        
        参数:
            elements: 元素列表
            page_width: 页面宽度，如果为None，则从元素坐标推断
            
        返回:
            list: 排序后的元素列表
        """
        # 筛选有效元素
        valid_elements = []
        for elem in elements:
            if "coordinate" in elem and len(elem["coordinate"]) == 4:
                valid_elements.append(elem)
        
        if not valid_elements:
            return []
        
        # 如果未提供页面宽度，则从元素坐标推断
        if page_width is None:
            page_width = max([elem["coordinate"][2] for elem in valid_elements])
            print(f"警告: 未提供页面宽度，从元素坐标推断为 {page_width}")
        
        # 页面中心点
        page_center_x = page_width / 2
        
        # 分左右栏
        left_column = []
        right_column = []
        
        for elem in valid_elements:
            x1, _, x2, _ = elem["coordinate"]
            elem_width = x2 - x1
            
            # 计算元素在页面左侧和右侧的部分
            left_part_width = max(0, min(x2, page_center_x) - x1)
            right_part_width = max(0, x2 - max(x1, page_center_x))
            
            # 计算左右覆盖比例
            left_ratio = left_part_width / elem_width if elem_width > 0 else 0
            right_ratio = right_part_width / elem_width if elem_width > 0 else 0
            
            # 根据覆盖比例判断元素归属
            if left_ratio >= 0.9:  # 90%以上在左侧
                left_column.append(elem)
            elif right_ratio >= 0.9:  # 90%以上在右侧
                right_column.append(elem)
            elif left_ratio > 0.3 and right_ratio > 0.3:  # 跨中线，两侧各占30%以上
                left_column.append(elem)  # 归为左栏
            else:  # 其他情况，根据元素中心点判断
                elem_center_x = (x1 + x2) / 2
                if elem_center_x <= page_center_x:
                    left_column.append(elem)
                else:
                    right_column.append(elem)
        
        # 按垂直位置排序（从上到下）
        left_column.sort(key=lambda e: e["coordinate"][1])  # 按y坐标起始点排序
        right_column.sort(key=lambda e: e["coordinate"][1])
        
        # 合并结果：先左栏，后右栏
        return left_column + right_column

    def _has_vertical_overlap(self, elem1, elem2, tolerance):
        """
        判断两个元素是否在垂直方向上有重叠
        
        参数:
            elem1, elem2: 两个需要比较的元素
            tolerance: 垂直方向的容差
            
        返回:
            bool: 是否有垂直重叠
        """
        # 获取元素垂直范围
        y1_top, y1_bottom = elem1["coordinate"][1], elem1["coordinate"][3]
        y2_top, y2_bottom = elem2["coordinate"][1], elem2["coordinate"][3]
        
        # 检查是否有重叠，考虑容差
        return (
            (y1_top <= y2_bottom + tolerance and y1_bottom >= y2_top - tolerance) or
            (y2_top <= y1_bottom + tolerance and y2_bottom >= y1_top - tolerance) or
            abs(elem1["center_y"] - elem2["center_y"]) <= tolerance
        )

    def _visualize_elements(self, image_path, elements, output_path):
        """
        将元素框可视化在原始图像上
        
        参数:
            image_path: 原始图像路径
            elements: 元素列表
            output_path: 输出图像路径
        """
        try:
            # 读取原始图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法加载图像: {image_path}")
            
            # 转换为RGB格式（OpenCV默认是BGR）
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 创建PIL图像对象
            pil_image = Image.fromarray(image_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # 加载中文字体
            font_size = 15
            try:
                if self.font_path:
                    font = ImageFont.truetype(self.font_path, font_size)
                else:
                    font = ImageFont.load_default()
            except Exception as e:
                print(f"加载字体失败: {e}")
                font = ImageFont.load_default()
            
            # 绘制每个元素的边界框和标签
            for i, elem in enumerate(elements):
                # 获取坐标和标签
                x1, y1, x2, y2 = [int(coord) for coord in elem["coordinate"]]
                label = elem.get("label", "unknown")
                score = elem.get("score", 0)
                
                # 获取颜色
                color_rgb = self.colors.get(label, self.default_color)
                
                # 绘制矩形框
                draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=2)
                
                # 绘制标签背景和文本
                text = f"{i+1}. {label} ({score:.2f})"
                text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:]
                draw.rectangle([x1, y1 - text_height - 2, x1 + text_width + 2, y1], fill=color_rgb)
                draw.text((x1 + 1, y1 - text_height - 1), text, fill=(255, 255, 255), font=font)
            
            # 保存结果
            pil_image.save(output_path)
            print(f"可视化结果已保存到: {output_path}")
            
        except Exception as e:
            print(f"可视化元素时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def _generate_markdown(self, elements, document_image_path, markdown_filename):
        """
        生成Markdown文档
        
        参数:
            elements: 元素列表
            document_image_path: 原始文档图像路径
            markdown_filename: 输出Markdown文件名
        """
        try:
            markdown_content = "# 文档内容\n\n"
            
            # 生成每个元素的Markdown内容
            for i, elem in enumerate(elements):
                # 使用工厂创建合适的元素处理器
                processor = ElementProcessorFactory.create_processor(
                    elem, i, document_image_path,
                    self.output_dir, self.images_dir
                )
                
                # 转换为Markdown并添加到内容中
                markdown_content += processor.to_markdown()
            
            # 写入Markdown文件
            markdown_path = os.path.join(self.output_dir, markdown_filename)
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Markdown文件已生成: {markdown_path}")
            
        except Exception as e:
            print(f"生成Markdown时出错: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    # 示例使用
    layout_json_path = "res.json"
    visualization_path = "visualization_result.png"
    markdown_filename = "document.md"
    
    processor = DocumentElementProcessor()
    processor.process_document(layout_json_path, visualization_path, markdown_filename)
