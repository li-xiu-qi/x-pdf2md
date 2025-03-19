from typing import List, Optional
import os

from x_pdf2md.image2md.get_image_title import get_image_title
from x_pdf2md.image2md.vlm_function import extract_table_from_image, extract_text_from_image, describe_image
from x_pdf2md.image_utils.formula_recognize import recognize_formula
from x_pdf2md.ocr_utils.ocr_image import OCRProcessor
from x_pdf2md.remote_image.image_uploader import ImageUploader
from x_pdf2md.image_utils.region_image import RegionImage

ocr_processor = OCRProcessor()

def format_region_content(
    region: RegionImage, 
    image_upload_obj: Optional[ImageUploader] = None,
    output_dir: Optional[str] = None
) -> None:
    """
    根据区域标签类型生成或增强内容

    参数:
        region: RegionImage对象
        image_upload_obj: 可选的图片上传器对象
        output_dir: 可选的输出目录，用于保存处理结果
    """

    # 获取标签
    label = region.label
    # 清空区域内容
    region.content = ""
    # 默认内容为空
    content = ""
    
    # 使用图片路径
    image_path = region.image_path
    
    # 排除图片相关部分，这些已在format_region中单独处理
    if label in ["image", "figure", "chart"]:
        print("处理图片：", image_path)
        # 获取图片描述
        image_describe = describe_image(image_path)
        print("图片描述：", image_describe)
        
        # 如果有图片路径且有上传器，尝试上传
        image_title = get_image_title(image_describe)
        if not image_title:
            image_title = f"{label}_{region.region_index+1}"
        print(f"处理图片: {image_title}")
        
        # 如果指定了输出目录，可以在这里处理输出相关的逻辑
        result_path = image_path
        if output_dir:
            # 这里可以添加将处理结果保存到输出目录的逻辑
            # 例如: 复制图片到输出目录或者生成新的输出文件
            result_filename = os.path.basename(image_path)
            result_path = os.path.join(output_dir, result_filename)
            
        # 如果有图片路径且有上传器，尝试上传
        if image_path and image_upload_obj:
            print(f"上传图片: {image_path}")
            try:
                # 上传图片
                image_url = image_upload_obj.upload(image_path)
                # 如果上传成功，使用图片URL
                if image_url:
                    content = f"![{image_title}]({image_url})\n\n" + (
                        f"**{image_title}描述:** {region.content}"
                        if region.content
                        else ""
                    )
            except Exception as e:
                print(f"图片上传失败: {e}")
        else:
            # 如果有输出目录，将图片复制到images子文件夹并使用相对路径
            if output_dir:
                # 创建images子文件夹
                images_dir = os.path.join(output_dir, "images")
                os.makedirs(images_dir, exist_ok=True)
                
                # 获取原图片的文件名
                image_filename = os.path.basename(image_path)
                # 构建目标路径
                target_image_path = os.path.join(images_dir, image_filename)
                
                # 复制图片到目标路径
                import shutil
                try:
                    shutil.copy2(image_path, target_image_path)
                    print(f"图片已复制到: {target_image_path}")
                    # 使用相对路径引用图片
                    image_rel_path = f"./images/{image_filename}"
                    content = f"![{image_title}]({image_rel_path})\n\n" + (
                        f"**{image_title}描述:** {region.content}" if region.content else ""
                    )
                except Exception as e:
                    print(f"复制图片失败: {e}")
                    # 失败时回退到使用原始路径
                    content = f"![{image_title}]({image_path})\n\n" + (
                        f"**{image_title}描述:** {region.content}" if region.content else ""
                    )
            else:
                # 没有输出目录时使用原始路径
                content = f"![{image_title}]({image_path})\n\n" + (
                    f"**{image_title}描述:** {region.content}" if region.content else ""
                )
    
    # 根据标签类型处理内容
    if label == "text":
        # 文本内容处理
        content = extract_text_from_image(image_path=image_path)
         
    elif label == "formula":
        content = recognize_formula(input_path=image_path)
        # 公式内容处理
        if not content.startswith("$$") and not content.endswith("$$"):
            content = f"$$\n{content}\n$$"
            
    elif label == "table":
        # 表格内容处理
        content = extract_table_from_image(image_path=image_path)
    elif label in ["doc_title", "paragraph_title",
                   "chart_title", "table_title", "figure_title",
                   "abstract"]:
        # 其他类型标签的默认处理
        content = ocr_processor.extract_text(image_path)
    
    region.content = content


def format_pdf_regions(
    page_regions: List[List[RegionImage]],
    image_uploader: Optional[ImageUploader] = None,
    output_dir: Optional[str] = None,
) -> List[str]:
    """
    格式化所有页面的区域为Markdown文本

    参数:
        page_regions: 每页的RegionImage对象列表
        image_uploader: 可选的图片上传器对象
        output_dir: 可选的输出目录，用于保存处理结果

    返回:
        List[str]: 每页的Markdown文本列表
    """
    # 内部函数：将format_region移到这里
    def format_region(
        region: RegionImage, 
        image_upload_obj: Optional[ImageUploader] = None,
        output_dir: Optional[str] = None
    ) -> str:
        """
        将区块处理结果格式化为Markdown

        参数:
            region: RegionImage对象，表示区块处理结果
            image_upload_obj: 图片上传器对象，用于处理图片上传
            output_dir: 可选的输出目录，用于保存处理结果

        返回:
            Markdown格式的文本
        """
        # print(f"处理区域 #{region.region_index+1}，标签: {region.label}")

        # 生成或增强区域内容
        format_region_content(region, image_upload_obj, output_dir)

        if not region.content:
            return ""
        return region.content

    formatted_pages = []
    for page_num, regions in enumerate(page_regions, 1):
        print(f"\n处理第 {page_num} 页的格式化...")
        page_content = []
        for region in regions:
            formatted = format_region(region, image_uploader, output_dir)
            if formatted:
                page_content.append(formatted)
        formatted_pages.append("\n\n".join(page_content))
    return formatted_pages
