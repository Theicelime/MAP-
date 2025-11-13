import streamlit as st
import pandas as pd
import math
import io
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="坐标系转换工具",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 坐标系转换类
class CoordinateConverter:
    """坐标系转换工具类"""
    
    PI = math.pi
    AXIS = 6378245.0
    OFFSET = 0.00669342162296594323
    X_PI = PI * 3000.0 / 180.0
    
    @staticmethod
    def _transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * CoordinateConverter.PI) + 
               20.0 * math.sin(2.0 * x * CoordinateConverter.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * CoordinateConverter.PI) + 
               40.0 * math.sin(y / 3.0 * CoordinateConverter.PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * CoordinateConverter.PI) + 
               320 * math.sin(y * CoordinateConverter.PI / 30.0)) * 2.0 / 3.0
        return ret

    @staticmethod
    def _transform_lng(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * CoordinateConverter.PI) + 
               20.0 * math.sin(2.0 * x * CoordinateConverter.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * CoordinateConverter.PI) + 
               40.0 * math.sin(x / 3.0 * CoordinateConverter.PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * CoordinateConverter.PI) + 
               300.0 * math.sin(x / 30.0 * CoordinateConverter.PI)) * 2.0 / 3.0
        return ret

    @staticmethod
    def _out_of_china(lng, lat):
        return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)

    @staticmethod
    def wgs84_to_gcj02(lng, lat):
        if CoordinateConverter._out_of_china(lng, lat):
            return lng, lat
        dlat = CoordinateConverter._transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordinateConverter._transform_lng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * CoordinateConverter.PI
        magic = math.sin(radlat)
        magic = 1 - CoordinateConverter.OFFSET * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((CoordinateConverter.AXIS * (1 - CoordinateConverter.OFFSET)) / 
                                (magic * sqrtmagic) * CoordinateConverter.PI)
        dlng = (dlng * 180.0) / (CoordinateConverter.AXIS / sqrtmagic * 
                                math.cos(radlat) * CoordinateConverter.PI)
        mglat = lat + dlat
        mglng = lng + dlng
        return mglng, mglat

    @staticmethod
    def gcj02_to_wgs84(lng, lat):
        if CoordinateConverter._out_of_china(lng, lat):
            return lng, lat
        dlat = CoordinateConverter._transform_lat(lng - 105.0, lat - 35.0)
        dlng = CoordinateConverter._transform_lng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * CoordinateConverter.PI
        magic = math.sin(radlat)
        magic = 1 - CoordinateConverter.OFFSET * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((CoordinateConverter.AXIS * (1 - CoordinateConverter.OFFSET)) / 
                                (magic * sqrtmagic) * CoordinateConverter.PI)
        dlng = (dlng * 180.0) / (CoordinateConverter.AXIS / sqrtmagic * 
                                math.cos(radlat) * CoordinateConverter.PI)
        wgslat = lat - dlat
        wgslng = lng - dlng
        return wgslng, wgslat

    @staticmethod
    def gcj02_to_bd09(lng, lat):
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * CoordinateConverter.X_PI)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * CoordinateConverter.X_PI)
        bdlng = z * math.cos(theta) + 0.0065
        bdlat = z * math.sin(theta) + 0.006
        return bdlng, bdlat

    @staticmethod
    def bd09_to_gcj02(lng, lat):
        x = lng - 0.0065
        y = lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * CoordinateConverter.X_PI)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * CoordinateConverter.X_PI)
        gclng = z * math.cos(theta)
        gclat = z * math.sin(theta)
        return gclng, gclat

    @staticmethod
    def wgs84_to_bd09(lng, lat):
        lng, lat = CoordinateConverter.wgs84_to_gcj02(lng, lat)
        return CoordinateConverter.gcj02_to_bd09(lng, lat)

    @staticmethod
    def bd09_to_wgs84(lng, lat):
        lng, lat = CoordinateConverter.bd09_to_gcj02(lng, lat)
        return CoordinateConverter.gcj02_to_wgs84(lng, lat)

# 页面标题和介绍
st.title("🌍 坐标系转换工具")
st.markdown("""
这个工具可以帮助您在 **WGS84**、**GCJ02** 和 **BD09** 坐标系之间进行转换。
- **WGS84**: GPS全球定位系统使用的坐标系
- **GCJ02**: 高德地图、腾讯地图等使用的坐标系
- **BD09**: 百度地图使用的坐标系
""")

# 侧边栏
with st.sidebar:
    st.header("使用说明")
    st.markdown("""
    1. 上传包含坐标数据的CSV或Excel文件
    2. 选择经度和纬度字段
    3. 选择源坐标系和目标坐标系
    4. 点击"开始转换"按钮
    5. 下载转换后的文件
    
    **注意**: 请确保坐标数据格式正确
    - 经度范围: -180° ~ 180°
    - 纬度范围: -90° ~ 90°
    """)
    
    st.header("关于")
    st.markdown("""
    此工具基于公开的坐标转换算法开发，
    适用于地理信息数据处理和地图应用开发。
    """)

# 文件上传区域
st.header("1. 上传数据文件")
uploaded_file = st.file_uploader(
    "选择CSV或Excel文件", 
    type=['csv', 'xlsx', 'xls'],
    help="支持CSV和Excel格式文件"
)

# 初始化会话状态
if 'df' not in st.session_state:
    st.session_state.df = None
if 'converted' not in st.session_state:
    st.session_state.converted = False

