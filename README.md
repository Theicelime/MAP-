# 坐标系转换工具

一个基于Streamlit的在线坐标系转换工具，支持WGS84、GCJ02和BD09坐标系之间的相互转换。

## 功能特点

- 🌍 支持WGS84、GCJ02、BD09坐标系互转
- 📊 支持CSV和Excel文件格式
- 🔄 批量处理大量坐标点
- 📥 一键下载转换结果
- 🎯 用户友好的Web界面

## 支持的转换

- WGS84 ↔ GCJ02
- WGS84 ↔ BD09  
- GCJ02 ↔ BD09

## 使用方法

1. 上传包含坐标数据的CSV或Excel文件
2. 选择经度和纬度字段
3. 选择源坐标系和目标坐标系
4. 设置输出字段名
5. 点击"开始转换"按钮
6. 下载转换后的文件

## 部署

此应用已部署在Streamlit Cloud，可直接访问使用。

## 本地运行

如需本地运行：

```bash
pip install -r requirements.txt
streamlit run app.py
