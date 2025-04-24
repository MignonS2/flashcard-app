import streamlit as st
import random
import json
import os
import base64
from PIL import Image
import io
import time
import uuid
import datetime

# 데이터 파일 경로
DATA_FILE = "flashcards.json"
IMAGE_FOLDER = "images"
TEMP_IMAGE_FOLDER = "temp_images"

# 이미지 폴더 생성
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# 임시 이미지 폴더 생성
if not os.path.exists(TEMP_IMAGE_FOLDER):
    os.makedirs(TEMP_IMAGE_FOLDER)

# 스트림릿 페이지 스타일 설정
def set_page_style():
    st.markdown("""
    <style>
    /* 전체 앱 스타일 */
    .stApp {
        background-color: #f7f9fc;
        font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3, h4 {
        font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
        color: #1a365d;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h1 {
        font-size: 2.2rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #4263EB;
        padding-bottom: 0.5rem;
        color: #1a365d;
    }
    
    h2 {
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        color: #2a4a7f;
    }
    
    h3 {
        font-size: 1.4rem;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        color: #2c5282;
    }
    
    /* 사이드바 스타일 */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #e8f0fe;
        border-right: 1px solid #d0def7;
    }
    
    /* 카드 스타일 */
    .card {
        border-radius: 12px;
        border: 1px solid #d0def7;
        padding: 20px;
        background-color: white;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(66, 99, 235, 0.1);
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #4263EB;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(66, 99, 235, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #3b56d7;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(66, 99, 235, 0.4);
    }
    
    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 4px rgba(66, 99, 235, 0.3);
    }
    
    /* Secondary 버튼 */
    .stButton[data-testid*="secondary"]>button {
        background-color: #e8f0fe;
        color: #4263EB;
        border: 1px solid #4263EB;
    }
    
    .stButton[data-testid*="secondary"]>button:hover {
        background-color: #d0def7;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #d0def7;
        padding: 10px;
        transition: all 0.2s ease;
        background-color: #fafcff;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4263EB;
        box-shadow: 0 0 0 2px rgba(66, 99, 235, 0.2);
        background-color: white;
    }
    
    /* 파일 업로더 스타일 */
    .stFileUploader {
        border: 2px dashed #4263EB;
        border-radius: 8px;
        padding: 15px;
        background-color: rgba(66, 99, 235, 0.05);
        transition: all 0.2s ease;
    }
    
    .stFileUploader:hover {
        background-color: rgba(66, 99, 235, 0.1);
    }
    
    /* 셀렉트박스 스타일 */
    .stSelectbox {
        border-radius: 8px;
    }
    
    .stSelectbox>div>div>div {
        background-color: #fafcff;
        border-radius: 8px;
        border: 1px solid #d0def7;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    
    .stSelectbox>div>div>div:hover {
        border-color: #4263EB;
    }
    
    /* 확장 패널 스타일 */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #1a365d;
        background-color: #e8f0fe;
        border-radius: 8px;
        border: none !important;
        padding: 12px 15px;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #d0def7;
    }
    
    .streamlit-expanderContent {
        border: 1px solid #d0def7;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 20px;
        background-color: #fafcff;
    }
    
    /* 이미지 미리보기 컨테이너 */
    .preview-container {
        text-align: center;
        margin: 15px auto;
        padding: 15px;
        border-radius: 8px;
        background-color: #e8f0fe;
        max-height: 600px;
        overflow: auto;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 이미지 스타일 및 마우스 오버 효과 */
    .img-container {
        position: relative;
        display: inline-block;
        margin: 12px;
        cursor: pointer;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .img-container img {
        transition: all 0.4s ease;
        max-width: 100%;
        display: block;
    }
    
    .img-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(26, 54, 93, 0.7);
        color: white;
        opacity: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        transition: all 0.3s ease;
    }
    
    .img-container:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transform: translateY(-5px);
    }
    
    .img-container:hover .img-overlay {
        opacity: 1;
    }
    
    .img-container:hover img {
        transform: scale(1.05);
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 3px;
        background-color: #e8f0fe;
        padding: 8px 8px 0;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #fafcff;
        border-radius: 8px 8px 0 0;
        color: #4263EB;
        padding: 10px 20px;
        transition: all 0.2s ease;
        border: 1px solid #d0def7;
        border-bottom: none;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4263EB;
        color: white;
        border-color: #4263EB;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border: 1px solid #d0def7;
        border-radius: 0 0 8px 8px;
        padding: 24px;
    }
    
    /* 토픽 선택 스타일 */
    .topic-selector {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 24px;
        border: 1px solid #d0def7;
    }
    
    /* 정의/개념 카드 스타일 */
    .concept-card {
        background-color: white;
        border-left: 5px solid #4263EB;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .concept-card:hover {
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }
    
    /* 메시지 알림 스타일 */
    .stAlert {
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }
    
    .stAlert>div {
        padding: 12px 16px;
        border-radius: 8px;
    }
    
    /* 성공 메시지 */
    .element-container:has(.stAlert>div[data-baseweb="notification"][kind="positive"]) {
        animation: fadeInDown 0.5s ease-out;
    }
    
    /* 에러 메시지 */
    .element-container:has(.stAlert>div[data-baseweb="notification"][kind="negative"]) {
        animation: shake 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
    }
    
    /* 정보 메시지 */
    .element-container:has(.stAlert>div[data-baseweb="notification"][kind="info"]) {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* 애니메이션 키프레임 */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes shake {
        10%, 90% { transform: translateX(-1px); }
        20%, 80% { transform: translateX(2px); }
        30%, 50%, 70% { transform: translateX(-4px); }
        40%, 60% { transform: translateX(4px); }
    }
    
    /* 학습 요소 강조 스타일 */
    .domain-label {
        font-weight: 600;
        color: #1a365d;
        background-color: #e8f0fe;
        padding: 5px 10px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 8px;
        border-left: 3px solid #4263EB;
    }
    
    .topic-label {
        font-weight: 600;
        color: #2a4a7f;
        background-color: #edf2ff;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 8px;
        border-left: 3px solid #5a7eeb;
    }
    
    .term-label {
        font-weight: 700;
        color: #2c5282;
        padding: 2px 0;
        border-bottom: 2px solid #4263EB;
        display: inline-block;
        margin-right: 8px;
    }
    
    .keyword-label {
        font-weight: 600;
        color: #3182ce;
        background-color: #ebf8ff;
        padding: 3px 8px;
        border-radius: 20px;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
        border: 1px solid #bee3f8;
    }
    
    .rhyming-label {
        font-weight: 600;
        color: #805ad5;
        background-color: #f5f0ff;
        padding: 3px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 8px;
        border-left: 2px solid #805ad5;
        font-family: 'Consolas', monospace;
    }
    
    /* 중요 내용 강조 */
    strong, b {
        color: #2c5282;
        background-color: #f0f7ff;
        padding: 0 4px;
        border-radius: 3px;
    }
    
    /* 링크 스타일 */
    a {
        color: #4263EB;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    a:hover {
        color: #3b56d7;
        text-decoration: underline;
    }
    </style>
    
    <script>
    // 도메인, 토픽, 정의/개념 등의 레이블에 CSS 클래스 추가
    document.addEventListener('DOMContentLoaded', function() {
        // 도메인 레이블에 클래스 추가
        document.querySelectorAll('span:contains("도메인:")').forEach(el => {
            el.classList.add('domain-label');
        });
        
        // 토픽 레이블에 클래스 추가
        document.querySelectorAll('span:contains("토픽:")').forEach(el => {
            el.classList.add('topic-label');
        });
        
        // 정의/개념 레이블에 클래스 추가
        document.querySelectorAll('span:contains("정의/개념:")').forEach(el => {
            el.classList.add('term-label');
        });
        
        // 핵심키워드 레이블에 클래스 추가
        document.querySelectorAll('span:contains("핵심키워드:")').forEach(el => {
            el.classList.add('keyword-label');
        });
        
        // 두음 레이블에 클래스 추가
        document.querySelectorAll('span:contains("두음:")').forEach(el => {
            el.classList.add('rhyming-label');
        });
    });
    </script>
    """, unsafe_allow_html=True)

