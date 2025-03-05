"""
文件: test_output.py
描述: 测试文档处理输出和图片引用
作者: 筱可
微信公众号: 筱可AI研习社
日期: 2025-3-6
"""

import os
import sys
from visualize_boxes import DocumentElementProcessor

def test_document_processing():
    """测试文档处理功能，特别关注输出文件和图片路径引用"""
    
    # 文件路径
    layout_json_path = "res.json"
    
    # 设置明确的输出路径
    output_dir = "output"
    images_dir = "images"
    markdown_path = "test.md"
    visualization_path = "visualization_test.png"  # 这是一个独立的输出路径
    
    print(f"开始测试文档处理...")
    print(f"- 输入JSON: {layout_json_path}")
    print(f"- 输出目录: {output_dir}")
    print(f"- 图片目录: {os.path.join(output_dir, images_dir)}")
    print(f"- Markdown文件: {os.path.join(output_dir, markdown_path)}")
    print(f"- 可视化结果: {visualization_path}")  # 直接使用visualization_path
    
    # 删除可能的旧输出以确保测试的干净性
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        if os.path.exists(output_dir):
            try:
                os.rmdir(output_dir)
            except:
                pass
    
    # 删除可能存在的旧可视化文件
    if os.path.exists(visualization_path):
        os.remove(visualization_path)
    
    # 创建处理器并执行流程
    processor = DocumentElementProcessor(
        output_dir=output_dir,
        images_dir=images_dir
    )
    
    processor.process_document(
        layout_json_path,
        visualization_path,
        markdown_path
    )
    
    # 检查可视化输出
    if os.path.exists(visualization_path):
        print(f"\n✓ 可视化文件已成功创建: {visualization_path}")
    else:
        print(f"\n✗ 可视化文件未创建: {visualization_path}")
    
    # 检查输出
    md_file_path = os.path.join(output_dir, markdown_path)
    if os.path.exists(md_file_path):
        print(f"\n✓ Markdown文件已成功创建: {md_file_path}")
        
        # 检查Markdown内容中的图片引用格式
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找图片引用
        import re
        image_refs = re.findall(r'!\[(.*?)\]\((.*?)\)', content)
        if image_refs:
            print(f"✓ 在Markdown中找到 {len(image_refs)} 个图片引用:")
            for alt_text, img_path in image_refs:
                print(f"  - [{alt_text}]: {img_path}")
                
                # 检查图片文件是否存在
                full_img_path = os.path.join(output_dir, img_path)
                if os.path.exists(full_img_path):
                    print(f"    ✓ 图片文件存在: {full_img_path}")
                else:
                    print(f"    ✗ 图片文件不存在: {full_img_path}")
        else:
            print(f"✗ 在Markdown中未找到图片引用")
    else:
        print(f"\n✗ Markdown文件未创建: {md_file_path}")

if __name__ == "__main__":
    test_document_processing()
