import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List
from layout_config import LayoutConfig

class LayoutVisualizer:
    def __init__(self, font_path: str = None, font_size: int = 24):  # 修改默认字体大小为24
        """初始化可视化器
        
        Args:
            font_path: 字体文件路径，默认使用PIL默认字体
            font_size: 字体大小，默认24
        """
        self.font = ImageFont.load_default()
        if font_path:
            try:
                self.font = ImageFont.truetype(font_path, font_size)
            except:
                print("无法加载指定字体，使用默认字体")
        
        # 使用配置文件中的颜色设置
        self.colors = LayoutConfig.COLORS
        self.default_color = LayoutConfig.DEFAULT_COLOR
        
    def draw_boxes(self, image: np.ndarray, boxes: List[Dict], 
                  show_order: bool = True, show_label: bool = True) -> np.ndarray:
        """绘制排序后的检测框
        
        Args:
            image: 原始图像(RGB格式)
            boxes: 排序后的检测框列表
            show_order: 是否显示排序顺序
            show_label: 是否显示标签类型
            
        Returns:
            绘制了检测框的图像
        """
        # 转换为PIL图像
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # 绘制每个元素
        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box['coordinate'])
            label = box['label']
            score = box.get('score', 0)
            color = self.colors.get(label, self.default_color)
            
            # 绘制矩形框
            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            
            # 准备标注文本
            text_elements = []
            if show_order:
                text_elements.append(f"#{i+1}")
            if show_label:
                text_elements.append(f"{label}")
                if score > 0:
                    text_elements.append(f"{score:.2f}")
            text = " ".join(text_elements)
            
            if text:
                # 获取文本尺寸
                text_bbox = draw.textbbox((0, 0), text, font=self.font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # 绘制文本背景
                draw.rectangle(
                    [x1, y1 - text_height - 8, x1 + text_width + 8, y1],  # 增加内边距
                    fill=color
                )
                
                # 绘制文本
                draw.text(
                    (x1 + 4, y1 - text_height - 4),  # 调整文本位置
                    text,
                    fill=(255, 255, 255),
                    font=self.font
                )
        
        # 转换回OpenCV格式
        result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        return result

    def save_visualization(self, image_path: str, boxes: List[Dict], 
                         output_path: str,
                         show_order: bool = True,
                         show_label: bool = True) -> None:
        """保存可视化结果
        
        Args:
            image_path: 原始图像路径
            boxes: 排序后的检测框列表
            output_path: 输出图像路径
            show_order: 是否显示排序顺序
            show_label: 是否显示标签类型
        """
        # 读取原始图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        # 绘制检测框
        result = self.draw_boxes(image, boxes, show_order, show_label)
        
        # 保存结果
        cv2.imwrite(output_path, result)
        print(f"可视化结果已保存至: {output_path}")
