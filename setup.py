from setuptools import setup, find_packages

setup(
    name="x-pdf2md",
    version="0.1.0",
    packages=find_packages(include=['x_pdf2md', 'x_pdf2md.*']),  # 明确包含x_pdf2md包及其子包
    install_requires=[
        "tqdm>=4.45.0",
        "pdf2image>=1.14.0",
        "Pillow>=8.0.0",
        "numpy>=1.18.0",
        "opencv-python>=4.5.0",
        "pytesseract>=0.3.0",
        "requests>=2.25.0",
        "fastapi",
        "pymupdf", 
        "python-dotenv",
        "uvicorn",
        # PaddlePaddle和PaddleX需要特殊安装方式，不在这里列出
    ],
    author="li-xiu-qi",
    author_email="lixiuqixiaoke@qq.com",
    description="将PDF文档转换为Markdown的工具",
    keywords="pdf, markdown, conversion",
    url="",
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
    entry_points={
        'console_scripts': [
            'x-pdf2md=x_pdf2md.main:main',  # 更新入口点指向新的main.py
        ],
    },
    python_requires='>=3.7',
)