# 클립보드 이미지 컴포넌트용 JavaScript 코드
def clipboard_component():
    clipboard_callback = """
    <script>
    let clipboard_image = null;
    
    document.addEventListener('paste', function(e) {
        const clipboardData = e.clipboardData;
        if (!clipboardData) return;
        
        const items = clipboardData.items;
        
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    const base64data = event.target.result;
                    clipboard_image = base64data;
                    
                    // 이미지 미리보기 표시
                    document.getElementById('preview-image').src = base64data;
                    document.getElementById('preview-image').style.display = 'block';
                    document.getElementById('preview-container').style.display = 'block';
                    
                    // Streamlit에 데이터 전송
                    Streamlit.setComponentValue({
                        image: base64data,
                        timestamp: new Date().toISOString()
                    });
                };
                
                reader.readAsDataURL(blob);
                break;
            }
        }
    });
    
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const base64data = event.target.result;
                clipboard_image = base64data;
                
                // 이미지 미리보기 표시
                document.getElementById('preview-image').src = base64data;
                document.getElementById('preview-image').style.display = 'block';
                document.getElementById('preview-container').style.display = 'block';
                
                // Streamlit에 데이터 전송
                Streamlit.setComponentValue({
                    image: base64data,
                    timestamp: new Date().toISOString()
                });
            };
            reader.readAsDataURL(file);
        }
    }
    
    function openImageInNewTab() {
        if (clipboard_image) {
            const newWindow = window.open('', '_blank', 'width=800,height=600,menubar=no,toolbar=no,location=no,status=no');
            newWindow.document.write('<html><head><title>이미지 미리보기</title></head><body style="margin:0;padding:0;display:flex;justify-content:center;align-items:center;background:#000;"><img src="' + clipboard_image + '" style="max-width:100%;max-height:100%;" /></body></html>');
        }
    }
    </script>
    
    <div class="clipboard-area">
        <p>여기에 <strong>Ctrl+V</strong>로 캡쳐한 이미지를 붙여넣으세요</p>
        <p style="font-size: 12px; color: #666;">또는 파일을 선택하세요</p>
        <input type="file" accept="image/*" onchange="handleFileSelect(event)" style="margin-top: 10px;" />
    </div>
    
    <div id="preview-container" class="preview-container" style="display: none;">
        <h4>이미지 미리보기</h4>
        <div style="text-align: center;">
            <img id="preview-image" style="max-width: 100%; display: none; border: 1px solid #ddd; border-radius: 4px; cursor: pointer;" onclick="openImageInNewTab()" />
            <div style="margin-top: 5px; font-size: 12px; color: #666;">클릭하면 새 창에서 열립니다</div>
        </div>
    </div>
    """
    
    st.components.v1.html(clipboard_callback, height=400, scrolling=True)
    
    # 클립보드 이미지 데이터 처리
    if "clipboard_image" not in st.session_state:
        st.session_state.clipboard_image = None
    if "clipboard_timestamp" not in st.session_state:
        st.session_state.clipboard_timestamp = None
    if "clipboard_history" not in st.session_state:
        st.session_state.clipboard_history = []
    
    # 컴포넌트 값이 변경되었는지 확인
    component_value = st.session_state.get("_component_value")
    if component_value and isinstance(component_value, dict) and "image" in component_value:
        new_image = component_value["image"]
        new_timestamp = component_value.get("timestamp")
        
        if new_image != st.session_state.clipboard_image:
            # 새 이미지 저장
            st.session_state.clipboard_image = new_image
            st.session_state.clipboard_timestamp = new_timestamp
            
            # 임시 파일로 저장
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clipboard_{timestamp}.png"
            filepath = os.path.join(TEMP_IMAGE_FOLDER, filename)
            
            try:
                # 폴더가 존재하는지 확인하고 없으면 생성
                if not os.path.exists(TEMP_IMAGE_FOLDER):
                    os.makedirs(TEMP_IMAGE_FOLDER)
                
                # 이미지 데이터에서 Base64 헤더 제거
                img_data = new_image.split(',')[1] if ',' in new_image else new_image
                
                # 파일로 저장
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(img_data))
                
                # 이력에 추가
                st.session_state.clipboard_history.append({
                    "filename": filename,
                    "filepath": filepath,
                    "timestamp": new_timestamp or datetime.datetime.now().isoformat()
                })
                
                st.success("이미지가 복사되었습니다!")
            except Exception as e:
                st.error(f"이미지 처리 중 오류 발생: {str(e)}")
    
    return st.session_state.clipboard_image

# 클립보드 이미지 붙여넣기 이력 표시
def show_clipboard_history():
    if st.session_state.clipboard_history:
        st.markdown("### 이미지 붙여넣기 이력")
        
        # 클립보드 이미지 정리 버튼
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("최근에 붙여넣은 이미지 목록")
        with col2:
            if st.button("모두 삭제", key="clear_temp_images"):
                if clear_temp_images():
                    st.session_state.clipboard_history = []
                    st.success("모든 임시 이미지가 삭제되었습니다.")
                    st.rerun()
        
        # 이미지 목록 표시
        for i, item in enumerate(reversed(st.session_state.clipboard_history)):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                timestamp = datetime.datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
                st.text(f"파일: {item['filename']}")
            with col2:
                st.text(f"시간: {timestamp}")
            with col3:
                if st.button("삭제", key=f"del_temp_{i}", type="secondary"):
                    if delete_temp_image(item["filepath"]):
                        # 이력에서도 제거
                        st.session_state.clipboard_history.remove(item)
                        st.success("이미지가 삭제되었습니다.")
                        st.rerun()