# 处理上传的文件
if uploaded_file is not None:
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state.df = df
        
        # 显示数据预览
        st.subheader("数据预览")
        st.write(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
        st.dataframe(df.head(), use_container_width=True)
        
        # 显示列名
        st.subheader("2. 选择坐标字段")
        col1, col2 = st.columns(2)
        
        with col1:
            x_field = st.selectbox(
                "选择经度字段",
                options=df.columns.tolist(),
                index=0,
                help="选择包含经度数据的列"
            )
        
        with col2:
            y_field = st.selectbox(
                "选择纬度字段",
                options=df.columns.tolist(),
                index=min(1, len(df.columns)-1),
                help="选择包含纬度数据的列"
            )
        
        # 坐标系选择
        st.subheader("3. 选择坐标系")
        col1, col2 = st.columns(2)
        
        with col1:
            from_crs = st.selectbox(
                "源坐标系",
                options=['WGS84', 'GCJ02', 'BD09'],
                index=0,
                help="数据当前使用的坐标系"
            )
        
        with col2:
            to_crs = st.selectbox(
                "目标坐标系",
                options=['WGS84', 'GCJ02', 'BD09'],
                index=1,
                help="想要转换到的坐标系"
            )
        
        # 新字段名设置
        st.subheader("4. 输出设置")
        col1, col2 = st.columns(2)
        
        with col1:
            new_x_field = st.text_input(
                "新经度字段名",
                value=f"{to_crs.lower()}_lng",
                help="转换后经度数据的字段名"
            )
        
        with col2:
            new_y_field = st.text_input(
                "新纬度字段名",
                value=f"{to_crs.lower()}_lat",
                help="转换后纬度数据的字段名"
            )
        
        # 转换按钮
        if st.button("🚀 开始转换", type="primary", use_container_width=True):
            with st.spinner("正在转换坐标..."):
                # 定义转换函数映射
                conversion_map = {
                    ('WGS84', 'GCJ02'): CoordinateConverter.wgs84_to_gcj02,
                    ('WGS84', 'BD09'): CoordinateConverter.wgs84_to_bd09,
                    ('GCJ02', 'WGS84'): CoordinateConverter.gcj02_to_wgs84,
                    ('GCJ02', 'BD09'): CoordinateConverter.gcj02_to_bd09,
                    ('BD09', 'WGS84'): CoordinateConverter.bd09_to_wgs84,
                    ('BD09', 'GCJ02'): CoordinateConverter.bd09_to_gcj02,
                }
                
                # 相同坐标系不需要转换
                if from_crs == to_crs:
                    conversion_func = lambda lng, lat: (lng, lat)
                else:
                    conversion_func = conversion_map.get((from_crs, to_crs))
                
                # 执行坐标转换
                converted_coords = []
                success_count = 0
                error_count = 0
                error_details = []
                
                for idx, row in df.iterrows():
                    try:
                        lng = float(row[x_field])
                        lat = float(row[y_field])
                        
                        # 验证坐标范围
                        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
                            raise ValueError(f"坐标超出有效范围: ({lng}, {lat})")
                        
                        if from_crs != to_crs:
                            new_lng, new_lat = conversion_func(lng, lat)
                        else:
                            new_lng, new_lat = lng, lat
                            
                        converted_coords.append((new_lng, new_lat))
                        success_count += 1
                        
                    except Exception as e:
                        error_details.append(f"第 {idx+1} 行: {str(e)}")
                        converted_coords.append((None, None))
                        error_count += 1
                
                # 添加转换后的坐标到数据框
                result_df = df.copy()
                result_df[new_x_field] = [coord[0] for coord in converted_coords]
                result_df[new_y_field] = [coord[1] for coord in converted_coords]
                
                # 保存结果到会话状态
                st.session_state.result_df = result_df
                st.session_state.converted = True
                
                # 显示转换结果
                st.success(f"转换完成! 成功: {success_count} 条, 失败: {error_count} 条")
                
                # 显示错误详情（如果有）
                if error_count > 0:
                    with st.expander("查看错误详情"):
                        for error in error_details:
                            st.error(error)
                
                # 显示转换后的数据预览
                st.subheader("转换结果预览")
                st.dataframe(result_df.head(), use_container_width=True)
                
                # 提供下载
                st.subheader("5. 下载转换结果")
                
                # 获取文件格式
                file_ext = uploaded_file.name.split('.')[-1]
                
                # 创建下载按钮
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV下载
                    csv_data = result_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 下载CSV格式",
                        data=csv_data,
                        file_name=f"converted_coordinates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Excel下载
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        result_df.to_excel(writer, index=False, sheet_name='Coordinates')
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="📥 下载Excel格式",
                        data=excel_data,
                        file_name=f"converted_coordinates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
    
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")

else:
    # 显示示例数据格式
    st.info("👆 请上传数据文件开始转换")
    
    # 显示示例数据
    st.subheader("数据格式示例")
    example_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['点A', '点B', '点C', '点D', '点E'],
        'longitude': [116.3974, 121.4737, 113.2644, 114.0579, 108.9480],
        'latitude': [39.9093, 31.2304, 23.1291, 22.5431, 34.2617]
    })
    st.dataframe(example_data, use_container_width=True)
    st.caption("示例数据格式: 包含经度(longitude)和纬度(latitude)字段")

# 页脚
st.markdown("---")
st.caption("坐标系转换工具 © 2023 | 基于Streamlit构建")
