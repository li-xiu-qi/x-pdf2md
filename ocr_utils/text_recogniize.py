import json
import os
from paddlex import create_model


def recognize_text(
    input_image: str,
    output_path: str = "./output/res.json",
    model="PP-OCRv4_mobile_rec",
) -> list:
    """
    识别图片中的文本
    Args:
        input_image: 输入图片路径
        output_dir: 输出目录路径
    Returns:
        识别结果列表
    """
    output_dir = os.path.dirname(output_path)
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 创建模型
    model = create_model(model_name=model)

    # 预测
    output = model.predict(input=input_image, batch_size=1)

    for res in output:
        res.save_to_json(save_path=output_path)

    with open(output_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    return result


# 使用示例:
# results = recognize_text("text_area_4_score_0.9858.png")

# OCR 文本识别结果

# 以下是 OCR 文本识别的 JSON 结果数据：

# ```json
# {
#     "input_path": "general_ocr_rec_001.png",  // 输入图像文件路径
#     "page_index": null,                        // 页码索引（多页文档时使用）
#     "rec_text": "绿洲仕格维花园公寓",           // 识别出的文本内容
#     "rec_score": 0.9875162839889526           // 识别结果的置信度分数（0-1之间）
# }
# ```

# ## 字段说明

# - **input_path**: 输入的源图像文件名
# - **page_index**: 在多页文档中的页码索引，null 表示单页文档或默认页
# - **rec_text**: OCR 识别出的文本内容
# - **rec_score**: 识别结果的置信度，越接近 1 表示识别结果越可信