# 클립보드 이미지를 파일로 저장하는 함수
def save_clipboard_image(base64_img, domain, topic, term):
    if not base64_img:
        st.error("저장할 이미지가 없습니다.")
        return None
    
    try:
        # 도메인과 토픽 폴더 생성
        domain_folder = os.path.join(IMAGE_FOLDER, domain)
        if not os.path.exists(domain_folder):
            os.makedirs(domain_folder)
        
        topic_folder = os.path.join(domain_folder, topic)
        if not os.path.exists(topic_folder):
            os.makedirs(topic_folder)
        
        # 윈도우 파일 이름으로 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_term = ''.join(c for c in term if c not in '\\/:*?"<>|')
        filename = f"{safe_term}.png"
        file_path = os.path.join(topic_folder, filename)
        
        # 이미지 데이터에서 Base64 헤더 제거
        if ',' in base64_img:
            base64_img = base64_img.split(',')[1]
        
        # 이미지 저장
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_img))
        
        # 디버그 메시지
        st.success(f"이미지가 성공적으로 저장되었습니다: {file_path}")
        
        # 파일이 제대로 생성되었는지 확인
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        else:
            st.error("이미지 저장에 실패했습니다.")
            return None
    except Exception as e:
        st.error(f"이미지 저장 중 오류가 발생했습니다: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# 초기 데이터 설정
def initialize_data():
    if not os.path.exists(DATA_FILE):
        domains = [
            "SW공학", "SW테스트", "IT경영/전력", "DB", 
            "빅데이터분석", "인공지능", "보안", "신기술", "법/제도"
        ]
        data = {domain: {} for domain in domains}
        save_data(data)
    return load_data()

# 데이터 불러오기
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        domains = [
            "SW공학", "SW테스트", "IT경영/전력", "DB", 
            "빅데이터분석", "인공지능", "보안", "신기술", "법/제도"
        ]
        return {domain: {} for domain in domains}

# 데이터 저장하기
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

# 이미지 저장 함수
def save_image(image_file, domain, topic, term):
    try:
        # 도메인과 토픽 폴더 생성
        domain_folder = os.path.join(IMAGE_FOLDER, domain)
        if not os.path.exists(domain_folder):
            os.makedirs(domain_folder)
        
        topic_folder = os.path.join(domain_folder, topic)
        if not os.path.exists(topic_folder):
            os.makedirs(topic_folder)
        
        # 파일 확장자 가져오기
        file_ext = os.path.splitext(image_file.name)[1].lower()
        if not file_ext:
            file_ext = '.png'  # 확장자가 없는 경우 기본값 설정
        
        # 파일명 생성 (용어를 기반으로)
        # 윈도우 파일 이름으로 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_term = ''.join(c for c in term if c not in '\\/:*?"<>|')
        filename = f"{safe_term}{file_ext}"
        file_path = os.path.join(topic_folder, filename)
        
        # 이미지 저장
        with open(file_path, "wb") as f:
            f.write(image_file.getbuffer())
        
        st.success(f"이미지가 저장되었습니다: {file_path}")
        return file_path
    except Exception as e:
        st.error(f"이미지 저장 중 오류 발생: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# 이미지 경로 가져오기
def get_image_path(domain, topic, term):
    try:
        # 가능한 이미지 확장자 목록
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        # 도메인과 토픽 폴더 경로
        topic_folder = os.path.join(IMAGE_FOLDER, domain, topic)
        
        # 해당 폴더가 없으면 None 반환
        if not os.path.exists(topic_folder):
            return None
        
        # 윈도우 파일 이름으로 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_term = ''.join(c for c in term if c not in '\\/:*?"<>|')
        
        # 각 확장자에 대해 파일 존재 여부 확인
        for ext in extensions:
            file_path = os.path.join(topic_folder, f"{safe_term}{ext}")
            if os.path.exists(file_path):
                return file_path
        
        # 파일명이 term을 포함하는 모든 파일 검색 (확장자는 상관없음)
        # term의 앞부분만 일치하는 경우도 찾음
        for file_name in os.listdir(topic_folder):
            file_path = os.path.join(topic_folder, file_name)
            if os.path.isfile(file_path) and term.strip() in file_name:
                return file_path
                
        # 직접 디버그 정보 출력
        st.sidebar.info(f"디버그: {topic_folder} 폴더의 파일 목록: {os.listdir(topic_folder)}")
        st.sidebar.info(f"찾으려는 파일: {safe_term}.[png/jpg/jpeg/gif/bmp]")
        
        return None
    except Exception as e:
        st.error(f"이미지 경로 검색 중 오류 발생: {str(e)}")
        return None

# 이미지 표시 함수
def display_image(domain, topic, term):
    image_path = get_image_path(domain, topic, term)

    if image_path:
        try:
            # 이미지 로드
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()

            # Base64로 인코딩
            encoded = base64.b64encode(img_bytes).decode()

            # 이미지 확장자 확인 (MIME 타입 결정용)
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_ext == '.png':
                mime_type = 'image/png'
            elif file_ext == '.gif':
                mime_type = 'image/gif'
            else:
                mime_type = 'image/png'  # 기본값

            # JavaScript 함수를 포함한 HTML 생성
            html = f"""
            <script>
            function openImageInNewWindow(base64Data, mimeType) {{
                const newWindow = window.open("", "_blank", "width=800,height=600");
                if (!newWindow) {{
                    alert("팝업 창이 차단되었습니다. 팝업 차단을 해제해주세요.");
                    return;
                }}
                
                newWindow.document.write(`
                    <html>
                    <head>
                        <title>이미지 보기</title>
                        <style>
                            body {{
                                margin: 0;
                                padding: 0;
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                min-height: 100vh;
                                background-color: #000;
                            }}
                            img {{
                                max-width: 100%;
                                max-height: 100vh;
                                object-fit: contain;
                            }}
                        </style>
                    </head>
                    <body>
                        <img src="data:${{mimeType}};base64,${{base64Data}}" />
                    </body>
                    </html>
                `);
                newWindow.document.close();
            }}
            </script>
            <div style="text-align: center; margin: 10px 0;">
                <img src="data:{mime_type};base64,{encoded}" 
                     style="max-width: 100%; max-height: 300px; cursor: pointer; border: 1px solid #ddd; border-radius: 5px;" 
                     onclick="openImageInNewWindow('{encoded}', '{mime_type}')" 
                     title="클릭하면 새 창에서 크게 볼 수 있습니다" />
                <div style="font-size: 12px; color: #666; margin-top: 5px;">이미지를 클릭하면 새 창에서 크게 볼 수 있습니다</div>
            </div>
            """
            
            # HTML 컴포넌트 표시
            st.components.v1.html(html, height=350)
            return True
        except Exception as e:
            st.error(f"이미지 표시 중 오류 발생: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    return False

# 이미지 삭제 함수
def delete_image(domain, topic, term):
    image_path = get_image_path(domain, topic, term)
    if image_path and os.path.exists(image_path):
        try:
            os.unlink(image_path)
            return True
        except Exception as e:
            st.error(f"이미지 삭제 중 오류 발생: {e}")
            return False
    return False

# 임시 이미지 삭제 함수
def delete_temp_image(filepath):
    if os.path.exists(filepath):
        try:
            os.unlink(filepath)
            return True
        except Exception as e:
            st.error(f"임시 이미지 삭제 중 오류 발생: {e}")
            return False
    return False

# 모든 임시 이미지 삭제 함수
def clear_temp_images():
    if os.path.exists(TEMP_IMAGE_FOLDER):
        try:
            for filename in os.listdir(TEMP_IMAGE_FOLDER):
                file_path = os.path.join(TEMP_IMAGE_FOLDER, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            return True
        except Exception as e:
            st.error(f"임시 이미지 폴더 정리 중 오류 발생: {e}")
            return False
    return False

# 사이드바 구성
def sidebar():
    st.sidebar.title("정보관리기술사 암기장")
    
    # 모드 관련 세션 상태 설정
    if "mode" not in st.session_state:
        st.session_state.mode = "플래시카드 관리"
    
    st.sidebar.subheader("모드 선택")
    
    # 도메인 기반 모드 선택 (버튼 인터페이스)
    if st.sidebar.button("플래시카드 관리", type="primary" if st.session_state.mode == "플래시카드 관리" else "secondary", use_container_width=True):
        st.session_state.mode = "플래시카드 관리"
        st.rerun()
        
    if st.sidebar.button("학습 모드", type="primary" if st.session_state.mode == "학습 모드" else "secondary", use_container_width=True):
        st.session_state.mode = "학습 모드"
        st.rerun()
        
    if st.sidebar.button("퀴즈 모드", type="primary" if st.session_state.mode == "퀴즈 모드" else "secondary", use_container_width=True):
        st.session_state.mode = "퀴즈 모드"
        st.rerun()
    
    st.sidebar.divider()
    
    # 전체 도메인 모드 선택
    st.sidebar.subheader("전체 도메인 모드")
    
    if st.sidebar.button("전체 도메인 토픽 학습", type="primary" if st.session_state.mode == "전체 학습" else "secondary", use_container_width=True):
        st.session_state.mode = "전체 학습"
        st.rerun()
    
    if st.sidebar.button("전체 도메인 토픽 퀴즈", type="primary" if st.session_state.mode == "전체 퀴즈" else "secondary", use_container_width=True):
        st.session_state.mode = "전체 퀴즈"
        st.rerun()
    
    st.sidebar.divider()
    
    # 도메인 선택
    data = load_data()
    domains = list(data.keys())
    
    if "selected_domain" not in st.session_state:
        st.session_state.selected_domain = domains[0] if domains else None
    
    selected_domain = st.sidebar.selectbox("도메인 선택", domains, index=domains.index(st.session_state.selected_domain) if st.session_state.selected_domain in domains else 0)
    
    # 일반 모드일 때만 도메인 업데이트
    if st.session_state.mode in ["플래시카드 관리", "학습 모드", "퀴즈 모드"]:
        st.session_state.selected_domain = selected_domain
    
    # 새 도메인 추가
    with st.sidebar.expander("새 도메인 추가"):
        new_domain = st.text_input("새 도메인 이름")
        if st.button("도메인 추가") and new_domain and new_domain not in domains:
            data[new_domain] = {}
            save_data(data)
            st.success(f"'{new_domain}' 도메인이 추가되었습니다!")
            st.rerun()
    
    # 사이드바 하단에 만든이 정보 추가
    st.sidebar.divider()
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px; margin-top: 20px; background-color: #f0f7ff; border-radius: 8px; border-left: 4px solid #4263EB; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <p style="font-weight: bold; font-size: 1rem; margin-bottom: 5px; color: #1E3A8A;">만든이 : 유민형( Vibe Coding with Cursor AI )</p>
            <p style="font-size: 0.8rem; color: #4a5568;">© 2023-2024</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 모드와 도메인 반환
    return st.session_state.mode, st.session_state.selected_domain

# 플래시카드 관리 화면
def manage_flashcards(domain):
    st.header(f"{domain} - 플래시카드 관리")
    
    data = load_data()
    
    # domain이 data에 없으면 빈 딕셔너리 추가
    if domain not in data:
        data[domain] = {}
        
    # 토픽 가져오기
    topics = data[domain]
    
    # 새 플래시카드 추가 - 신규 등록만 가능하도록 변경
    with st.expander("새 플래시카드 추가", expanded=True):
        # 새 토픽 입력
        topic_name = st.text_input("토픽 이름", key="new_topic_name")
        
        # 카드 정보 입력
        term = st.text_input("정의/개념", key="new_term")
        keyword = st.text_input("핵심키워드", key="new_keyword")
        rhyming = st.text_input("두음", key="new_rhyming")
        content = st.text_area("내용", key="new_content")
        
        # 이미지 업로드
        image_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg", "gif"], key="new_image_file")
        if image_file:
            st.image(image_file, caption="업로드된 이미지", use_container_width=True)
        
        # 제출 버튼 - 폼이 제출되면 데이터 저장 후 페이지 새로고침
        if st.button("플래시카드 추가", key="add_flashcard_btn"):
            # 필수 필드 검증
            if not topic_name:
                st.error("토픽 이름을 입력해주세요.")
            elif not term:
                st.error("정의/개념을 입력해주세요.")
            elif not content:
                st.error("내용을 입력해주세요.")
            else:
                if topic_name not in topics:
                    topics[topic_name] = {}
                
                # 주제, 특징, 내용을 포함하는 데이터 구조
                card_data = {
                    "subject": term,
                    "keyword": keyword,
                    "rhyming": rhyming,
                    "content": content
                }
                
                # 같은 토픽/용어 조합이 이미 존재하는지 확인
                if term in topics[topic_name]:
                    st.error(f"'{topic_name}' 토픽에 '{term}' 정의/개념이 이미 존재합니다. 다른 이름을 사용하거나 아래에서 기존 카드를 수정하세요.")
                else:
                    topics[topic_name][term] = card_data
                    save_data(data)
                    
                    # 이미지 저장 처리
                    image_saved = False
                    
                    # 파일 업로드로 이미지 저장
                    if image_file:
                        try:
                            image_path = save_image(image_file, domain, topic_name, term)
                            if image_path:
                                image_saved = True
                        except Exception as e:
                            st.error(f"이미지 저장 중 오류 발생: {str(e)}")
                    
                    # 저장 성공 메시지
                    if image_saved:
                        st.success(f"'{term}' 플래시카드와 이미지가 '{topic_name}' 토픽에 추가되었습니다!")
                    else:
                        st.success(f"'{term}' 플래시카드가 '{topic_name}' 토픽에 추가되었습니다!")
                    
                    # 입력 필드 초기화
                    # st.session_state.new_topic_name = ""
                    # st.session_state.new_term = ""
                    # st.session_state.new_keyword = ""
                    # st.session_state.new_rhyming = ""
                    # st.session_state.new_content = ""
                    
                    # 페이지 새로고침
                    time.sleep(1)
                    st.rerun()
    
    # 기존 플래시카드 보기
    if topics:
        st.subheader("기존 플래시카드")
        for topic_name, cards in topics.items():
            with st.expander(f"토픽: {topic_name} ({len(cards)}개)"):
                # 토픽 삭제 버튼
                if st.button(f"토픽 삭제: {topic_name}", key=f"del_topic_{topic_name}"):
                    # 해당 토픽의 이미지 폴더 삭제
                    topic_folder = os.path.join(IMAGE_FOLDER, domain, topic_name)
                    if os.path.exists(topic_folder):
                        try:
                            for filename in os.listdir(topic_folder):
                                file_path = os.path.join(topic_folder, filename)
                                if os.path.isfile(file_path):
                                    os.unlink(file_path)
                            os.rmdir(topic_folder)
                        except Exception as e:
                            st.error(f"이미지 폴더 삭제 중 오류 발생: {e}")
                    
                    del data[domain][topic_name]
                    save_data(data)
                    st.success(f"'{topic_name}' 토픽이 삭제되었습니다!")
                    time.sleep(1)
                    st.rerun()
                
                # 카드 목록
                for term, card_data in cards.items():
                    st.markdown("---")
                    st.markdown(f"### 정의/개념 : {term}")
                    
                    # 수정 가능한 입력 필드
                    edit_col1, edit_col2 = st.columns([1, 3])
                    
                    with edit_col1:
                        # 이미지 표시
                        image_path = get_image_path(domain, topic_name, term)
                        if image_path:
                            display_image(domain, topic_name, term)
                            
                            # 이미지 삭제 버튼
                            if st.button("이미지 삭제", key=f"del_img_{topic_name}_{term}", type="secondary"):
                                if delete_image(domain, topic_name, term):
                                    st.success("이미지가 삭제되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                            
                            # 이미지 업데이트
                            st.markdown("#### 이미지 업데이트")
                            update_image_file = st.file_uploader("새 이미지 업로드", type=["png", "jpg", "jpeg", "gif"], key=f"update_image_{topic_name}_{term}")
                            if update_image_file:
                                st.image(update_image_file, caption="업로드할 이미지", use_container_width=True)
                                
                                if st.button("이미지 업데이트", key=f"update_img_btn_{topic_name}_{term}"):
                                    try:
                                        # 이전 이미지 제거 후 새 이미지 저장
                                        delete_image(domain, topic_name, term)
                                        save_image(update_image_file, domain, topic_name, term)
                                        st.success("이미지가 업데이트되었습니다.")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"이미지 업데이트 중 오류: {str(e)}")
                        else:
                            # 이미지 추가 기능
                            st.markdown("#### 이미지 추가")
                            new_image = st.file_uploader(f"이미지 ({term})", 
                                                      type=["png", "jpg", "jpeg", "gif"], 
                                                      key=f"add_img_{topic_name}_{term}")
                            if new_image:
                                st.image(new_image, caption="추가할 이미지", use_container_width=True)
                                
                                if st.button("이미지 추가", key=f"add_img_btn_{topic_name}_{term}"):
                                    save_image(new_image, domain, topic_name, term)
                                    st.success("이미지가 추가되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                    
                    with edit_col2:
                        # 토픽 이름 변경 기능 추가
                        new_topic_name = st.text_input("토픽 이름", value=topic_name, key=f"edit_topic_{topic_name}_{term}")
                        
                        # 정의/개념 변경 기능 추가
                        new_term = st.text_input("정의/개념", value=term, key=f"edit_term_{topic_name}_{term}")
                        
                        # 편집 가능한 필드들
                        new_keyword = st.text_input("핵심키워드", value=card_data.get("keyword", ""), key=f"edit_keyword_{topic_name}_{term}")
                        new_rhyming = st.text_input("두음", value=card_data.get("rhyming", ""), key=f"edit_rhyming_{topic_name}_{term}")
                        new_content = st.text_area("내용", value=card_data.get("content", ""), height=150, key=f"edit_content_{topic_name}_{term}")
                        
                        # 변경 저장 버튼
                        col_save, col_del = st.columns(2)
                        with col_save:
                            if st.button("변경 저장", key=f"save_edit_{topic_name}_{term}"):
                                topic_changed = new_topic_name != topic_name
                                term_changed = new_term != term
                                
                                # 토픽 이름 또는 용어가 변경된 경우
                                if topic_changed or term_changed:
                                    # 새 토픽 확인 및 생성
                                    if new_topic_name not in data[domain]:
                                        data[domain][new_topic_name] = {}
                                    
                                    # 같은 토픽/용어 조합이 이미 존재하는지 확인
                                    if term_changed and new_term in data[domain][new_topic_name]:
                                        st.error(f"'{new_topic_name}' 토픽에 '{new_term}' 정의/개념이 이미 존재합니다.")
                                    else:
                                        # 이미지 경로 저장
                                        old_image_path = get_image_path(domain, topic_name, term)
                                        has_image = old_image_path and os.path.exists(old_image_path)
                                        
                                        # 카드 데이터 업데이트
                                        updated_card_data = {
                                            "subject": new_term,
                                            "keyword": new_keyword,
                                            "rhyming": new_rhyming,
                                            "content": new_content
                                        }
                                        
                                        # 새 위치에 카드 추가
                                        data[domain][new_topic_name][new_term] = updated_card_data
                                        
                                        # 원래 카드 삭제
                                        del data[domain][topic_name][term]
                                        
                                        # 원래 토픽이 비어있으면 삭제
                                        if not data[domain][topic_name]:
                                            del data[domain][topic_name]
                                        
                                        # 이미지 이동 처리
                                        if has_image:
                                            try:
                                                # 새 폴더 확인 및 생성
                                                new_topic_folder = os.path.join(IMAGE_FOLDER, domain, new_topic_name)
                                                if not os.path.exists(new_topic_folder):
                                                    os.makedirs(new_topic_folder)
                                                
                                                # 이미지 파일 확장자 가져오기
                                                _, ext = os.path.splitext(old_image_path)
                                                
                                                # 윈도우 파일 이름으로 사용할 수 없는 문자 제거
                                                safe_term = ''.join(c for c in new_term if c not in '\\/:*?"<>|')
                                                new_image_path = os.path.join(new_topic_folder, f"{safe_term}{ext}")
                                                
                                                # 이미지 파일 이동
                                                import shutil
                                                shutil.copy2(old_image_path, new_image_path)
                                                os.unlink(old_image_path)
                                            except Exception as e:
                                                st.error(f"이미지 이동 중 오류 발생: {str(e)}")
                                        
                                        # 데이터 저장
                                        save_data(data)
                                        st.success(f"카드가 '{new_topic_name}' 토픽의 '{new_term}'으로 업데이트되었습니다!")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    # 카드 데이터만 업데이트
                                    card_data["keyword"] = new_keyword
                                    card_data["rhyming"] = new_rhyming
                                    card_data["content"] = new_content
                                    data[domain][topic_name][term] = card_data
                                    
                                    # 데이터 저장 및 페이지 새로고침
                                    save_data(data)
                                    st.success(f"'{term}' 카드가 업데이트되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                        
                        with col_del:
                            if st.button("카드 삭제", key=f"del_{topic_name}_{term}"):
                                # 연결된 이미지 삭제
                                image_path = get_image_path(domain, topic_name, term)
                                if image_path and os.path.exists(image_path):
                                    os.unlink(image_path)
                                
                                del data[domain][topic_name][term]
                                if not data[domain][topic_name]:  # 토픽에 카드가 없으면 토픽도 삭제
                                    del data[domain][topic_name]
                                save_data(data)
                                st.success(f"'{term}' 카드가 삭제되었습니다!")
                                time.sleep(1)
                                st.rerun()
    
    else:
        st.info(f"{domain} 도메인에 아직 플래시카드가 없습니다. 새 플래시카드를 추가해보세요!")

# 학습 모드 화면
def study_mode(domain):
    import random  # random 모듈 추가
    st.header(f"{domain} - 학습 모드")
    
    data = load_data()
    topics = data[domain]
    
    if not topics:
        st.info(f"{domain} 도메인에 아직 플래시카드가 없습니다. 플래시카드를 추가한 후 학습해보세요!")
        return
    
    # 토픽 선택
    all_topics = list(topics.keys())
    selected_topics = st.multiselect("학습할 토픽 선택", all_topics, default=all_topics)
    
    if not selected_topics:
        st.warning("학습할 토픽을 선택해주세요.")
        return
    
    # 선택된 토픽에서 카드 가져오기
    all_cards = []
    for topic in selected_topics:
        for term, card_data in topics[topic].items():
            all_cards.append({"topic": topic, "term": term, "card_data": card_data})
    
    if not all_cards:
        st.warning("선택한 토픽에 플래시카드가 없습니다.")
        return
    
    st.write(f"총 {len(all_cards)}개의 플래시카드가 있습니다.")
    
    # 세션 상태 초기화
    if "study_cards" not in st.session_state:
        st.session_state.study_cards = all_cards.copy()
        random.shuffle(st.session_state.study_cards)  # 초기에 카드 섞기
        st.session_state.current_card_index = 0
        # 기본값을 True로 설정하여 처음부터 모든 내용이 보이도록 함
        st.session_state.study_show_content = True
        st.session_state.study_show_keyword = True
        st.session_state.study_show_rhyming = True
    
    # 카드가 변경되었는지 확인 (토픽 선택 변경시)
    current_cards_ids = set(f"{card['topic']}_{card['term']}" for card in all_cards)
    session_cards_ids = set(f"{card['topic']}_{card['term']}" for card in st.session_state.study_cards)
    
    if current_cards_ids != session_cards_ids:
        st.session_state.study_cards = all_cards.copy()
        st.session_state.current_card_index = 0
        # 토픽이 변경되어도 보기 상태 유지
        st.session_state.study_show_content = True
        st.session_state.study_show_keyword = True
        st.session_state.study_show_rhyming = True
    
    # 카드 섞기 버튼 - 퀴즈 모드와 동일한 패턴으로 구현
    if st.button("카드 섞기", key="study_shuffle_button"):
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        
        # 세션 상태 업데이트
        st.session_state.study_cards = shuffled_cards
        st.session_state.current_card_index = 0
        # 카드 섞기 후에도 보기 상태 유지
        st.session_state.study_show_content = True
        st.session_state.study_show_keyword = True
        st.session_state.study_show_rhyming = True
        
        st.success("카드가 섞였습니다!")
        st.rerun()
    
    # 플래시카드 보여주기
    if st.session_state.study_cards:
        current_card = st.session_state.study_cards[st.session_state.current_card_index]
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(f"토픽: {current_card['topic']}")
        with col2:
            st.write(f"{st.session_state.current_card_index + 1}/{len(st.session_state.study_cards)}")
        
        # 카드 컨테이너 분할 (텍스트 / 이미지)
        text_col, image_col = st.columns([3, 2])
        
        with text_col:
            # 카드 표시
            st.markdown(f"""
            <div class="card">
                <h2>{current_card['term']}</h2>
                <p>정의/개념</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 핵심키워드 표시 - 버튼 텍스트 변경
            keyword_button_text = "핵심키워드 가리기" if st.session_state.study_show_keyword else "핵심키워드 보기"
            if st.button(keyword_button_text, key="study_keyword_btn"):
                st.session_state.study_show_keyword = not st.session_state.study_show_keyword
                st.rerun()
                
            if st.session_state.study_show_keyword:
                st.markdown("### 핵심키워드")
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
            
            # 두음 표시 - 버튼 텍스트 변경
            rhyming_button_text = "두음 가리기" if st.session_state.study_show_rhyming else "두음 보기"
            if st.button(rhyming_button_text, key="study_rhyming_btn"):
                st.session_state.study_show_rhyming = not st.session_state.study_show_rhyming
                st.rerun()
                
            if st.session_state.study_show_rhyming:
                st.markdown("### 두음")
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
                
            # 내용 표시 - 버튼 텍스트 변경
            content_button_text = "내용 가리기" if st.session_state.study_show_content else "내용 보기"
            if st.button(content_button_text, key="study_content_btn"):
                st.session_state.study_show_content = not st.session_state.study_show_content
                st.rerun()
                
            if st.session_state.study_show_content:
                st.markdown("### 내용")
                st.markdown(current_card['card_data']['content'])
        
        with image_col:
            # 이미지 표시 (정의/개념을 기준으로 이미지 경로 구성)
            term = current_card['term']
            image_path = get_image_path(domain, current_card['topic'], term)
            if image_path:
                display_image(domain, current_card['topic'], term)
            else:
                st.info("이 카드에는 이미지가 없습니다.")
        
        # 버튼 행 - 모두 보기 버튼 추가
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("이전", key="prev_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index - 1) % len(st.session_state.study_cards)
                # 이전 카드로 이동해도 보기 상태 유지
                st.rerun()
        
        with col2:
            if st.button("모두 가리기", key="hide_all"):
                st.session_state.study_show_content = False
                st.session_state.study_show_keyword = False
                st.session_state.study_show_rhyming = False
                st.rerun()
        
        with col3:
            if st.button("모두 보기", key="show_all"):
                st.session_state.study_show_content = True
                st.session_state.study_show_keyword = True
                st.session_state.study_show_rhyming = True
                st.rerun()
        
        with col4:
            if st.button("다음", key="next_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(st.session_state.study_cards)
                # 다음 카드로 이동해도 보기 상태 유지
                st.rerun()

# 전체 도메인 학습 모드
def all_domains_study_mode():
    import random  # random 모듈 추가
    st.header("전체 도메인 학습 모드")
    
    # 세션 상태를 유지하여 키 충돌 방지
    if "all_study_initialized" not in st.session_state:
        st.session_state.all_study_initialized = True
        if "all_current_card_index" not in st.session_state:
            st.session_state.all_current_card_index = 0
        if "all_study_show_content" not in st.session_state:
            st.session_state.all_study_show_content = True  # 기본값을 True로 설정
        if "all_study_show_keyword" not in st.session_state:
            st.session_state.all_study_show_keyword = True  # 기본값을 True로 설정
        if "all_study_show_rhyming" not in st.session_state:
            st.session_state.all_study_show_rhyming = True  # 기본값을 True로 설정
        if "all_study_cards" not in st.session_state:
            # 모든 도메인의 모든 카드 가져오기
            all_cards = []
            data = load_data()
            for domain, topics in data.items():
                for topic, cards in topics.items():
                    for term, card_data in cards.items():
                        all_cards.append({
                            "domain": domain,
                            "topic": topic,
                            "term": term,
                            "card_data": card_data
                        })
            st.session_state.all_study_cards = all_cards
    
    data = load_data()
    
    # 모든 도메인의 모든 카드 가져오기
    all_cards = []
    for domain, topics in data.items():
        for topic, cards in topics.items():
            for term, card_data in cards.items():
                all_cards.append({
                    "domain": domain,
                    "topic": topic,
                    "term": term,
                    "card_data": card_data
                })
    
    if not all_cards:
        st.warning("학습할 카드가 없습니다. 플래시카드를 추가한 후 학습해보세요!")
        return
    
    st.write(f"총 {len(all_cards)}개의 플래시카드가 있습니다.")
    
    # 카드가 변경되었는지 확인
    if len(st.session_state.all_study_cards) != len(all_cards):
        st.session_state.all_study_cards = all_cards.copy()
        st.session_state.all_current_card_index = 0
        # 토픽이 변경되어도 보기 상태는 유지
        st.session_state.all_study_show_content = True
        st.session_state.all_study_show_keyword = True
        st.session_state.all_study_show_rhyming = True
    
    # 플래시카드 보여주기
    if st.session_state.all_study_cards:
        current_card = st.session_state.all_study_cards[st.session_state.all_current_card_index]
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div style="margin-bottom: 10px;">
                <span style="font-size: 14px; color: #666;">도메인: {current_card['domain']}</span><br/>
                <span style="font-size: 24px; font-weight: bold; color: #1E3A8A;">토픽: {current_card['topic']}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.write(f"{st.session_state.all_current_card_index + 1}/{len(st.session_state.all_study_cards)}")
        
        # 카드 컨테이너 분할 (텍스트 / 이미지)
        text_col, image_col = st.columns([3, 2])
        
        with text_col:
            # 카드 표시
            st.markdown(f"""
            <div class="card">
                <h2>{current_card['term']}</h2>
                <p>정의/개념</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 핵심키워드 표시 - 버튼 텍스트 변경
            keyword_button_text = "핵심키워드 가리기" if st.session_state.all_study_show_keyword else "핵심키워드 보기"
            keyword_btn = st.button(keyword_button_text, key="all_study_keyword_btn")
            if keyword_btn:
                st.session_state.all_study_show_keyword = not st.session_state.all_study_show_keyword
                st.rerun()
                
            if st.session_state.all_study_show_keyword:
                st.markdown("### 핵심키워드")
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
            
            # 두음 표시 - 버튼 텍스트 변경
            rhyming_button_text = "두음 가리기" if st.session_state.all_study_show_rhyming else "두음 보기"
            rhyming_btn = st.button(rhyming_button_text, key="all_study_rhyming_btn")
            if rhyming_btn:
                st.session_state.all_study_show_rhyming = not st.session_state.all_study_show_rhyming
                st.rerun()
                
            if st.session_state.all_study_show_rhyming:
                st.markdown("### 두음")
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
            
            # 내용 표시 - 버튼 텍스트 변경
            content_button_text = "내용 가리기" if st.session_state.all_study_show_content else "내용 보기"
            content_btn = st.button(content_button_text, key="all_study_content_btn")
            if content_btn:
                st.session_state.all_study_show_content = not st.session_state.all_study_show_content
                st.rerun()
                
            if st.session_state.all_study_show_content:
                st.markdown("### 내용")
                st.markdown(current_card['card_data']['content'])
        
        with image_col:
            # 이미지 표시
            domain = current_card['domain']
            topic = current_card['topic']
            term = current_card['term']
            image_path = get_image_path(domain, topic, term)
            if image_path:
                display_image(domain, topic, term)
            else:
                st.info("이 카드에는 이미지가 없습니다.")
        
        # 버튼 행 - 모두 보기 버튼 추가
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            prev_btn = st.button("이전", key="all_prev_card")
            if prev_btn:
                st.session_state.all_current_card_index = (st.session_state.all_current_card_index - 1) % len(st.session_state.all_study_cards)
                # 이전 카드로 이동해도 보기 상태는 유지
                st.rerun()
        
        with col2:
            hide_btn = st.button("모두 가리기", key="all_hide_all")
            if hide_btn:
                st.session_state.all_study_show_content = False
                st.session_state.all_study_show_keyword = False
                st.session_state.all_study_show_rhyming = False
                st.rerun()
        
        with col3:
            show_btn = st.button("모두 보기", key="all_show_all")
            if show_btn:
                st.session_state.all_study_show_content = True
                st.session_state.all_study_show_keyword = True
                st.session_state.all_study_show_rhyming = True
                st.rerun()
        
        with col4:
            next_btn = st.button("다음", key="all_next_card")
            if next_btn:
                st.session_state.all_current_card_index = (st.session_state.all_current_card_index + 1) % len(st.session_state.all_study_cards)
                # 다음 카드로 이동해도 보기 상태는 유지
                st.rerun()
        
        # 셔플 버튼
        shuffle_btn = st.button("카드 섞기", key="all_shuffle_cards")
        if shuffle_btn:
            shuffled_cards = st.session_state.all_study_cards.copy()
            random.shuffle(shuffled_cards)
            st.session_state.all_study_cards = shuffled_cards
            st.session_state.all_current_card_index = 0
            # 카드 섞기 후에도 보기 상태는 유지
            st.session_state.all_study_show_content = True
            st.session_state.all_study_show_keyword = True
            st.session_state.all_study_show_rhyming = True
            st.success("카드가 섞였습니다!")
            st.rerun()

# 전체 도메인 퀴즈 모드
def all_domains_quiz_mode():
    import random  # random 모듈 추가
    st.header("전체 도메인 퀴즈 모드")
    
    # 세션 상태 초기화 (한 번만 실행)
    if "all_quiz_initialized" not in st.session_state:
        st.session_state.all_quiz_initialized = True
        if "all_quiz_cards" not in st.session_state:
            # 모든 도메인의 모든 카드 가져오기
            all_cards = []
            data = load_data()
            for domain, topics in data.items():
                for topic, cards in topics.items():
                    for term, card_data in cards.items():
                        all_cards.append({
                            "domain": domain,
                            "topic": topic,
                            "term": term,
                            "card_data": card_data
                        })
            
            if all_cards:
                random.shuffle(all_cards)
                st.session_state.all_quiz_cards = all_cards
                st.session_state.all_current_quiz_index = 0
                st.session_state.all_quiz_score = 0
                st.session_state.all_quiz_total = min(10, len(all_cards))
                st.session_state.all_user_answer = ""
                st.session_state.all_quiz_answer_checked = False
                st.session_state.all_quiz_completed = False
                st.session_state.all_show_quiz_hint = False
                st.session_state.all_show_quiz_keyword = False
                st.session_state.all_show_quiz_rhyming = False
                st.session_state.all_show_quiz_content = False
                st.session_state.all_show_quiz_image = False
    
    data = load_data()
    
    # 모든 도메인의 모든 카드 가져오기
    all_cards = []
    for domain, topics in data.items():
        for topic, cards in topics.items():
            for term, card_data in cards.items():
                all_cards.append({
                    "domain": domain,
                    "topic": topic,
                    "term": term,
                    "card_data": card_data
                })
    
    if not all_cards:
        st.warning("퀴즈 문제가 없습니다. 플래시카드를 추가한 후 퀴즈를 풀어보세요!")
        return
    
    # 문제 수 선택
    max_questions = min(100, len(all_cards))
    
    # 카드가 1개일 경우 슬라이더를 사용하지 않음
    if max_questions == 1:
        quiz_total = 1
        st.info("플래시카드가 1개뿐입니다. 1문제로 퀴즈가 진행됩니다.")
    else:
        default_value = min(10, max_questions)
        quiz_total = st.slider("퀴즈 문제 수", 1, max_questions, default_value)
    
    # 카드 섞기 버튼
    if st.button("카드 섞기", key="all_quiz_shuffle_cards"):
        import random
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        st.session_state.all_quiz_cards = shuffled_cards
        st.session_state.all_current_quiz_index = 0
        st.session_state.all_quiz_score = 0
        st.session_state.all_quiz_total = quiz_total
        st.session_state.all_user_answer = ""
        st.session_state.all_quiz_answer_checked = False
        st.session_state.all_quiz_completed = False
        st.session_state.all_show_quiz_hint = False
        st.session_state.all_show_quiz_keyword = False
        st.session_state.all_show_quiz_rhyming = False
        st.session_state.all_show_quiz_content = False
        st.session_state.all_show_quiz_image = False
        st.success("카드가 섞였습니다!")
        st.rerun()
    
    # 새 퀴즈 시작 버튼
    new_quiz_btn = st.button("새 퀴즈 시작")
    if new_quiz_btn:
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        st.session_state.all_quiz_cards = shuffled_cards
        st.session_state.all_current_quiz_index = 0
        st.session_state.all_quiz_score = 0
        st.session_state.all_quiz_total = quiz_total
        st.session_state.all_user_answer = ""
        st.session_state.all_quiz_answer_checked = False
        st.session_state.all_quiz_completed = False
        st.session_state.all_show_quiz_hint = False
        st.session_state.all_show_quiz_keyword = False
        st.session_state.all_show_quiz_rhyming = False
        st.session_state.all_show_quiz_content = False
        st.session_state.all_show_quiz_image = False
        st.rerun()
    
    # 카드가 변경되었는지 확인 (데이터 추가/삭제 시)
    if "all_quiz_cards" not in st.session_state or len(st.session_state.all_quiz_cards) != len(all_cards):
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        st.session_state.all_quiz_cards = shuffled_cards
        st.session_state.all_current_quiz_index = 0
        st.session_state.all_quiz_score = 0
        st.session_state.all_quiz_total = quiz_total
    
    # 퀴즈가 완료되었는지 확인
    if st.session_state.all_quiz_completed:
        st.success(f"퀴즈 완료! 점수: {st.session_state.all_quiz_score}/{st.session_state.all_quiz_total}")
        replay_btn = st.button("다시 풀기")
        if replay_btn:
            shuffled_cards = all_cards.copy()
            random.shuffle(shuffled_cards)
            st.session_state.all_quiz_cards = shuffled_cards
            st.session_state.all_current_quiz_index = 0
            st.session_state.all_quiz_score = 0
            st.session_state.all_quiz_total = quiz_total
            st.session_state.all_user_answer = ""
            st.session_state.all_quiz_answer_checked = False
            st.session_state.all_quiz_completed = False
            st.session_state.all_show_quiz_hint = False
            st.session_state.all_show_quiz_keyword = False
            st.session_state.all_show_quiz_rhyming = False
            st.session_state.all_show_quiz_content = False
            st.session_state.all_show_quiz_image = False
            st.rerun()
        return
    
    # 현재 퀴즈 카드
    current_card = st.session_state.all_quiz_cards[st.session_state.all_current_quiz_index]
    
    st.markdown(f"""
    <div class='card'>
        <h3>문제 {st.session_state.all_current_quiz_index + 1}/{st.session_state.all_quiz_total}</h3>
        <div style="margin-bottom: 10px;">
            <span style="font-size: 14px; color: #666;">도메인 : {current_card['domain']}</span><br/>
            <span style="font-size: 24px; font-weight: bold; color: #1E3A8A;">토픽 : {current_card['topic']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 컨텐츠 열 분할 (퀴즈 / 이미지)
    quiz_col, image_col = st.columns([3, 2])
    
    with quiz_col:
        st.markdown(f"""
        <div class='concept-card'>
            <h2>{current_card['topic']}</h2>
            <p>위 토픽에 해당하는 정의/개념은 무엇인가요?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 힌트 버튼들
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # 정의/개념 힌트
            term_hint_btn = st.button("정의/개념 힌트", key="all_quiz_term_btn")
            if term_hint_btn:
                st.session_state.all_show_quiz_hint = not st.session_state.all_show_quiz_hint
                st.rerun()
        
        with col2:
            # 핵심키워드 힌트
            keyword_hint_btn = st.button("핵심키워드 힌트", key="all_quiz_keyword_btn")
            if keyword_hint_btn:
                st.session_state.all_show_quiz_keyword = not st.session_state.all_show_quiz_keyword
                st.rerun()
        
        with col3:
            # 두음 힌트
            rhyming_hint_btn = st.button("두음 힌트", key="all_quiz_rhyming_btn")
            if rhyming_hint_btn:
                st.session_state.all_show_quiz_rhyming = not st.session_state.all_show_quiz_rhyming
                st.rerun()
        
        with col4:
            # 내용 힌트
            content_hint_btn = st.button("내용 힌트", key="all_quiz_content_btn")
            if content_hint_btn:
                st.session_state.all_show_quiz_content = not st.session_state.all_show_quiz_content
                st.rerun()
        
        with col5:
            # 이미지 힌트
            image_hint_btn = st.button("이미지 보기", key="all_quiz_image_btn")
            if image_hint_btn:
                st.session_state.all_show_quiz_image = not st.session_state.all_show_quiz_image
                st.rerun()
        
        # 힌트 표시 영역
        hint_displayed = False
        
        # 정의/개념 힌트
        if st.session_state.all_show_quiz_hint:
            hint_displayed = True
            with st.expander("정의/개념 힌트", expanded=True):
                st.markdown(f"**정의/개념:** {current_card['term']}")
        
        # 핵심키워드 힌트
        if st.session_state.all_show_quiz_keyword:
            hint_displayed = True
            with st.expander("핵심키워드 힌트", expanded=True):
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
        
        # 두음 힌트
        if st.session_state.all_show_quiz_rhyming:
            hint_displayed = True
            with st.expander("두음 힌트", expanded=True):
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
        
        # 내용 힌트
        if st.session_state.all_show_quiz_content:
            hint_displayed = True
            with st.expander("내용 힌트", expanded=True):
                st.markdown(current_card['card_data']['content'])
        
        # 사용자 답변 입력
        if not st.session_state.all_quiz_answer_checked:
            user_answer = st.text_area("답변", key="all_answer_input", height=100)
            check_answer_btn = st.button("정답 확인")
            if check_answer_btn:
                st.session_state.all_user_answer = user_answer
                st.session_state.all_quiz_answer_checked = True
                st.rerun()
        else:
            st.text_area("답변", value=st.session_state.all_user_answer, disabled=True, height=100)
            
            # 정답 표시
            st.markdown("### 정답")
            # 정의/개념 정답
            st.markdown(f"**정의/개념:** {current_card['term']}")
            # 핵심키워드 정답
            st.markdown(f"**핵심키워드:** {current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.')}")
            # 두음 정답
            st.markdown(f"**두음:** {current_card['card_data'].get('rhyming', '두음 정보가 없습니다.')}")
            # 내용 정답
            st.markdown(f"**내용:** {current_card['card_data']['content']}")
            
            # 자가 채점
            col1, col2 = st.columns(2)
            with col1:
                correct_btn = st.button("맞았어요")
                if correct_btn:
                    st.session_state.all_quiz_score += 1
                    if st.session_state.all_current_quiz_index + 1 < st.session_state.all_quiz_total:
                        st.session_state.all_current_quiz_index += 1
                        st.session_state.all_quiz_answer_checked = False
                        st.session_state.all_show_quiz_hint = False
                        st.session_state.all_show_quiz_keyword = False
                        st.session_state.all_show_quiz_rhyming = False
                        st.session_state.all_show_quiz_content = False
                        st.session_state.all_show_quiz_image = False
                    else:
                        st.session_state.all_quiz_completed = True
                    st.rerun()
            
            with col2:
                wrong_btn = st.button("틀렸어요")
                if wrong_btn:
                    if st.session_state.all_current_quiz_index + 1 < st.session_state.all_quiz_total:
                        st.session_state.all_current_quiz_index += 1
                        st.session_state.all_quiz_answer_checked = False
                        st.session_state.all_show_quiz_hint = False
                        st.session_state.all_show_quiz_keyword = False
                        st.session_state.all_show_quiz_rhyming = False
                        st.session_state.all_show_quiz_content = False
                        st.session_state.all_show_quiz_image = False
                    else:
                        st.session_state.all_quiz_completed = True
                    st.rerun()
    
    with image_col:
        # 이미지는 힌트 버튼을 누른 경우에만 표시
        if st.session_state.all_show_quiz_image:
            # 이미지 표시
            domain = current_card['domain']
            topic = current_card['topic']
            term = current_card['term']
            image_path = get_image_path(domain, topic, term)
            if image_path:
                display_image(domain, topic, term)
            else:
                st.info("이 카드에는 이미지가 없습니다.")

# 퀴즈 모드 화면
def quiz_mode(domain):
    import random  # random 모듈 추가
    st.header(f"{domain} - 퀴즈 모드")
    
    data = load_data()
    topics = data[domain]
    
    if not topics:
        st.info(f"{domain} 도메인에 아직 플래시카드가 없습니다. 플래시카드를 추가한 후 퀴즈를 풀어보세요!")
        return
    
    # 토픽 선택
    all_topics = list(topics.keys())
    selected_topics = st.multiselect("퀴즈 토픽 선택", all_topics, default=all_topics)
    
    if not selected_topics:
        st.warning("퀴즈를 볼 토픽을 선택해주세요.")
        return
    
    # 선택된 토픽에서 카드 가져오기
    all_cards = []
    for topic in selected_topics:
        for term, card_data in topics[topic].items():
            all_cards.append({"topic": topic, "term": term, "card_data": card_data})
    
    if not all_cards:
        st.warning("선택한 토픽에 플래시카드가 없습니다.")
        return
    
    # 문제 수 선택
    max_questions = min(100, len(all_cards))
    
    # 카드가 1개일 경우 슬라이더를 사용하지 않음
    if max_questions == 1:
        quiz_total = 1
        st.info("플래시카드가 1개뿐입니다. 1문제로 퀴즈가 진행됩니다.")
    else:
        default_value = min(10, max_questions)
        quiz_total = st.slider("퀴즈 문제 수", 1, max_questions, default_value)
    
    # 카드 섞기 버튼
    if st.button("카드 섞기", key="quiz_shuffle_cards"):
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        
        # 세션 상태 초기화 및 섞인 카드 설정
        st.session_state.quiz_cards = shuffled_cards
        st.session_state.current_quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = quiz_total
        st.session_state.user_answer = ""
        st.session_state.quiz_answer_checked = False
        st.session_state.quiz_completed = False
        st.session_state.show_quiz_hint = False
        st.session_state.show_quiz_keyword = False
        st.session_state.show_quiz_rhyming = False
        st.session_state.show_quiz_content = False
        st.session_state.show_quiz_image = False
        
        st.success("카드가 섞였습니다!")
        st.rerun()
    
    # 세션 상태 초기화
    if "quiz_cards" not in st.session_state or st.button("새 퀴즈 시작"):
        st.session_state.quiz_cards = all_cards.copy()
        random.shuffle(st.session_state.quiz_cards)
        st.session_state.current_quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = quiz_total
        st.session_state.user_answer = ""
        st.session_state.quiz_answer_checked = False
        st.session_state.quiz_completed = False
        st.session_state.show_quiz_hint = False
        st.session_state.show_quiz_keyword = False
        st.session_state.show_quiz_rhyming = False
        st.session_state.show_quiz_content = False
        st.session_state.show_quiz_image = False
    
    # 퀴즈가 완료되었는지 확인
    if st.session_state.quiz_completed:
        st.success(f"퀴즈 완료! 점수: {st.session_state.quiz_score}/{st.session_state.quiz_total}")
        if st.button("다시 풀기"):
            st.session_state.quiz_cards = all_cards.copy()
            random.shuffle(st.session_state.quiz_cards)
            st.session_state.current_quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_total = quiz_total
            st.session_state.user_answer = ""
            st.session_state.quiz_answer_checked = False
            st.session_state.quiz_completed = False
            st.session_state.show_quiz_hint = False
            st.session_state.show_quiz_keyword = False
            st.session_state.show_quiz_rhyming = False
            st.session_state.show_quiz_content = False
            st.session_state.show_quiz_image = False
            st.rerun()
        return
    
    # 현재 퀴즈 카드
    current_card = st.session_state.quiz_cards[st.session_state.current_quiz_index]
    
    # 퀴즈 타입 설정 - 항상 토픽 보여주고 정의/개념, 특징, 내용 묻기
    quiz_type = "topic_to_all"
    
    st.markdown(f"""
    <div class='card'>
        <h3>문제 {st.session_state.current_quiz_index + 1}/{st.session_state.quiz_total}</h3>
        <div style="margin-bottom: 10px;">
            <span style="font-size: 14px; color: #666;">도메인: {domain}</span><br/>
            <span style="font-size: 24px; font-weight: bold; color: #1E3A8A;">토픽: {current_card['topic']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 컨텐츠 열 분할 (퀴즈 / 이미지)
    quiz_col, image_col = st.columns([3, 2])
    
    with quiz_col:
        st.markdown(f"""
        <div class='concept-card'>
            <h2>{current_card['topic']}</h2>
            <p>위 토픽에 해당하는 정의/개념은 무엇인가요?</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 힌트 버튼들
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # 정의/개념 힌트
            if st.button("정의/개념 힌트", key="quiz_term_btn"):
                st.session_state.show_quiz_hint = not st.session_state.show_quiz_hint
                st.rerun()
        
        with col2:
            # 핵심키워드 힌트
            if st.button("핵심키워드 힌트", key="quiz_keyword_btn"):
                st.session_state.show_quiz_keyword = not st.session_state.show_quiz_keyword
                st.rerun()
        
        with col3:
            # 두음 힌트
            if st.button("두음 힌트", key="quiz_rhyming_btn"):
                st.session_state.show_quiz_rhyming = not st.session_state.show_quiz_rhyming
                st.rerun()
            
        with col4:
            # 내용 힌트
            if st.button("내용 힌트", key="quiz_content_btn"):
                st.session_state.show_quiz_content = not st.session_state.show_quiz_content
                st.rerun()
        
        with col5:
            # 이미지 힌트
            if st.button("이미지 보기", key="quiz_image_btn"):
                st.session_state.show_quiz_image = not st.session_state.show_quiz_image
                st.rerun()
        
        # 힌트 표시 영역
        hint_displayed = False
        
        # 정의/개념 힌트
        if st.session_state.show_quiz_hint:
            hint_displayed = True
            with st.expander("정의/개념 힌트", expanded=True):
                st.markdown(f"**정의/개념:** {current_card['term']}")
        
        # 핵심키워드 힌트
        if st.session_state.show_quiz_keyword:
            hint_displayed = True
            with st.expander("핵심키워드 힌트", expanded=True):
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
        
        # 두음 힌트
        if st.session_state.show_quiz_rhyming:
            hint_displayed = True
            with st.expander("두음 힌트", expanded=True):
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
                
        # 내용 힌트
        if st.session_state.show_quiz_content:
            hint_displayed = True
            with st.expander("내용 힌트", expanded=True):
                st.markdown(current_card['card_data']['content'])
        
        # 사용자 답변 입력
        if not st.session_state.quiz_answer_checked:
            user_answer = st.text_area("답변", key="answer_input", height=100)
            if st.button("정답 확인"):
                st.session_state.user_answer = user_answer
                st.session_state.quiz_answer_checked = True
                st.rerun()
        else:
            st.text_area("답변", value=st.session_state.user_answer, disabled=True, height=100)
            
            # 정답 표시
            st.markdown("### 정답")
            # 정의/개념 정답
            st.markdown(f"**정의/개념:** {current_card['term']}")
            # 핵심키워드 정답
            st.markdown(f"**핵심키워드:** {current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.')}")
            # 내용 정답
            st.markdown(f"**내용:** {current_card['card_data']['content']}")
            
            # 자가 채점
            col1, col2 = st.columns(2)
            with col1:
                if st.button("맞았어요"):
                    st.session_state.quiz_score += 1
                    if st.session_state.current_quiz_index + 1 < st.session_state.quiz_total:
                        st.session_state.current_quiz_index += 1
                        st.session_state.quiz_answer_checked = False
                        st.session_state.show_quiz_hint = False
                        st.session_state.show_quiz_keyword = False
                        st.session_state.show_quiz_rhyming = False
                        st.session_state.show_quiz_content = False
                        st.session_state.show_quiz_image = False
                    else:
                        st.session_state.quiz_completed = True
                    st.rerun()
            
            with col2:
                if st.button("틀렸어요"):
                    if st.session_state.current_quiz_index + 1 < st.session_state.quiz_total:
                        st.session_state.current_quiz_index += 1
                        st.session_state.quiz_answer_checked = False
                        st.session_state.show_quiz_hint = False
                        st.session_state.show_quiz_keyword = False
                        st.session_state.show_quiz_rhyming = False
                        st.session_state.show_quiz_content = False
                        st.session_state.show_quiz_image = False
                    else:
                        st.session_state.quiz_completed = True
                    st.rerun()
    
    with image_col:
        # 이미지는 힌트 버튼을 누른 경우에만 표시
        if st.session_state.show_quiz_image:
            # 이미지 표시
            term = current_card['term']
            image_path = get_image_path(domain, current_card['topic'], term)
            if image_path:
                display_image(domain, current_card['topic'], term)
            else:
                st.info("이 카드에는 이미지가 없습니다.")

# 스크린샷 캡쳐 안내 함수
def capture_instruction():
    st.markdown("""
    <div style="border-left: 5px solid #4CAF50; padding: 15px; background-color: #f8f9fa; margin-bottom: 20px; border-radius: 4px;">
        <h4 style="margin-top: 0;">📷 화면 캡쳐 방법</h4>
        <p>1. 키보드에서 <strong>Windows + Shift + S</strong> 키를 눌러 윈도우 캡쳐 도구를 실행하세요.</p>
        <p>2. 캡쳐하려는 영역을 선택하세요.</p>
        <p>3. 캡쳐된 이미지는 클립보드에 저장됩니다.</p>
        <p>4. 이미지 편집 프로그램(그림판 등)을 열고 <strong>Ctrl + V</strong>로 붙여넣은 후 이미지를 저장하세요.</p>
        <p>5. 아래에서 저장한 이미지 파일을 업로드하세요.</p>
    </div>
    """, unsafe_allow_html=True)

# 도메인 목록 가져오는 함수 추가
def get_domains():
    data = load_data()
    return list(data.keys())

# 메인 함수
def main():
    st.set_page_config(
        page_title="정보관리기술사 암기장",
        page_icon="📚",
        layout="wide"
    )
    
    # 개발 디버그 모드
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    
    # 스타일 적용
    set_page_style()
    
    # 데이터 초기화
    initialize_data()
    
    # 사이드바
    mode, domain = sidebar()
    
    # 개발자 모드 토글 - 주석 처리하여 숨김
    # if st.sidebar.checkbox("개발자 모드", value=st.session_state.debug_mode):
    #     st.session_state.debug_mode = True
    # else:
    #     st.session_state.debug_mode = False
    
    # 선택된 모드에 따라 화면 표시
    if mode == "플래시카드 관리":
        manage_flashcards(domain)
    elif mode == "학습 모드":
        study_mode(domain)
    elif mode == "퀴즈 모드":
        quiz_mode(domain)
    elif mode == "전체 학습":
        all_domains_study_mode()
    elif mode == "전체 퀴즈":
        all_domains_quiz_mode()
    # 새로운 플래시카드 관리 인터페이스
    elif mode == "새 관리 인터페이스":
        st.title("플래시카드 관리")
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["카드 추가", "카드 수정/삭제", "데이터 관리"])
        
        with tab1:
            st.header("새 플래시카드 추가")
            
            # 도메인 선택
            all_domains = get_domains()
            domain = st.selectbox("도메인 선택", options=all_domains, key="add_domain_select")
            
            # 토픽 입력
            topic = st.text_input("토픽 입력", key="add_topic_input")
            
            # 정의/개념 입력
            term = st.text_area("정의/개념 입력", height=100, key="add_definition_input")
            
            # 특징 입력
            features = st.text_area("특징 입력 (각 항목을 새 줄로 구분)", height=100, key="add_features_input")
            
            # 내용 입력
            content = st.text_area("내용 입력 (각 항목을 새 줄로 구분)", height=150, key="add_content_input")
            
            # 키워드 입력
            keyword = st.text_input("키워드 입력 (쉼표로 구분)", key="add_keywords_input")
            
            # 연상법 입력
            rhyming = st.text_area("두음법 입력", height=100, key="add_mnemonic_input")
            
            # 일반 이미지 업로드
            uploaded_file = st.file_uploader("이미지 파일 업로드", type=["png", "jpg", "jpeg"], key="add_file_uploader")
            
            if st.button("카드 추가", key="add_card_button"):
                # 기본 검증
                if not topic:
                    st.error("토픽을 입력해주세요.")
                elif not term:
                    st.error("정의/개념을 입력해주세요.")
                elif not content:
                    st.error("내용을 입력해주세요.")
                else:
                    # 데이터 로드
                    data = load_data()
                    
                    # 도메인이 없으면 생성
                    if domain not in data:
                        data[domain] = {}
                    
                    # 토픽이 없으면 생성
                    if topic not in data[domain]:
                        data[domain][topic] = {}
                    
                    # 같은 토픽/용어 조합이 이미 존재하는지 확인
                    if term in data[domain][topic]:
                        st.error(f"'{topic}' 토픽에 '{term}' 정의/개념이 이미 존재합니다. 다른 이름을 사용하거나 기존 카드를 수정하세요.")
                    else:
                        # 주제, 특징, 내용을 포함하는 데이터 구조
                        card_data = {
                            "subject": term,
                            "keyword": keyword,
                            "rhyming": rhyming,
                            "content": content
                        }
                        
                        # 카드 데이터 저장
                        data[domain][topic][term] = card_data
                        save_data(data)
                        
                        # 이미지 저장 처리
                        image_saved = False
                        if uploaded_file:
                            try:
                                image_path = save_image(uploaded_file, domain, topic, term)
                                if image_path:
                                    image_saved = True
                            except Exception as e:
                                st.error(f"이미지 저장 중 오류 발생: {str(e)}")
                        
                        # 저장 성공 메시지
                        if image_saved:
                            st.success(f"'{term}' 플래시카드와 이미지가 '{topic}' 토픽에 추가되었습니다!")
                        else:
                            st.success(f"'{term}' 플래시카드가 '{topic}' 토픽에 추가되었습니다!")
                        
                        # 페이지 새로고침
                        time.sleep(1)
                        st.rerun()
    
    # 디버그 모드일 때 추가 정보 표시
    if st.session_state.debug_mode:
        st.sidebar.divider()
        st.sidebar.subheader("디버그 정보")
        st.sidebar.write(f"이미지 폴더 경로: {os.path.abspath(IMAGE_FOLDER)}")
        st.sidebar.write(f"임시 이미지 폴더 경로: {os.path.abspath(TEMP_IMAGE_FOLDER)}")
        
        # 이미지 폴더 내용 확인
        if os.path.exists(IMAGE_FOLDER):
            st.sidebar.write("이미지 폴더 내용:")
            for root, dirs, files in os.walk(IMAGE_FOLDER):
                if files:
                    st.sidebar.write(f"경로: {root}")
                    for file in files:
                        st.sidebar.write(f"- {file}")
                        
        # 세션 상태 확인
        st.sidebar.write("클립보드 이미지 상태:")
        st.sidebar.write(f"- 클립보드 이미지: {'있음' if st.session_state.get('clipboard_image') else '없음'}")
        st.sidebar.write(f"- 클립보드 이력: {len(st.session_state.get('clipboard_history', []))}개 항목")

if __name__ == "__main__":
    main() 