import json


with open("S_output/res.json", "r", encoding="utf-8") as f:
    s_data = json.load(f)
    
with open("L_output/res.json", "r", encoding="utf-8") as f:
    l_data = json.load(f)

with open("UniMERNet_output/res.json", "r", encoding="utf-8") as f:
    u_data = json.load(f)

# 写入到md文件
with open("output/formula_recognition.md", "w", encoding="utf-8") as f:
    f.write("# 公式识别结果对比\n\n")
    # 小模型识别结果
    f.write("## 小模型识别结果\n\n")
    f.write(f"输入图像: {s_data['input_path']}\n\n")
    f.write(f"识别结果: $${s_data['rec_formula']}$$\n\n")
    # 大模型识别结果
    f.write("## 大模型识别结果\n\n")
    f.write(f"输入图像: {l_data['input_path']}\n\n")
    f.write(f"识别结果:$$ {l_data['rec_formula']}$$\n\n")
    # 加入UniMERNet_output的识别结果
    f.write("## UniMERNet模型识别结果\n\n")
    f.write(f"输入图像: {u_data['input_path']}\n\n")
    f.write(f"识别结果:$$ {u_data['rec_formula']}$$\n\n")