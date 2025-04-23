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
        background-color: #f8f9fa;
    }
    
    /* 헤더 스타일 */
    h1, h2, h3, h4 {
        font-family: 'Noto Sans KR', sans-serif;
        color: #1E3A8A;
    }
    
    /* 카드 스타일 */
    .card {
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        background-color: #4263EB;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #3b56d7;
        border-color: #3b56d7;
    }
    
    /* 파일 업로더 스타일 */
    .stFileUploader {
        border: 2px dashed #4263EB;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* 이미지 미리보기 컨테이너 */
    .preview-container {
        text-align: center;
        margin: 10px auto;
        padding: 10px;
        border-radius: 5px;
        background-color: #f1f3f9;
        max-height: 400px;
        overflow: auto;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f3f9;
        border-radius: 4px 4px 0px 0px;
        color: #4263EB;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4263EB;
        color: white;
    }
    
    /* 토픽 선택 스타일 */
    .topic-selector {
        background-color: white;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* 정의/개념 카드 스타일 */
    .concept-card {
        background-color: white;
        border-left: 5px solid #4263EB;
        padding: 15px;
        border-radius: 0 5px 5px 0;
        margin-bottom: 15px;
    }
    
    /* 클립보드 영역 스타일 */
    .clipboard-area {
        border: 2px dashed #4263EB;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    
    /* 이미지 업로드 내역 */
    .upload-history {
        margin-top: 10px;
        padding: 10px;
        background-color: #f1f3f9;
        border-radius: 5px;
        max-height: 150px;
        overflow-y: auto;
    }
    
    .upload-item {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# 클립보드 이미지 컴포넌트용 JavaScript 코드
def clipboard_component():
    clipboard_callback = """
    <script>
    const previewImage = (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                document.getElementById('preview-image').src = event.target.result;
                document.getElementById('preview-image').style.display = 'block';
                document.getElementById('preview-container').style.display = 'block';
                
                // 이미지 크기에 맞게 컨테이너 높이 조정
                const img = new Image();
                img.onload = function() {
                    const container = document.getElementById('preview-container');
                    const maxHeight = Math.min(400, img.height + 60); // 최대 높이는 400px 또는 이미지 높이+여백
                    container.style.height = maxHeight + 'px';
                };
                img.src = event.target.result;
            }
            reader.readAsDataURL(file);
        }
    }

    document.addEventListener('paste', function(e) {
        const clipboardData = e.clipboardData;
        const items = clipboardData.items;
        
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    // Base64 인코딩된 이미지 데이터
                    const base64data = event.target.result;
                    
                    // 이미지 미리보기 표시
                    const previewImage = document.getElementById('preview-image');
                    previewImage.src = base64data;
                    previewImage.style.display = 'block';
                    document.getElementById('preview-container').style.display = 'block';
                    
                    // 이미지 크기에 맞게 컨테이너 높이 조정
                    const img = new Image();
                    img.onload = function() {
                        const container = document.getElementById('preview-container');
                        const maxHeight = Math.min(400, img.height + 60); // 최대 높이는 400px 또는 이미지 높이+여백
                        container.style.height = maxHeight + 'px';
                    };
                    img.src = base64data;
                    
                    // Streamlit에 데이터 전송
                    const data = {
                        type: "clipboard_image",
                        image: base64data,
                        timestamp: new Date().toISOString()
                    };
                    window.parent.postMessage(JSON.stringify(data), "*");
                };
                
                reader.readAsDataURL(blob);
                break;
            }
        }
    });
    </script>
    
    <div class="clipboard-area">
        <p>여기에 <strong>Ctrl+V</strong>로 캡쳐한 이미지를 붙여넣으세요</p>
        <p style="font-size: 12px; color: #666;">또는 파일을 선택하세요</p>
        <input type="file" accept="image/*" onchange="previewImage(event)" style="margin-top: 10px;" />
    </div>
    
    <div id="preview-container" class="preview-container" style="display: none;">
        <h4>이미지 미리보기</h4>
        <img id="preview-image" style="max-width: 100%; display: none; border: 1px solid #ddd; border-radius: 4px;" />
    </div>
    """
    
    st.components.v1.html(clipboard_callback, height=550)
    
    # 클립보드 이미지 데이터 받기
    if "clipboard_image" not in st.session_state:
        st.session_state.clipboard_image = None
    if "clipboard_timestamp" not in st.session_state:
        st.session_state.clipboard_timestamp = None
    if "clipboard_history" not in st.session_state:
        st.session_state.clipboard_history = []
    
    # JavaScript에서 전송된 이미지 데이터를 받는 로직
    js_code = """
    <script>
    window.addEventListener('message', function(e) {
        try {
            const data = JSON.parse(e.data);
            if (data.type === 'clipboard_image') {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: {
                        image: data.image,
                        timestamp: data.timestamp
                    }
                }, '*');
            }
        } catch(err) {
            console.error('Error processing message:', err);
        }
    });
    </script>
    """
    st.components.v1.html(js_code, height=0)
    
    # 새 이미지가 클립보드에서 감지되면 임시 저장 및 이력에 추가
    current_image = st.session_state.clipboard_image
    current_timestamp = st.session_state.clipboard_timestamp
    
    # 컴포넌트 값이 변경되었는지 확인
    component_value = st.session_state.get("_component_value")
    if component_value and isinstance(component_value, dict) and "image" in component_value:
        new_image = component_value["image"]
        new_timestamp = component_value.get("timestamp")
        
        if new_image != current_image:
            # 새 이미지 저장
            st.session_state.clipboard_image = new_image
            st.session_state.clipboard_timestamp = new_timestamp
            
            # 임시 파일로 저장
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clipboard_{timestamp}.png"
            filepath = os.path.join(TEMP_IMAGE_FOLDER, filename)
            
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
        return None
    
    # Base64 이미지 데이터에서 헤더 제거
    if ',' in base64_img:
        base64_img = base64_img.split(',')[1]
    
    # 도메인과 토픽 폴더 생성
    domain_folder = os.path.join(IMAGE_FOLDER, domain)
    if not os.path.exists(domain_folder):
        os.makedirs(domain_folder)
    
    topic_folder = os.path.join(domain_folder, topic)
    if not os.path.exists(topic_folder):
        os.makedirs(topic_folder)
    
    # 이미지 저장
    image_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(image_data))
    
    filename = f"{term}.png"
    file_path = os.path.join(topic_folder, filename)
    
    image.save(file_path, "PNG")
    return file_path

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
    # 도메인과 토픽 폴더 생성
    domain_folder = os.path.join(IMAGE_FOLDER, domain)
    if not os.path.exists(domain_folder):
        os.makedirs(domain_folder)
    
    topic_folder = os.path.join(domain_folder, topic)
    if not os.path.exists(topic_folder):
        os.makedirs(topic_folder)
    
    # 파일 확장자 가져오기
    file_ext = os.path.splitext(image_file.name)[1].lower()
    
    # 파일명 생성 (용어를 기반으로)
    filename = f"{term}{file_ext}"
    file_path = os.path.join(topic_folder, filename)
    
    # 이미지 저장
    with open(file_path, "wb") as f:
        f.write(image_file.getbuffer())
    
    return file_path

# 이미지 경로 가져오기
def get_image_path(domain, topic, term):
    # 가능한 이미지 확장자 목록
    extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    
    # 도메인과 토픽 폴더 경로
    topic_folder = os.path.join(IMAGE_FOLDER, domain, topic)
    
    # 해당 폴더가 없으면 None 반환
    if not os.path.exists(topic_folder):
        return None
    
    # 각 확장자에 대해 파일 존재 여부 확인
    for ext in extensions:
        file_path = os.path.join(topic_folder, f"{term}{ext}")
        if os.path.exists(file_path):
            return file_path
    
    return None

# 이미지 표시 함수
def display_image(domain, topic, term):
    image_path = get_image_path(domain, topic, term)
    if image_path:
        try:
            image = Image.open(image_path)
            st.image(image, caption=f"{topic} 이미지", use_container_width=True)
        except Exception as e:
            st.error(f"이미지를 표시할 수 없습니다: {e}")

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
    
    # 모드 선택
    current_mode = st.session_state.mode
    
    # 모드가 전체 학습 또는 전체 퀴즈인 경우 라디오 버튼에서는 기본 모드로 표시
    display_mode = current_mode if current_mode in ["플래시카드 관리", "학습 모드", "퀴즈 모드"] else "플래시카드 관리"
    
    mode = st.sidebar.radio("모드 선택", ["플래시카드 관리", "학습 모드", "퀴즈 모드"], index=["플래시카드 관리", "학습 모드", "퀴즈 모드"].index(display_mode))
    
    # 일반 모드를 선택한 경우에만 모드 변경 (전체 모드 선택 중에는 라디오 버튼을 통한 변경 제한)
    if mode != current_mode and current_mode not in ["전체 학습", "전체 퀴즈"]:
        st.session_state.mode = mode
    elif mode != display_mode and current_mode in ["전체 학습", "전체 퀴즈"]:
        st.session_state.mode = mode
    
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
    
    st.sidebar.divider()
    
    # 전체 도메인 학습/퀴즈 기능
    st.sidebar.subheader("모든 도메인 학습/퀴즈")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("전체 도메인 토픽 학습", key="all_domain_study", help="모든 도메인의 토픽을 학습합니다."):
            st.session_state.mode = "전체 학습"
            st.rerun()
    
    with col2:
        if st.button("전체 도메인 토픽 퀴즈", key="all_domain_quiz", help="모든 도메인의 토픽으로 퀴즈를 풉니다."):
            st.session_state.mode = "전체 퀴즈"
            st.rerun()
    
    st.sidebar.divider()
    
    # 현재 모드가 전체 모드인 경우 알림 표시
    if st.session_state.mode == "전체 학습":
        st.sidebar.info("현재 '전체 도메인 토픽 학습' 모드입니다. 일반 모드로 돌아가려면 상단의 모드를 선택하세요.")
    elif st.session_state.mode == "전체 퀴즈":
        st.sidebar.info("현재 '전체 도메인 토픽 퀴즈' 모드입니다. 일반 모드로 돌아가려면 상단의 모드를 선택하세요.")
    
    # 모드와 도메인 반환
    return st.session_state.mode, st.session_state.selected_domain

# 플래시카드 관리 화면
def manage_flashcards(domain):
    st.header(f"{domain} - 플래시카드 관리")
    
    data = load_data()
    topics = data[domain]
    
    # 새 토픽/카드 추가
    with st.expander("새 플래시카드 추가", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            topics_list = list(topics.keys())
            if topics_list:
                selected_topic = st.selectbox("기존 토픽 선택", ["새 토픽 생성"] + topics_list)
            else:
                selected_topic = "새 토픽 생성"
        
        topic_name = ""
        with col2:
            if selected_topic == "새 토픽 생성":
                topic_name = st.text_input("새 토픽 이름")
            else:
                topic_name = selected_topic
        
        term = st.text_input("정의/개념")
        keyword = st.text_input("핵심키워드")
        rhyming = st.text_input("두음")
        content = st.text_area("내용")
        
        # 이미지 업로드 방식 선택 (파일 업로드 / 화면 캡쳐)
        image_upload_method = st.radio("이미지 추가 방식 선택", ["파일 업로드", "화면 캡쳐", "없음"], horizontal=True)
        
        image_file = None
        screenshot_file = None
        clipboard_image = None
        
        if image_upload_method == "파일 업로드":
            # 파일 업로더 표시
            image_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg", "gif"])
        elif image_upload_method == "화면 캡쳐":
            # 화면 캡쳐 컴포넌트 표시
            st.write("윈도우 화면 캡쳐(Win+Shift+S) 후 아래 영역에 붙여넣기(Ctrl+V)하세요.")
            
            # 클립보드 이미지 컴포넌트 사용
            clipboard_image = clipboard_component()
            
            # 붙여넣기 이력 표시
            show_clipboard_history()
            
            if clipboard_image:
                st.success("이미지가 붙여넣기 되었습니다! 아래 버튼을 클릭하여 플래시카드를 저장하세요.")
        
        if st.button("플래시카드 추가") and topic_name and term and content:
            if topic_name not in topics:
                topics[topic_name] = {}
            
            # 주제, 특징, 내용을 포함하는 데이터 구조
            card_data = {
                "subject": term,
                "keyword": keyword,
                "rhyming": rhyming,
                "content": content
            }
            
            topics[topic_name][term] = card_data
            save_data(data)
            
            # 이미지 저장 처리
            if image_upload_method == "파일 업로드" and image_file:
                save_image(image_file, domain, topic_name, term)
                st.success(f"'{term}' 플래시카드와 이미지가 '{topic_name}' 토픽에 추가되었습니다!")
            elif image_upload_method == "화면 캡쳐" and clipboard_image:
                # 클립보드 이미지 저장
                save_clipboard_image(clipboard_image, domain, topic_name, term)
                st.success(f"'{term}' 플래시카드와 붙여넣은 이미지가 '{topic_name}' 토픽에 추가되었습니다!")
            else:
                st.success(f"'{term}' 플래시카드가 '{topic_name}' 토픽에 추가되었습니다!")
    
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
                    st.rerun()
                
                # 카드 목록
                for term, card_data in cards.items():
                    st.markdown("---")
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.markdown(f"**정의/개념:** {term}")
                        # 이미지 표시
                        image_path = get_image_path(domain, topic_name, term)
                        if image_path:
                            st.image(image_path, caption=f"{topic_name} 이미지", width=200)
                            
                            # 이미지 삭제 버튼
                            if st.button("이미지 삭제", key=f"del_img_{topic_name}_{term}", type="secondary"):
                                if delete_image(domain, topic_name, term):
                                    st.success("이미지가 삭제되었습니다!")
                                    st.rerun()
                            
                            # 이미지 업데이트 기능 (expander 사용하지 않음)
                            st.markdown("#### 이미지 업데이트")
                            update_method = st.radio(f"이미지 업데이트 방식 ({term})",
                                                   ["파일 업로드", "화면 캡쳐"],
                                                   key=f"update_method_{topic_name}_{term}",
                                                   horizontal=True)
                            
                            if update_method == "파일 업로드":
                                new_image = st.file_uploader(f"새 이미지 ({term})", 
                                                        type=["png", "jpg", "jpeg", "gif"], 
                                                        key=f"update_img_{topic_name}_{term}")
                                if st.button("이미지 업데이트", key=f"update_img_btn_{topic_name}_{term}") and new_image:
                                    # 기존 이미지 삭제
                                    if os.path.exists(image_path):
                                        os.unlink(image_path)
                                    # 새 이미지 저장
                                    save_image(new_image, domain, topic_name, term)
                                    st.success("이미지가 업데이트되었습니다!")
                                    st.rerun()
                            else:  # 화면 캡쳐 방식
                                st.write("윈도우 화면 캡쳐 후 아래 영역에 붙여넣기(Ctrl+V)하세요.")
                                # 클립보드 이미지 컴포넌트 사용
                                clipboard_update_key = f"clipboard_update_{topic_name}_{term}"
                                if clipboard_update_key not in st.session_state:
                                    st.session_state[clipboard_update_key] = None
                                
                                clipboard_image = clipboard_component()
                                
                                if clipboard_image and clipboard_image != st.session_state[clipboard_update_key]:
                                    st.session_state[clipboard_update_key] = clipboard_image
                                    st.success("이미지가 붙여넣기 되었습니다!")
                                
                                if st.button("이미지 업데이트", key=f"update_clipboard_{topic_name}_{term}") and st.session_state[clipboard_update_key]:
                                    # 기존 이미지 삭제
                                    if os.path.exists(image_path):
                                        os.unlink(image_path)
                                    # 새 이미지 저장
                                    save_clipboard_image(st.session_state[clipboard_update_key], domain, topic_name, term)
                                    st.success("이미지가 업데이트되었습니다!")
                                    st.rerun()
                        else:
                            # 이미지 추가 기능 (expander 사용하지 않음)
                            st.markdown("#### 이미지 추가")
                            # 이미지 추가 방식 선택
                            img_add_method = st.radio(f"이미지 추가 방식 ({term})", 
                                                    ["파일 업로드", "화면 캡쳐"], 
                                                    key=f"img_method_{topic_name}_{term}", 
                                                    horizontal=True)
                            
                            if img_add_method == "파일 업로드":
                                new_image = st.file_uploader(f"이미지 ({term})", 
                                                          type=["png", "jpg", "jpeg", "gif"], 
                                                          key=f"add_img_{topic_name}_{term}")
                                if st.button("이미지 추가", key=f"add_img_btn_{topic_name}_{term}") and new_image:
                                    save_image(new_image, domain, topic_name, term)
                                    st.success("이미지가 추가되었습니다!")
                                    st.rerun()
                            else:  # 화면 캡쳐 방식
                                st.write("윈도우 화면 캡쳐 후 아래 영역에 붙여넣기(Ctrl+V)하세요.")
                                # 클립보드 이미지 컴포넌트 사용 (고유 키 추가)
                                clipboard_key = f"clipboard_{topic_name}_{term}"
                                if clipboard_key not in st.session_state:
                                    st.session_state[clipboard_key] = None
                                
                                clipboard_image = clipboard_component()
                                
                                if clipboard_image and clipboard_image != st.session_state[clipboard_key]:
                                    st.session_state[clipboard_key] = clipboard_image
                                    st.success("이미지가 붙여넣기 되었습니다!")
                                
                                if st.button("붙여넣은 이미지 저장", key=f"save_clipboard_{topic_name}_{term}") and st.session_state[clipboard_key]:
                                    save_clipboard_image(st.session_state[clipboard_key], domain, topic_name, term)
                                    st.success("이미지가 저장되었습니다!")
                                    st.rerun()
                    
                    with col2:
                        # 주제, 특징, 내용 표시
                        st.markdown(f"**핵심키워드:** {card_data.get('keyword', '')}")
                        st.markdown(f"**두음:** {card_data.get('rhyming', '')}")
                        st.markdown(f"**내용:**")
                        st.markdown(card_data["content"])
                        col_edit, col_del = st.columns(2)
                        with col_edit:
                            if st.button("수정", key=f"edit_{topic_name}_{term}"):
                                st.session_state.edit_term = term
                                st.session_state.edit_topic = topic_name
                                st.session_state.edit_card_data = card_data
                                st.rerun()
                        with col_del:
                            if st.button("삭제", key=f"del_{topic_name}_{term}"):
                                # 연결된 이미지 삭제
                                image_path = get_image_path(domain, topic_name, term)
                                if image_path and os.path.exists(image_path):
                                    os.unlink(image_path)
                                
                                del data[domain][topic_name][term]
                                if not data[domain][topic_name]:  # 토픽에 카드가 없으면 토픽도 삭제
                                    del data[domain][topic_name]
                                save_data(data)
                                st.success(f"'{term}' 카드가 삭제되었습니다!")
                                st.rerun()
    
    else:
        st.info(f"{domain} 도메인에 아직 플래시카드가 없습니다. 새 플래시카드를 추가해보세요!")

# 학습 모드 화면
def study_mode(domain):
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
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0
    if "study_show_content" not in st.session_state:
        st.session_state.study_show_content = False
    if "study_show_keyword" not in st.session_state:
        st.session_state.study_show_keyword = False
    if "study_show_rhyming" not in st.session_state:
        st.session_state.study_show_rhyming = False
    if "study_cards" not in st.session_state:
        st.session_state.study_cards = all_cards.copy()
    
    # 카드가 변경되었는지 확인
    current_cards_ids = [f"{card['topic']}_{card['term']}" for card in all_cards]
    session_cards_ids = [f"{card['topic']}_{card['term']}" for card in st.session_state.study_cards]
    
    if current_cards_ids != session_cards_ids:
        st.session_state.study_cards = all_cards.copy()
        st.session_state.current_card_index = 0
        st.session_state.study_show_content = False
        st.session_state.study_show_keyword = False
        st.session_state.study_show_rhyming = False
    
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
            
            # 핵심키워드 표시
            if st.button("핵심키워드 보기", key="study_keyword_btn"):
                st.session_state.study_show_keyword = not st.session_state.study_show_keyword
                st.rerun()
                
            if st.session_state.study_show_keyword:
                st.markdown("### 핵심키워드")
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
            
            # 두음 표시
            if st.button("두음 보기", key="study_rhyming_btn"):
                st.session_state.study_show_rhyming = not st.session_state.study_show_rhyming
                st.rerun()
                
            if st.session_state.study_show_rhyming:
                st.markdown("### 두음")
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
                
            # 내용 표시
            if st.button("내용 보기", key="study_content_btn"):
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
                st.image(image_path, caption=f"{current_card['topic']} 이미지", use_container_width=True)
            else:
                st.info("이 카드에는 이미지가 없습니다.")
        
        # 버튼 행
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("이전", key="prev_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index - 1) % len(st.session_state.study_cards)
                st.session_state.study_show_content = False
                st.session_state.study_show_keyword = False
                st.session_state.study_show_rhyming = False
                st.rerun()
        
        with col2:
            if st.button("모두 가리기", key="hide_all"):
                st.session_state.study_show_content = False
                st.session_state.study_show_keyword = False
                st.session_state.study_show_rhyming = False
                st.rerun()
        
        with col3:
            if st.button("다음", key="next_card"):
                st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(st.session_state.study_cards)
                st.session_state.study_show_content = False
                st.session_state.study_show_keyword = False
                st.session_state.study_show_rhyming = False
                st.rerun()
        
        # 셔플 버튼
        if st.button("카드 섞기", key="shuffle_cards"):
            random.shuffle(st.session_state.study_cards)
            st.session_state.current_card_index = 0
            st.session_state.study_show_content = False
            st.session_state.study_show_keyword = False
            st.session_state.study_show_rhyming = False
            st.rerun()

# 전체 도메인 학습 모드
def all_domains_study_mode():
    st.header("전체 도메인 학습 모드")
    
    # 세션 상태를 유지하여 키 충돌 방지
    if "all_study_initialized" not in st.session_state:
        st.session_state.all_study_initialized = True
        if "all_current_card_index" not in st.session_state:
            st.session_state.all_current_card_index = 0
        if "all_study_show_content" not in st.session_state:
            st.session_state.all_study_show_content = False
        if "all_study_show_keyword" not in st.session_state:
            st.session_state.all_study_show_keyword = False
        if "all_study_show_rhyming" not in st.session_state:
            st.session_state.all_study_show_rhyming = False
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
            
            # 핵심키워드 표시
            keyword_btn = st.button("핵심키워드 보기", key="all_study_keyword_btn")
            if keyword_btn:
                st.session_state.all_study_show_keyword = not st.session_state.all_study_show_keyword
                st.rerun()
                
            if st.session_state.all_study_show_keyword:
                st.markdown("### 핵심키워드")
                st.markdown(current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.'))
            
            # 두음 표시
            rhyming_btn = st.button("두음 보기", key="all_study_rhyming_btn")
            if rhyming_btn:
                st.session_state.all_study_show_rhyming = not st.session_state.all_study_show_rhyming
                st.rerun()
                
            if st.session_state.all_study_show_rhyming:
                st.markdown("### 두음")
                st.markdown(current_card['card_data'].get('rhyming', '두음 정보가 없습니다.'))
            
            # 내용 표시
            content_btn = st.button("내용 보기", key="all_study_content_btn")
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
                st.image(image_path, caption=f"{topic} 이미지", use_container_width=True)
            else:
                st.info("이 카드에는 이미지가 없습니다.")
        
        # 버튼 행
        col1, col2, col3 = st.columns(3)
        
        with col1:
            prev_btn = st.button("이전", key="all_prev_card")
            if prev_btn:
                st.session_state.all_current_card_index = (st.session_state.all_current_card_index - 1) % len(st.session_state.all_study_cards)
                st.session_state.all_study_show_content = False
                st.session_state.all_study_show_keyword = False
                st.session_state.all_study_show_rhyming = False
                st.rerun()
        
        with col2:
            hide_btn = st.button("모두 가리기", key="all_hide_all")
            if hide_btn:
                st.session_state.all_study_show_content = False
                st.session_state.all_study_show_keyword = False
                st.session_state.all_study_show_rhyming = False
                st.rerun()
        
        with col3:
            next_btn = st.button("다음", key="all_next_card")
            if next_btn:
                st.session_state.all_current_card_index = (st.session_state.all_current_card_index + 1) % len(st.session_state.all_study_cards)
                st.session_state.all_study_show_content = False
                st.session_state.all_study_show_keyword = False
                st.session_state.all_study_show_rhyming = False
                st.rerun()
        
        # 셔플 버튼
        shuffle_btn = st.button("카드 섞기", key="all_shuffle_cards")
        if shuffle_btn:
            shuffled_cards = st.session_state.all_study_cards.copy()
            random.shuffle(shuffled_cards)
            st.session_state.all_study_cards = shuffled_cards
            st.session_state.all_current_card_index = 0
            st.session_state.all_study_show_content = False
            st.session_state.all_study_show_keyword = False
            st.session_state.all_study_show_rhyming = False
            st.rerun()

# 전체 도메인 퀴즈 모드
def all_domains_quiz_mode():
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
                st.image(image_path, caption=f"{topic} 이미지", use_container_width=True)
            else:
                st.info("이 카드에는 이미지가 없습니다.")

# 퀴즈 모드 화면
def quiz_mode(domain):
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
                st.image(image_path, caption=f"{current_card['topic']} 이미지", use_container_width=True)
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

# 메인 함수
def main():
    st.set_page_config(
        page_title="정보관리기술사 암기장",
        page_icon="📚",
        layout="wide"
    )
    
    # 스타일 적용
    set_page_style()
    
    # 데이터 초기화
    initialize_data()
    
    # 사이드바
    mode, domain = sidebar()
    
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

if __name__ == "__main__":
    main() 