from x_pdf2md.remote_image.image_uploader import ImageUploader
from x_pdf2md.remote_image.remote_image_config import BASE_URL


# 创建默认的上传器实例
default_uploader = ImageUploader(BASE_URL)

# 导出常用的接口
__all__ = ['default_uploader']
