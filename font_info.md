# 中文字体设置指南

## 字体文件说明

本程序使用中文字体 SimHei (黑体) 来显示中文文本。为了确保中文显示正确，程序会在以下位置查找字体文件：

1. 当前目录
2. Windows 标准字体目录 (C:/Windows/Fonts/)
3. Linux 标准字体目录 (/usr/share/fonts/)
4. macOS 标准字体目录 (/System/Library/Fonts/)
5. 程序安装目录

## 如何添加中文字体

如果在上述位置未找到中文字体，您可以：

### Windows

1. 下载 SimHei.ttf 字体文件
2. 将其放置在程序同一目录下即可

### Linux

1. 安装中文字体包：

   ```bash
   sudo apt-get install fonts-arphic-uming  # Debian/Ubuntu
   ```

   或

   ```bash
   sudo yum install wqy-zenhei-fonts  # CentOS/Fedora
   ```

### macOS

1. macOS 通常已预装中文字体，无需额外安装

## 自定义字体路径

您也可以修改程序代码的 `main()` 函数，通过参数指定自定义字体路径：
