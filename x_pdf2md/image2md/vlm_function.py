from .image2text import ImageTextExtractor, extract_markdown_content
import os

# 定义提示词
ocr_prompt = """
使用OCR的模式提取图像中的文本内容，并转换为Markdown格式。
注意：不要输出图片以外的内容。
其中表格输出为Markdown格式，或者html格式，公式输出为带有$或者$$风格的LaTeX格式。
"""

description_prompt = """
# PDF图像内容描述提示

## 任务

使用视觉语言模型生成从PDF提取的图像内容的简洁描述。

## 背景

- 图像来源于PDF文档
- 需要清晰理解图像的主要内容和用途
- 避免冗余描述，保持精简

## 输入

- 从PDF提取的图像

## 输出

请简洁描述图像的以下关键方面：

1. 图像类型（图表、示意图、照片等）
2. 主要内容/主题
3. 包含的关键信息点
4. 文本或标签（如有）
5. 图像的可能用途

示例格式：
"这是一张[图像类型]，展示了[主要内容]。包含[关键信息]。[其他相关细节]。"
"""

extract_table_prompt = """
提取图片当中的表格，并输出为支持markdown格式的html语法。
注意：不要输出图片以外的内容。
"""


def _process_image_with_model(
    image_path: str,
    model: str,
    prompt_path: str = None,
    prompt_text: str = None,
    api_key: str = None,
    detail: str = "low",
    post_process_func = None
) -> str:
    """处理图像并返回模型输出的基础函数"""
    if api_key is None:
        api_key = os.getenv("API_KEY")
    
    extractor = ImageTextExtractor(
        api_key=api_key,
        prompt_path=prompt_path,
        prompt=prompt_text
    )

    try:
        result = extractor.extract_image_text(
            local_image_path=image_path, model=model, detail=detail
        )
        
        if not result.strip():
            return "No content extracted from the image"
        
        if post_process_func:
            return post_process_func(result)
        return extract_markdown_content(result)
    except Exception as e:
        return f"Error processing image: {str(e)}"


def extract_text_from_image(
    image_path: str,
    model: str = None,
    ocr_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """从图像中提取文本内容并转换为Markdown格式"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=ocr_prompt_path,
        prompt_text=ocr_prompt if not ocr_prompt_path else None,
        api_key=api_key,
        detail="low"
    )


def describe_image(
    image_path: str,
    model: str = None,
    description_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """描述图像内容并生成文本描述"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=description_prompt_path,
        prompt_text=description_prompt if not description_prompt_path else None,
        api_key=api_key,
        detail="low"
    )


def process_table_content(result):
    """处理表格内容"""
    table_content = extract_markdown_content(result)
    
    if not (table_content.startswith('|') and '|---' in table_content):
        if '<table' in table_content.lower() and '</table>' in table_content.lower():
            return table_content
        else:
            return f"```\n{table_content}\n```"
    return table_content


def extract_table_from_image(
    image_path: str,
    model: str = None,
    extract_table_prompt_path: str = None,
    api_key: str = None,
) -> str:
    """从图像中提取表格内容并转换为Markdown或HTML格式"""
    return _process_image_with_model(
        image_path=image_path,
        model=model,
        prompt_path=extract_table_prompt_path,
        prompt_text=extract_table_prompt if not extract_table_prompt_path else None,
        api_key=api_key,
        detail="high",
        post_process_func=process_table_content
    )


# 测试代码
if __name__ == "__main__":
    import sys
    from pathlib import Path

    current_dir = Path(__file__).parent
    test_image_path = current_dir / "car.png"

    if not test_image_path.exists():
        print(f"测试图像文件不存在: {test_image_path}")
        sys.exit(1)

    print(f"正在处理图像: {test_image_path}")

    ocr_prompt_path = current_dir / "prompts/ocr_prompt.md"
    description_prompt_path = current_dir / "prompts/description_prompt.md"
    table_prompt_path = current_dir / "prompts/extract_table_prompt.md"

    # 测试文本提取
    print("\n" + "=" * 50)
    print("1. 提取的文本内容:")
    print("=" * 50)
    extracted_text = extract_text_from_image(
        str(test_image_path),
        ocr_prompt_path=str(ocr_prompt_path) if ocr_prompt_path.exists() else None,
    )
    print(extracted_text)

    # 测试图像描述
    print("\n" + "=" * 50)
    print("2. 图像描述:")
    print("=" * 50)
    image_description = describe_image(
        str(test_image_path),
        description_prompt_path=(
            str(description_prompt_path) if description_prompt_path.exists() else None
        ),
    )
    print(image_description)

    # 测试表格提取
    print("\n" + "=" * 50)
    print("3. 提取的表格内容:")
    print("=" * 50)
    table_content = extract_table_from_image(
        str(test_image_path),
        extract_table_prompt_path=(
            str(table_prompt_path) if table_prompt_path.exists() else None
        ),
    )
    print(table_content)
    print("=" * 50)
