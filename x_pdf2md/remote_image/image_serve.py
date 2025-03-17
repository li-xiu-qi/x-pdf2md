import os
import json
from fastapi import FastAPI, UploadFile, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uuid
from typing import List
from remote_image_config import UPLOAD_DIR, BASE_URL, HOST, PORT, IMAGE_NAMES_FILE

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app = FastAPI()

# 挂载静态文件目录
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")
app.mount("static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}

# 加载图片名称映射
image_names = {}
if os.path.exists(IMAGE_NAMES_FILE):
    with open(IMAGE_NAMES_FILE, 'r', encoding='utf-8') as f:
        image_names = json.load(f)

@app.post("/image_upload")
async def upload_image(file: UploadFile):
    """
    图片上传接口
    """
    try:
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 确保上传目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 保存原始文件名映射
        image_names[unique_filename] = original_filename
        with open(IMAGE_NAMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(image_names, f, ensure_ascii=False, indent=2)
        
        # 返回相对路径，不包含BASE_URL
        return {"url": f"images/{unique_filename}", "originalName": original_filename}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload failed: {str(e)}"}
        )

@app.get("/api/images")
async def list_images(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
    all_images = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
    all_images.sort(key=lambda x: os.path.getctime(os.path.join(UPLOAD_DIR, x)), reverse=True)
    
    # 计算分页
    total = len(all_images)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = min(start + page_size, total)
    
    # 添加原始文件名
    image_list = []
    for img in all_images[start:end]:
        image_list.append({
            "filename": img,
            "originalName": image_names.get(img, img)
        })
    
    return {
        "images": image_list,
        "totalPages": total_pages,
        "currentPage": page,
        "total": total
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
