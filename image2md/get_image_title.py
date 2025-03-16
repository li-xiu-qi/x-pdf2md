from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

SYSTEM_PROMPT = """你是一个专业图像标题生成助手。
任务：根据提供的图像描述生成一个简短、准确且具有描述性的标题。

输出要求：
- 标题应简洁（通常控制在5-20个字之间）
- 突出图像的核心主题或最显著特征
- 使用具体而非抽象的词语
- 不要包含"这是"、"这张图片"等冗余词语
- 学术论文或技术图像应保留专业术语的准确性
- 直接输出标题文本，无需额外说明或引号

示例：
描述：茂密森林中，阳光透过树叶洒落在地面，形成斑驳光影。远处小溪流淌，水面反射着周围绿色植被。
标题：晨光森林溪流

描述：年轻女性在实验室使用显微镜观察样本。她穿白色实验服，戴护目镜，专注调整显微镜。旁边放着试管和实验笔记。
标题：科研人员显微观察

描述：学术论文封面，白色背景。标题"ISAM-MTL: Cross-subject multi-task learning model with identifiable spikes and associative memory networks"位于顶部，黑色字体。下方是作者名字"Junyan Li", "Bin Hu", "Zhi-Hong Guan"。摘要部分介绍EEG信号跨主体变化性和ISAM-MTL模型。页面右下角显示DOI和版权信息。
标题：ISAM-MTL 论文封面首页
"""


USER_PROMPT_TEMPLATE = """基于以下图像描述，提供一个简洁、专业的标题：
----
描述：{description}
----
直接输出标题（5-15字）："""


def get_image_title(image_description, api_key=None):
    """
    使用硅基流动的deepseek v3 为多模态提取的图片描述生成图片的标题。

    参数:
        image_description (str): 图像的描述文本
        api_key (str): 您的OpenAI API密钥

    返回:
        str: 为图像生成的标题
    """

    if not api_key:
        api_key = os.getenv("API_KEY")
    # 使用Silicon Flow基础URL初始化客户端
    client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.com/v1")

    # 发送API请求
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(description=image_description),
            },
        ],
    )

    # 提取并返回标题
    title = response.choices[0].message.content.strip()
    return title


if __name__ == "__main__":

    image_description = """
    这张图片显示了一篇学术论文的封面。
    封面的背景是白色的，标题
    "ISAM-MTL: Cross-subject multi-task learning model with identifiable spikes and associative memory networks"
    位于页面的顶部，使用了黑色的字体。
    标题下方是作者的名字，分别是"Junyan Li", "Bin Hu", 和"Zhi-Hong Guan"。再往下是摘要部分，使用了较小的字体。
    摘要的标题是"Abstract"，内容是关于EEG（脑电图）信号的跨主体变化性，
    以及一种新的模型"ISAM-MTL"（Identifiable Spikes and Associative Memory Multi-Task Learning）的介绍。
    摘要的最后是"Introduction"部分的开头，介绍了脑机接 口（BCI）系统和EEG信号的相关背景。
    页面的右下角显示了论文的引用信息，包括DOI（数字对象标识符）和版权信息。
    整体构图简洁明了，信息层次分明。
    """
    title = get_image_title(image_description)
    print(title)
