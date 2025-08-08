import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import tempfile
import os
from PIL import Image
import io

# Cấu hình trang
st.set_page_config(
    page_title="YOLOv8 Object Detection",
    page_icon="🔍",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("🔍 Ứng Dụng Phát Hiện Đối Tượng với YOLOv8")
st.markdown("---")

# Sidebar cho cài đặt
st.sidebar.header("⚙️ Cài Đặt")
confidence_threshold = st.sidebar.slider(
    "Ngưỡng tin cậy", 
    min_value=0.1, 
    max_value=1.0, 
    value=0.5, 
    step=0.1
)

# Tải model YOLOv8
@st.cache_resource
def load_model():
    """Tải model YOLOv8"""
    try:
        model = YOLO('yolov8n.pt')  # Sử dụng model nhỏ nhất
        return model
    except Exception as e:
        st.error(f"Lỗi khi tải model: {e}")
        return None

# Hàm phát hiện đối tượng
def detect_objects(image, model, conf_threshold):
    """Phát hiện đối tượng trong ảnh"""
    try:
        # Chuyển đổi PIL Image sang numpy array
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
            
        # Thực hiện phát hiện
        results = model(image_np, conf=conf_threshold)
        
        # Lấy kết quả đầu tiên
        result = results[0]
        
        # Vẽ bounding boxes
        annotated_image = result.plot()
        
        return annotated_image, result.boxes.data.cpu().numpy()
    except Exception as e:
        st.error(f"Lỗi khi phát hiện đối tượng: {e}")
        return None, None

# Tải model
with st.spinner("Đang tải model YOLOv8..."):
    model = load_model()

if model is None:
    st.error("Không thể tải model. Vui lòng kiểm tra kết nối internet và thử lại.")
    st.stop()

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Tải Ảnh Lên")
    
    # Upload file
    uploaded_file = st.file_uploader(
        "Chọn ảnh để phát hiện đối tượng",
        type=['png', 'jpg', 'jpeg'],
        help="Hỗ trợ định dạng: PNG, JPG, JPEG"
    )
    
    # Hiển thị thông tin phát hiện ở bên trái
    if uploaded_file is not None:
        # Phát hiện đối tượng
        with st.spinner("Đang phát hiện đối tượng..."):
            image = Image.open(uploaded_file)
            annotated_image, detections = detect_objects(image, model, confidence_threshold)
            
            if annotated_image is not None:
                # Hiển thị thông tin phát hiện
                if detections is not None and len(detections) > 0:
                    st.success(f"Phát hiện được {len(detections)} đối tượng!")
                    
                    # Tạo bảng thông tin
                    detection_info = []
                    for i, detection in enumerate(detections):
                        x1, y1, x2, y2, conf, class_id = detection
                        class_name = model.names[int(class_id)]
                        detection_info.append({
                            "Đối tượng": class_name,
                            "Độ tin cậy": f"{conf:.2f}",
                            "Vị trí": f"({int(x1)}, {int(y1)}) - ({int(x2)}, {int(y2)})"
                        })
                    
                    st.subheader("📋 Chi Tiết Phát Hiện")
                    st.dataframe(detection_info, use_container_width=True)
                else:
                    st.warning("Không phát hiện được đối tượng nào với ngưỡng tin cậy hiện tại.")
    
    else:
        st.info("👆 Vui lòng tải ảnh lên để bắt đầu phát hiện đối tượng")

with col2:
    st.header("📊 Kết Quả Phát Hiện")
    
    if uploaded_file is not None:
        # Xử lý file upload
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh gốc", use_container_width=True)
        
        # Phát hiện đối tượng
        with st.spinner("Đang phát hiện đối tượng..."):
            annotated_image, detections = detect_objects(image, model, confidence_threshold)
            
            if annotated_image is not None:
                st.image(annotated_image, caption="Ảnh sau phát hiện", use_container_width=True)
    
    else:
        st.info("👆 Vui lòng tải ảnh lên để bắt đầu phát hiện đối tượng")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🔍 Ứng dụng phát hiện đối tượng với YOLOv8 | Được xây dựng với Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
) 