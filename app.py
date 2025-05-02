import streamlit as st
import os
import json
import time
import base64
import datetime
import traceback
from PIL import Image
import io
import hashlib
import re
import uuid
import pandas as pd
import numpy as np
import random

# 파일 경로 설정
BASE_FOLDER = "flashcard_data"
USERS_FOLDER = os.path.join(BASE_FOLDER, "users")
USER_DATA_FILE = os.path.join(USERS_FOLDER, "users.json")
TEMP_IMAGE_FOLDER = os.path.join(BASE_FOLDER, "temp_images")

# 사용자별 데이터/이미지 폴더 경로 지정 함수
def get_user_data_folder(username):
    return os.path.join(USERS_FOLDER, username, "data")

def get_user_image_folder(username):
    return os.path.join(USERS_FOLDER, username, "images")

def get_user_data_file(username):
    return os.path.join(get_user_data_folder(username), "flashcards.json")

# 폴더 초기화 함수
def initialize_folders():
    # 기본 폴더 생성
    os.makedirs(BASE_FOLDER, exist_ok=True)
    os.makedirs(USERS_FOLDER, exist_ok=True)
    os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)
    
    # 사용자 데이터 파일 생성
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# 사용자 인증 함수들
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(name, affiliation, username, password):
    initialize_folders()
    
    # 사용자 데이터 로드
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}
    
    # 이미 존재하는 사용자인지 확인
    if username in users:
        return False, "이미 사용 중인 아이디입니다."
    
    # 사용자 정보 저장
    users[username] = {
        "name": name,
        "affiliation": affiliation,
        "password_hash": hash_password(password),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 사용자 정보 저장
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    # 사용자 데이터 폴더 생성
    os.makedirs(get_user_data_folder(username), exist_ok=True)
    os.makedirs(get_user_image_folder(username), exist_ok=True)
    
    # 기본 플래시카드 데이터 생성
    initialize_user_data(username)
    
    return True, "회원가입이 완료되었습니다."

def verify_user(username, password):
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        if username not in users:
            return False, "존재하지 않는 아이디입니다."
        
        if users[username]["password_hash"] != hash_password(password):
            return False, "비밀번호가 일치하지 않습니다."
        
        return True, "로그인 성공"
    except Exception as e:
        return False, f"로그인 중 오류가 발생했습니다: {str(e)}"

def find_user_id(name):
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        found_users = []
        for username, user_data in users.items():
            if user_data["name"] == name:
                found_users.append(username)
        
        if not found_users:
            return False, "해당 이름으로 등록된 아이디가 없습니다."
        
        return True, found_users
    except Exception as e:
        return False, f"아이디 찾기 중 오류가 발생했습니다: {str(e)}"

def reset_password(name, username):
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        if username not in users:
            return False, "존재하지 않는 아이디입니다."
        
        if users[username]["name"] != name:
            return False, "이름과 아이디가 일치하지 않습니다."
        
        # 임시 비밀번호 생성
        temp_password = str(uuid.uuid4())[:8]
        users[username]["password_hash"] = hash_password(temp_password)
        
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return True, temp_password
    except Exception as e:
        return False, f"비밀번호 재설정 중 오류가 발생했습니다: {str(e)}"

def change_password(name, username, current_password, new_password):
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        if username not in users:
            return False, "존재하지 않는 아이디입니다."
        
        if users[username]["name"] != name:
            return False, "이름과 아이디가 일치하지 않습니다."
        
        if users[username]["password_hash"] != hash_password(current_password):
            return False, "현재 비밀번호가 일치하지 않습니다."
        
        users[username]["password_hash"] = hash_password(new_password)
        
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        return True, "비밀번호가 성공적으로 변경되었습니다."
    except Exception as e:
        return False, f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"

def delete_user(username, password):
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        
        if username not in users:
            return False, "존재하지 않는 아이디입니다."
        
        if users[username]["password_hash"] != hash_password(password):
            return False, "비밀번호가 일치하지 않습니다."
        
        # 사용자 정보 삭제
        del users[username]
        
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        # 사용자 데이터 폴더 삭제 (옵션)
        # import shutil
        # shutil.rmtree(os.path.join(USERS_FOLDER, username))
        
        return True, "회원 탈퇴가 완료되었습니다."
    except Exception as e:
        return False, f"회원 탈퇴 중 오류가 발생했습니다: {str(e)}"

# 사용자별 데이터 초기화
def initialize_user_data(username):
    user_data_file = get_user_data_file(username)
    
    if not os.path.exists(user_data_file):
        domains = [
            "SW공학", "SW테스트", "IT경영/전력", "DB", 
            "빅데이터분석", "인공지능", "보안", "신기술", "법/제도"
        ]
        data = {domain: {} for domain in domains}
        
        # 사용자 데이터 저장
        os.makedirs(os.path.dirname(user_data_file), exist_ok=True)
        with open(user_data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    return load_user_data(username)

# 사용자 데이터 불러오기
def load_user_data(username):
    user_data_file = get_user_data_file(username)
    
    try:
        with open(user_data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return initialize_user_data(username)

# 사용자 데이터 저장
def save_user_data(username, data):
    user_data_file = get_user_data_file(username)
    os.makedirs(os.path.dirname(user_data_file), exist_ok=True)
    
    with open(user_data_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 기존 함수들 수정 (사용자별 데이터 처리)
def save_image(image_file, domain, topic, term):
    try:
        # 현재 로그인한 사용자 확인
        if 'username' not in st.session_state:
            st.error("로그인이 필요합니다.")
            return None
        
        username = st.session_state.username
        
        # 윈도우 파일 시스템에서 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_domain = ''.join(c for c in domain if c not in '\\/:*?"<>|')
        safe_topic = ''.join(c for c in topic if c not in '\\/:*?"<>|')
        
        # 사용자별 이미지 폴더와 도메인, 토픽 폴더 생성
        user_image_folder = get_user_image_folder(username)
        
        domain_folder = os.path.join(user_image_folder, safe_domain)
        if not os.path.exists(domain_folder):
            os.makedirs(domain_folder)
        
        topic_folder = os.path.join(domain_folder, safe_topic)
        if not os.path.exists(topic_folder):
            os.makedirs(topic_folder)
        
        # 이하 기존 코드와 동일
        # 파일 확장자 가져오기
        file_ext = os.path.splitext(image_file.name)[1].lower()
        if not file_ext:
            file_ext = '.png'  # 확장자가 없는 경우 기본값 설정
        
        # 윈도우 파일 이름으로 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_term = ''.join(c for c in term if c not in '\\/:*?"<>|')
        
        # 현재 타임스탬프 가져오기
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 현재 이미지 개수 확인하여 순번 지정
        image_count = 1
        # 같은 토픽과 타임스탬프를 가진 파일들 찾기
        for file_name in os.listdir(topic_folder):
            if os.path.isfile(os.path.join(topic_folder, file_name)) and safe_topic in file_name and timestamp in file_name:
                image_count += 1
        
        # 파일명 생성 (토픽 이름_타임스탬프_순번.확장자 형식)
        filename = f"{safe_topic}_{timestamp}_{image_count}{file_ext}"
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

# 이미지 경로 가져오기 (단일 이미지 - 이전 버전과의 호환성 유지)
def get_image_path(domain, topic, term):
    image_paths = get_all_image_paths(domain, topic, term)
    if image_paths and len(image_paths) > 0:
        return image_paths[0]  # 첫 번째 이미지만 반환
    return None

# 모든 이미지 경로 가져오기 (다중 이미지)
def get_all_image_paths(domain, topic, term):
    try:
        # 현재 로그인한 사용자 확인
        if 'username' not in st.session_state:
            return []
        
        username = st.session_state.username
        
        # 윈도우 파일 시스템에서 사용할 수 없는 문자 제거 (\ / : * ? " < > |)
        safe_domain = ''.join(c for c in domain if c not in '\\/:*?"<>|')
        safe_topic = ''.join(c for c in topic if c not in '\\/:*?"<>|')
        safe_term = ''.join(c for c in term if c not in '\\/:*?"<>|')
        
        # 사용자별 이미지 폴더와 도메인, 토픽 폴더 경로
        user_image_folder = get_user_image_folder(username)
        topic_folder = os.path.join(user_image_folder, safe_domain, safe_topic)
        
        # 이하 기존 코드와 동일
        # 해당 폴더가 없으면 빈 리스트 반환
        if not os.path.exists(topic_folder):
            return []
        
        # 이미지 파일 목록 저장할 리스트
        image_paths = []
        
        # 폴더 내 모든 파일 검색
        for file_name in os.listdir(topic_folder):
            file_path = os.path.join(topic_folder, file_name)
            if os.path.isfile(file_path):
                # 이미지 파일 확장자인지 확인
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    # 새 형식(토픽명_타임스탬프_순번) 또는 기존 형식(용어명)
                    # 특정 토픽과 관련된 모든 이미지 포함
                    image_paths.append((file_path, file_name))
        
        # 이하 기존 코드와 동일
        # 파일명에서 타임스탬프와 순번을 추출하여 정렬
        def sort_key(item):
            file_path, file_name = item
            
            # 새 형식: 토픽명_타임스탬프_순번.확장자
            # 타임스탬프와 순번으로 정렬
            import re
            match = re.search(r'_(\d{8}_\d{6})_(\d+)', file_name)
            if match:
                timestamp = match.group(1)
                number = int(match.group(2))
                # 순번을 먼저, 타임스탬프를 나중에 정렬 기준으로 사용
                return (number, timestamp)
            
            # 기존 형식: 파일 수정 시간으로 정렬
            try:
                file_time = os.path.getmtime(file_path)
                return (99999, str(file_time))  # 기존 파일은 뒤로 정렬
            except:
                return (99999, "0")
        
        # 순번 기준으로 정렬 (오름차순)
        image_paths.sort(key=sort_key)
        
        # 경로만 반환
        return [path for path, _ in image_paths]
    except Exception as e:
        st.error(f"이미지 경로 검색 중 오류 발생: {str(e)}")
        return []

# 기존 초기화 함수 수정
def initialize_data():
    # 세션 상태 초기화
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # 폴더 초기화
    initialize_folders()
    
    # 로그인한 경우 해당 사용자의 데이터 초기화
    if st.session_state.logged_in and st.session_state.username:
        return initialize_user_data(st.session_state.username)
    
    return None

# 기존 데이터 로드 함수 수정
def load_data():
    # 로그인한 경우 해당 사용자의 데이터 로드
    if st.session_state.logged_in and st.session_state.username:
        return load_user_data(st.session_state.username)
    
    # 로그인하지 않은 경우 빈 데이터 반환
    domains = [
        "SW공학", "SW테스트", "IT경영/전력", "DB", 
        "빅데이터분석", "인공지능", "보안", "신기술", "법/제도"
    ]
    return {domain: {} for domain in domains}

# 기존 데이터 저장 함수 수정
def save_data(data):
    # 로그인한 경우 해당 사용자의 데이터 저장
    if st.session_state.logged_in and st.session_state.username:
        save_user_data(st.session_state.username, data)

# 로그인 화면 표시 함수
def login_page():
    st.title("정보관리기술사 암기장")
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["로그인", "회원가입", "아이디 찾기", "비밀번호 재설정", "회원탈퇴"])
    
    # 로그인 탭
    with tab1:
        st.header("로그인")
        
        username = st.text_input("아이디", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        
        if st.button("로그인", key="login_button"):
            if not username or not password:
                st.error("아이디와 비밀번호를 모두 입력해주세요.")
            else:
                success, message = verify_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("로그인 성공! 잠시 후 메인 화면으로 이동합니다.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)
    
    # 회원가입 탭
    with tab2:
        st.header("회원가입")
        
        name = st.text_input("이름", key="signup_name")
        affiliation = st.text_input("소속", key="signup_affiliation")
        new_username = st.text_input("아이디", key="signup_username")
        new_password = st.text_input("비밀번호", type="password", key="signup_password")
        confirm_password = st.text_input("비밀번호 확인", type="password", key="signup_confirm_password")
        
        if st.button("회원가입", key="signup_button"):
            if not name or not affiliation or not new_username or not new_password:
                st.error("모든 필드를 입력해주세요.")
            elif new_password != confirm_password:
                st.error("비밀번호가 일치하지 않습니다.")
            else:
                success, message = save_user(name, affiliation, new_username, new_password)
                if success:
                    st.success(message)
                    time.sleep(1)
                    # 회원가입 후 자동 로그인
                    st.session_state.logged_in = True
                    st.session_state.username = new_username
                    st.rerun()
                else:
                    st.error(message)
    
    # 아이디 찾기 탭
    with tab3:
        st.header("아이디 찾기")
        
        find_name = st.text_input("이름", key="find_id_name")
        
        if st.button("아이디 찾기", key="find_id_button"):
            if not find_name:
                st.error("이름을 입력해주세요.")
            else:
                success, result = find_user_id(find_name)
                if success:
                    st.success(f"찾은 아이디: {', '.join(result)}")
                else:
                    st.error(result)
    
    # 비밀번호 재설정 탭
    with tab4:
        st.header("비밀번호 재설정")
        
        # 서브탭 생성
        pw_tab1, pw_tab2 = st.tabs(["임시 비밀번호 발급", "비밀번호 변경"])
        
        # 임시 비밀번호 발급 탭
        with pw_tab1:
            reset_name = st.text_input("이름", key="reset_pw_name")
            reset_username = st.text_input("아이디", key="reset_pw_username")
            
            if st.button("임시 비밀번호 발급", key="reset_pw_button"):
                if not reset_name or not reset_username:
                    st.error("이름과 아이디를 모두 입력해주세요.")
                else:
                    success, result = reset_password(reset_name, reset_username)
                    if success:
                        st.success(f"임시 비밀번호: {result}")
                    else:
                        st.error(result)
        
        # 비밀번호 변경 탭
        with pw_tab2:
            change_name = st.text_input("이름", key="change_pw_name")
            change_username = st.text_input("아이디", key="change_pw_username")
            current_password = st.text_input("현재 비밀번호", type="password", key="current_pw")
            new_pw = st.text_input("새 비밀번호", type="password", key="new_pw")
            confirm_new_pw = st.text_input("새 비밀번호 확인", type="password", key="confirm_new_pw")
            
            if st.button("비밀번호 변경", key="change_pw_button"):
                if not change_name or not change_username or not current_password or not new_pw or not confirm_new_pw:
                    st.error("모든 필드를 입력해주세요.")
                elif new_pw != confirm_new_pw:
                    st.error("새 비밀번호가 일치하지 않습니다.")
                else:
                    success, message = change_password(change_name, change_username, current_password, new_pw)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    # 회원탈퇴 탭
    with tab5:
        st.header("회원탈퇴")
        
        del_username = st.text_input("아이디", key="del_username")
        del_password = st.text_input("비밀번호", type="password", key="del_password")
        
        if st.button("회원탈퇴", key="delete_user_button"):
            if not del_username or not del_password:
                st.error("아이디와 비밀번호를 모두 입력해주세요.")
            else:
                success, message = delete_user(del_username, del_password)
                if success:
                    st.success(message)
                    # 로그아웃
                    if st.session_state.logged_in and st.session_state.username == del_username:
                        st.session_state.logged_in = False
                        st.session_state.username = None
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error(message)

# 사이드바 구성
def sidebar():
    st.sidebar.title("정보관리기술사 암기장")
    
    # 로그인한 사용자 정보 표시
    if st.session_state.logged_in and st.session_state.username:
        st.sidebar.success(f"{st.session_state.username}님 환영합니다!")
        if st.sidebar.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
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
        # 퀴즈 모드에서 이미지가 처음에 보이지 않도록 설정
        st.session_state.show_quiz_image = False
        st.rerun()
    
    st.sidebar.divider()
    
    # 전체 도메인 모드 선택
    st.sidebar.subheader("전체 도메인 모드")
    
    if st.sidebar.button("전체 도메인 토픽 학습", type="primary" if st.session_state.mode == "전체 학습" else "secondary", use_container_width=True):
        st.session_state.mode = "전체 학습"
        st.rerun()
    
    if st.sidebar.button("전체 도메인 토픽 퀴즈", type="primary" if st.session_state.mode == "전체 퀴즈" else "secondary", use_container_width=True):
        st.session_state.mode = "전체 퀴즈"
        # 전체 도메인 퀴즈 모드에서 이미지가 처음에 보이지 않도록 설정
        st.session_state.all_show_quiz_image = False
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
    
    # 도메인 관리 섹션
    st.sidebar.subheader("도메인 관리")
    
    # 새 도메인 추가
    with st.sidebar.expander("새 도메인 추가"):
        # 도메인 추가 성공 플래그 확인
        if "domain_add_success" not in st.session_state:
            st.session_state.domain_add_success = False
            
        # 성공 후 초기화를 위한 키 관리
        if "domain_add_counter" not in st.session_state:
            st.session_state.domain_add_counter = 0
            
        # 성공 후 다음 렌더링에서 입력창 초기화를 위해 키를 변경
        if st.session_state.domain_add_success:
            st.session_state.domain_add_counter += 1
            st.session_state.domain_add_success = False
            
        new_domain = st.text_input("새 도메인 이름", key=f"new_domain_input_{st.session_state.domain_add_counter}")
        
        if st.button("도메인 추가") and new_domain and new_domain not in domains:
            data[new_domain] = {}
            save_data(data)
            st.success(f"'{new_domain}' 도메인이 추가되었습니다!")
            # 성공 플래그 설정
            st.session_state.domain_add_success = True
            st.rerun()
    
    # 도메인 수정
    with st.sidebar.expander("도메인 이름 수정"):
        if domains:
            # 도메인 수정 성공 플래그 확인
            if "domain_edit_success" not in st.session_state:
                st.session_state.domain_edit_success = False
                
            # 성공 후 초기화를 위한 키 관리
            if "domain_edit_counter" not in st.session_state:
                st.session_state.domain_edit_counter = 0
                
            # 성공 후 다음 렌더링에서 입력창 초기화를 위해 키를 변경
            if st.session_state.domain_edit_success:
                st.session_state.domain_edit_counter += 1
                st.session_state.domain_edit_success = False
            
            domain_to_edit = st.selectbox("수정할 도메인 선택", domains, key=f"edit_domain_select_{st.session_state.domain_edit_counter}")
            new_domain_name = st.text_input("새 도메인 이름", key=f"edit_domain_name_{st.session_state.domain_edit_counter}")
            
            # 버튼을 한 번만 선언하고 결과를 변수에 저장
            edit_button_clicked = st.button("도메인 이름 수정", key=f"edit_domain_button_{st.session_state.domain_edit_counter}")
            
            # 버튼이 클릭되었고 새 도메인 이름이 입력된 경우
            if edit_button_clicked and new_domain_name:
                # 유효성 검사
                if domain_to_edit == new_domain_name:
                    st.warning("새 도메인 이름이 기존 이름과 동일합니다. 다른 이름을 사용하세요.")
                elif new_domain_name in domains:
                    st.error(f"'{new_domain_name}' 도메인이 이미 존재합니다. 다른 이름을 사용하세요.")
                else:
                    # 도메인 이름 변경
                    data[new_domain_name] = data[domain_to_edit]
                    del data[domain_to_edit]
                    save_data(data)
                    
                    # 이미지 폴더 이름도 변경 (사용자별 폴더 경로 사용)
                    if st.session_state.username:
                        old_folder = os.path.join(get_user_image_folder(st.session_state.username), domain_to_edit)
                        new_folder = os.path.join(get_user_image_folder(st.session_state.username), new_domain_name)
                        
                        if os.path.exists(old_folder):
                            try:
                                # 새 폴더가 이미 존재하면 병합, 아니면 이름 변경
                                if os.path.exists(new_folder):
                                    import shutil
                                    # 파일 복사
                                    for item in os.listdir(old_folder):
                                        s = os.path.join(old_folder, item)
                                        d = os.path.join(new_folder, item)
                                        if os.path.isdir(s):
                                            if not os.path.exists(d):
                                                shutil.copytree(s, d)
                                        else:
                                            shutil.copy2(s, d)
                                    # 기존 폴더 삭제
                                    shutil.rmtree(old_folder)
                                else:
                                    # 단순 이름 변경
                                    os.rename(old_folder, new_folder)
                            except Exception as e:
                                st.error(f"폴더 이름 변경 중 오류 발생: {str(e)}")
                    
                    # 세션 상태의 선택된 도메인도 업데이트
                    if st.session_state.selected_domain == domain_to_edit:
                        st.session_state.selected_domain = new_domain_name
                    
                    # 성공 플래그 설정
                    st.session_state.domain_edit_success = True
                    
                    st.success(f"'{domain_to_edit}'이(가) '{new_domain_name}'으로 변경되었습니다!")
                    st.rerun()
            elif edit_button_clicked and not new_domain_name:
                st.warning("새 도메인 이름을 입력해주세요.")
        else:
            st.info("수정할 도메인이 없습니다.")
    
    # 도메인 삭제
    with st.sidebar.expander("도메인 삭제"):
        if domains:
            # 도메인 삭제 성공 플래그 확인
            if "domain_delete_success" not in st.session_state:
                st.session_state.domain_delete_success = False
                
            # 성공 후 초기화를 위한 키 관리
            if "domain_delete_counter" not in st.session_state:
                st.session_state.domain_delete_counter = 0
                
            # 성공 후 다음 렌더링에서 입력창 초기화를 위해 키를 변경
            if st.session_state.domain_delete_success:
                st.session_state.domain_delete_counter += 1
                st.session_state.domain_delete_success = False
            
            domain_to_delete = st.selectbox("삭제할 도메인 선택", domains, key=f"delete_domain_select_{st.session_state.domain_delete_counter}")
            
            # 직접 삭제 버튼으로 변경
            delete_button = st.button("도메인 삭제", type="secondary", key=f"delete_domain_button_{st.session_state.domain_delete_counter}")
            if delete_button and domain_to_delete:
                # 도메인 삭제 로직
                # 확인 대화상자 대신 직접 삭제 처리
                try:
                    # 데이터에서 도메인 삭제
                    del data[domain_to_delete]
                    save_data(data)
                    
                    # 이미지 폴더도 삭제 (사용자별 폴더 경로 사용)
                    if st.session_state.username:
                        domain_folder = os.path.join(get_user_image_folder(st.session_state.username), domain_to_delete)
                        if os.path.exists(domain_folder):
                            try:
                                import shutil
                                shutil.rmtree(domain_folder)
                            except Exception as e:
                                st.error(f"도메인 폴더 삭제 중 오류 발생: {str(e)}")
                    
                    # 세션 상태의 선택된 도메인도 업데이트
                    if st.session_state.selected_domain == domain_to_delete:
                        remaining_domains = list(data.keys())
                        st.session_state.selected_domain = remaining_domains[0] if remaining_domains else None
                    
                    # 성공 플래그 설정
                    st.session_state.domain_delete_success = True
                    
                    st.success(f"'{domain_to_delete}' 도메인이 삭제되었습니다!")
                    # 페이지 새로고침
                    st.rerun()
                except Exception as e:
                    st.error(f"도메인 삭제 중 오류 발생: {str(e)}")
        else:
            st.info("삭제할 도메인이 없습니다.")
    
    # 사이드바 하단에 만든이 정보 추가
    st.sidebar.divider()
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 10px; margin-top: 20px; background-color: #f0f7ff; border-radius: 8px; border-left: 4px solid #4263EB; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <p style="font-weight: bold; font-size: 1rem; margin-bottom: 5px; color: #1E3A8A;">만든이 : 유민형( Vibe Coding with Cursor AI )</p>
            <p style="font-size: 0.8rem; color: #4a5568;">© 2024-2025</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 모드와 도메인 반환
    return st.session_state.mode, st.session_state.selected_domain

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
    
    /* 로그인/회원가입 폼 스타일 */
    .login-form-container {
        background-color: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        margin: 20px 0;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 애니메이션 */
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
    
    .card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .flashcard-button {
        margin: 5px;
    }
    
    /* 이미지 팝업 스타일 */
    .image-container {
        cursor: pointer;
        transition: transform 0.3s;
    }
    .image-container:hover {
        transform: scale(1.02);
    }
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        overflow: auto;
    }
    .modal-content {
        margin: auto;
        display: block;
        max-width: 90%;
        max-height: 90%;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .close {
        position: absolute;
        top: 15px;
        right: 35px;
        color: #f1f1f1;
        font-size: 40px;
        font-weight: bold;
        cursor: pointer;
    }
    
    /* 이미지 팝업 스타일 */
    .clickable-image {
        cursor: pointer;
        transition: transform 0.3s ease;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .clickable-image:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    #imageModal {
        display: none;
        position: fixed;
        z-index: 9999;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.9);
        justify-content: center;
        align-items: center;
        overflow: auto;
    }
    
    #modalImage {
        max-width: 90%;
        max-height: 90vh;
        margin: auto;
        display: block;
    }
    
    .close-btn {
        position: absolute;
        top: 20px;
        right: 30px;
        color: white;
        font-size: 40px;
        font-weight: bold;
        cursor: pointer;
        z-index: 10000;
    }
    </style>
    
    <!-- 이미지 모달 팝업창 -->
    <div id="imageModal">
        <span class="close-btn">&times;</span>
        <img id="modalImage">
    </div>
    
    <script>
    // 이미지 클릭 시 모달 팝업 표시 함수
    function openImageModal(src) {
        var modal = document.getElementById('imageModal');
        var modalImg = document.getElementById('modalImage');
        
        modal.style.display = "flex";
        modalImg.src = src;
        
        // 스크롤 막기
        document.body.style.overflow = 'hidden';
    }
    
    // 문서 로드 완료 시 이벤트 리스너 설정
    document.addEventListener('DOMContentLoaded', function() {
        // 닫기 버튼 이벤트
        var closeBtn = document.getElementsByClassName('close-btn')[0];
        var modal = document.getElementById('imageModal');
        
        if (closeBtn) {
            closeBtn.onclick = function() {
                modal.style.display = "none";
                document.body.style.overflow = 'auto';
            }
        }
        
        // 모달 바깥 영역 클릭 시 닫기
        if (modal) {
            modal.onclick = function(event) {
                if (event.target === modal) {
                    modal.style.display = "none";
                    document.body.style.overflow = 'auto';
                }
            }
        }
        
        // ESC 키 누를 때 모달 닫기
        document.addEventListener('keydown', function(event) {
            if (event.key === "Escape" && modal.style.display === "flex") {
                modal.style.display = "none";
                document.body.style.overflow = 'auto';
            }
        });
    });
    </script>
    """, unsafe_allow_html=True)

# 메인 함수 수정
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
    
    # 로그인 상태 확인
    if not st.session_state.logged_in:
        # 로그인 페이지 표시
        login_page()
        
        with st.sidebar:
            # 사이드바 하단에 만든이 정보 추가
            st.sidebar.divider()
            st.sidebar.markdown(
                """
                <div style="text-align: center; padding: 10px; margin-top: 20px; background-color: #f0f7ff; border-radius: 8px; border-left: 4px solid #4263EB; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="font-weight: bold; font-size: 1rem; margin-bottom: 5px; color: #1E3A8A;">만든이 : 유민형( Vibe Coding with Cursor AI )</p>
                    <p style="font-size: 0.8rem; color: #4a5568;">© 2024-2025</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        # 사이드바
        mode, domain = sidebar()
        
        # 선택된 모드에 따라 화면 표시
        if mode == "플래시카드 관리":
            manage_flashcards(domain)
        elif mode == "학습 모드":
            study_mode(domain)
        elif mode == "퀴즈 모드":
            # 퀴즈 모드에서는 이미지가 기본적으로 보이지 않도록 설정
            if "show_quiz_image" not in st.session_state:
                st.session_state.show_quiz_image = False
            quiz_mode(domain)
        elif mode == "전체 학습":
            all_domains_study_mode()
        elif mode == "전체 퀴즈":
            # 전체 도메인 퀴즈 모드에서는 이미지가 기본적으로 보이지 않도록 설정
            if "all_show_quiz_image" not in st.session_state:
                st.session_state.all_show_quiz_image = False
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
            if st.session_state.username:
                user_image_folder = get_user_image_folder(st.session_state.username)
                user_data_folder = get_user_data_folder(st.session_state.username)
                st.sidebar.write(f"현재 사용자: {st.session_state.username}")
                st.sidebar.write(f"사용자 데이터 경로: {os.path.abspath(user_data_folder)}")
                st.sidebar.write(f"사용자 이미지 경로: {os.path.abspath(user_image_folder)}")
            st.sidebar.write(f"임시 이미지 폴더 경로: {os.path.abspath(TEMP_IMAGE_FOLDER)}")
            
            # 이미지 폴더 내용 확인
            if st.session_state.username and os.path.exists(user_image_folder):
                st.sidebar.write("이미지 폴더 내용:")
                for root, dirs, files in os.walk(user_image_folder):
                    if files:
                        st.sidebar.write(f"경로: {root}")
                        for file in files[:5]:  # 파일이 많을 경우 최대 5개만 표시
                            st.sidebar.write(f"- {file}")
                        if len(files) > 5:
                            st.sidebar.write(f"... 외 {len(files)-5}개 파일")
                            
            # 세션 상태 확인
            st.sidebar.write("클립보드 이미지 상태:")
            st.sidebar.write(f"- 클립보드 이미지: {'있음' if st.session_state.get('clipboard_image') else '없음'}")
            st.sidebar.write(f"- 클립보드 이력: {len(st.session_state.get('clipboard_history', []))}개 항목")

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
        # 플래시카드 추가 성공 플래그 확인
        if "flashcard_add_success" not in st.session_state:
            st.session_state.flashcard_add_success = False
            
        # 성공 후 초기화를 위한 키 관리
        if "flashcard_add_counter" not in st.session_state:
            st.session_state.flashcard_add_counter = 0
            
        # 성공 후 다음 렌더링에서 입력창 초기화를 위해 키를 변경
        if st.session_state.flashcard_add_success:
            st.session_state.flashcard_add_counter += 1
            st.session_state.flashcard_add_success = False
        
        # 새 토픽 입력
        topic_name = st.text_input("토픽 이름", key=f"new_topic_name_{st.session_state.flashcard_add_counter}")
        
        # 카드 정보 입력
        term = st.text_input("정의/개념", key=f"new_term_{st.session_state.flashcard_add_counter}")
        keyword = st.text_input("핵심키워드", key=f"new_keyword_{st.session_state.flashcard_add_counter}")
        rhyming = st.text_input("두음", key=f"new_rhyming_{st.session_state.flashcard_add_counter}")
        content = st.text_area("내용", key=f"new_content_{st.session_state.flashcard_add_counter}")
        
        # 이미지 업로드 (여러 이미지 가능)
        uploaded_images = st.file_uploader("이미지 업로드 (여러 이미지 선택 가능)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True, key=f"new_image_files_{st.session_state.flashcard_add_counter}")
        if uploaded_images:
            for img in uploaded_images:
                try:
                    # 이미지 파일을 바이트로 읽고 PIL Image로 변환
                    image_bytes = img.getvalue()
                    image = Image.open(io.BytesIO(image_bytes))
                    # 변환된 이미지를 표시
                    st.image(image, caption=f"업로드된 이미지: {img.name}")
                except Exception as e:
                    st.error(f"이미지 표시 중 오류 발생: {str(e)}")
        
        # 제출 버튼 - 폼이 제출되면 데이터 저장 후 페이지 새로고침
        if st.button("플래시카드 추가", key=f"add_flashcard_btn_{st.session_state.flashcard_add_counter}"):
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
                    images_saved = 0
                    
                    # 여러 이미지 저장
                    if uploaded_images:
                        for img in uploaded_images:
                            try:
                                image_path = save_image(img, domain, topic_name, term)
                                if image_path:
                                    images_saved += 1
                            except Exception as e:
                                st.error(f"이미지 저장 중 오류 발생: {str(e)}")
                    
                    # 저장 성공 메시지
                    if images_saved > 0:
                        st.success(f"'{term}' 플래시카드와 {images_saved}개의 이미지가 '{topic_name}' 토픽에 추가되었습니다!")
                    else:
                        st.success(f"'{term}' 플래시카드가 '{topic_name}' 토픽에 추가되었습니다!")
                    
                    # 성공 플래그 설정
                    st.session_state.flashcard_add_success = True
                    
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
                    if st.session_state.username:
                        topic_folder = os.path.join(get_user_image_folder(st.session_state.username), domain, topic_name)
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
                        image_paths = get_all_image_paths(domain, topic_name, term)
                        if image_paths:
                            # 이미지 표시
                            for img_path in image_paths:
                                try:
                                    # 이미지를 base64로 인코딩하여 HTML로 표시
                                    with open(img_path, "rb") as img_file:
                                        encoded_img = base64.b64encode(img_file.read()).decode()
                                        st.markdown(f"""
                                        <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%"
                                            onclick="openImageModal(this.src)">
                                        """, unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"이미지 로드 중 오류: {str(e)}")
                            
                            # 이미지 삭제 버튼
                            if st.button("모든 이미지 삭제", key=f"del_img_{topic_name}_{term}", type="secondary"):
                                # 모든 이미지 삭제
                                deleted = 0
                                for img_path in image_paths:
                                    if os.path.exists(img_path):
                                        try:
                                            os.unlink(img_path)
                                            deleted += 1
                                        except Exception as e:
                                            st.error(f"이미지 삭제 중 오류 발생: {e}")
                                
                                if deleted > 0:
                                    st.success(f"{deleted}개 이미지가 삭제되었습니다!")
                                    time.sleep(1)
                                    st.rerun()
                            
                            # 이미지 업데이트
                            st.markdown("#### 이미지 추가")
                            additional_images = st.file_uploader("새 이미지 업로드 (여러 이미지 선택 가능)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True, key=f"update_images_{topic_name}_{term}")
                            if additional_images:
                                for img in additional_images:
                                    try:
                                        # 이미지 파일을 바이트로 읽고 PIL Image로 변환
                                        image_bytes = img.getvalue()
                                        image = Image.open(io.BytesIO(image_bytes))
                                        # 변환된 이미지를 표시
                                        st.image(image, caption=f"업로드할 이미지: {img.name}")
                                    except Exception as e:
                                        st.error(f"이미지 표시 중 오류 발생: {str(e)}")
                                
                                if st.button("이미지 추가", key=f"add_img_btn_{topic_name}_{term}"):
                                    images_saved = 0
                                    for img in additional_images:
                                        try:
                                            image_path = save_image(img, domain, topic_name, term)
                                            if image_path:
                                                images_saved += 1
                                        except Exception as e:
                                            st.error(f"이미지 추가 중 오류: {str(e)}")
                                            
                                    if images_saved > 0:
                                        st.success(f"{images_saved}개 이미지가 추가되었습니다!")
                                        time.sleep(1)
                                        st.rerun()
                        else:
                            # 이미지 추가 기능
                            st.markdown("#### 이미지 추가")
                            new_images = st.file_uploader(f"이미지 ({term}) - 여러 이미지 선택 가능", 
                                                      type=["png", "jpg", "jpeg", "gif"], 
                                                      accept_multiple_files=True,
                                                      key=f"add_img_{topic_name}_{term}")
                            if new_images:
                                for img in new_images:
                                    try:
                                        # 이미지 파일을 바이트로 읽고 PIL Image로 변환
                                        image_bytes = img.getvalue()
                                        image = Image.open(io.BytesIO(image_bytes))
                                        # 변환된 이미지를 표시
                                        st.image(image, caption=f"추가할 이미지: {img.name}")
                                    except Exception as e:
                                        st.error(f"이미지 표시 중 오류 발생: {str(e)}")
                                
                                if st.button("이미지 추가", key=f"add_img_btn_{topic_name}_{term}"):
                                    images_saved = 0
                                    for img in new_images:
                                        try:
                                            image_path = save_image(img, domain, topic_name, term)
                                            if image_path:
                                                images_saved += 1
                                        except Exception as e:
                                            st.error(f"이미지 추가 중 오류: {str(e)}")
                                            
                                    if images_saved > 0:
                                        st.success(f"{images_saved}개 이미지가 추가되었습니다!")
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
                                        old_image_paths = get_all_image_paths(domain, topic_name, term)
                                        has_images = old_image_paths and len(old_image_paths) > 0
                                        
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
                                        if has_images and st.session_state.username:
                                            try:
                                                # 사용자별 이미지 폴더
                                                user_image_folder = get_user_image_folder(st.session_state.username)
                                                
                                                # 새 폴더 확인 및 생성
                                                new_topic_folder = os.path.join(user_image_folder, domain, new_topic_name)
                                                if not os.path.exists(new_topic_folder):
                                                    os.makedirs(new_topic_folder)
                                                
                                                # 이미지 파일 이동
                                                import shutil
                                                for old_image_path in old_image_paths:
                                                    # 파일 확장자 가져오기
                                                    _, ext = os.path.splitext(old_image_path)
                                                    
                                                    # 새 이미지 파일명 생성
                                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                                    count = 1
                                                    new_image_path = os.path.join(new_topic_folder, f"{new_topic_name}_{timestamp}_{count}{ext}")
                                                    
                                                    # 파일 복사 후 원본 삭제
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
                                image_paths = get_all_image_paths(domain, topic_name, term)
                                deleted_count = 0
                                for img_path in image_paths:
                                    if os.path.exists(img_path):
                                        try:
                                            os.unlink(img_path)
                                            deleted_count += 1
                                        except Exception as e:
                                            st.error(f"이미지 삭제 중 오류 발생: {e}")
                                
                                if deleted_count > 0:
                                    st.success(f"{deleted_count}개 이미지가 삭제되었습니다!")
                                
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
    
    # 네비게이션 및 컨트롤 버튼
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
    
    with nav_col1:
        if st.button("이전", key="prev_card"):
            st.session_state.current_card_index = (st.session_state.current_card_index - 1) % len(st.session_state.study_cards)
            # 이전 카드로 이동해도 보기 상태 유지
            st.rerun()
    
    with nav_col2:
        if st.button("모두 가리기", key="hide_all"):
            st.session_state.study_show_content = False
            st.session_state.study_show_keyword = False
            st.session_state.study_show_rhyming = False
            st.rerun()
    
    with nav_col3:
        if st.button("모두 보기", key="show_all"):
            st.session_state.study_show_content = True
            st.session_state.study_show_keyword = True
            st.session_state.study_show_rhyming = True
            st.rerun()
    
    with nav_col4:
        if st.button("다음", key="next_card"):
            st.session_state.current_card_index = (st.session_state.current_card_index + 1) % len(st.session_state.study_cards)
            # 다음 카드로 이동해도 보기 상태 유지
            st.rerun()
            
    with nav_col5:
        # 카드 섞기 버튼
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
        text_col, image_col = st.columns([2, 3])
        
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
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data'].get('keyword', '정보 없음')}</h2>
                    <p>핵심키워드</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 두음 표시 - 버튼 텍스트 변경
            rhyming_button_text = "두음 가리기" if st.session_state.study_show_rhyming else "두음 보기"
            if st.button(rhyming_button_text, key="study_rhyming_btn"):
                st.session_state.study_show_rhyming = not st.session_state.study_show_rhyming
                st.rerun()
                
            if st.session_state.study_show_rhyming:
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data'].get('rhyming', '정보 없음')}</h2>
                    <p>두음</p>
                </div>
                """, unsafe_allow_html=True)
                
            # 내용 표시 - 버튼 텍스트 변경
            content_button_text = "내용 가리기" if st.session_state.study_show_content else "내용 보기"
            if st.button(content_button_text, key="study_content_btn"):
                st.session_state.study_show_content = not st.session_state.study_show_content
                st.rerun()
                
            if st.session_state.study_show_content:
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data']['content']}</h2>
                    <p>내용</p>
                </div>
                """, unsafe_allow_html=True)
        
        with image_col:
            # 이미지 표시 (정의/개념을 기준으로 이미지 경로 구성)
            term = current_card['term']
            image_paths = get_all_image_paths(domain, current_card['topic'], term)
            if image_paths:
                for img_path in image_paths:
                    try:
                        # 이미지를 base64로 인코딩하여 HTML로 표시
                        with open(img_path, "rb") as img_file:
                            encoded_img = base64.b64encode(img_file.read()).decode()
                            st.markdown(f"""
<<<<<<< HEAD
                            <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%"
=======
                            <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%" 
>>>>>>> 225f98ea8e732ace574241a623d9dc352272b440
                                onclick="openImageModal(this.src)">
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"이미지 로드 중 오류: {str(e)}")
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
        st.session_state.show_quiz_image = False  # 이미지는 처음에 보이지 않도록 설정
    
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
            st.session_state.show_quiz_image = False  # 이미지는 처음에 보이지 않도록 설정
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
    quiz_col, image_col = st.columns([2, 3])
    
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
                st.markdown(f"**핵심키워드:** {current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.')}")
        
        # 두음 힌트
        if st.session_state.show_quiz_rhyming:
            hint_displayed = True
            with st.expander("두음 힌트", expanded=True):
                st.markdown(f"**두음:** {current_card['card_data'].get('rhyming', '두음 정보가 없습니다.')}")
                
        # 내용 힌트
        if st.session_state.show_quiz_content:
            hint_displayed = True
            with st.expander("내용 힌트", expanded=True):
                st.markdown(f"**내용:** {current_card['card_data']['content']}")
        
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
            # 두음 정답
            st.markdown(f"**두음:** {current_card['card_data'].get('rhyming', '두음 정보가 없습니다.')}")
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
            image_paths = get_all_image_paths(domain, current_card['topic'], term)
            if image_paths:
                for img_path in image_paths:
                    try:
                        # 이미지를 base64로 인코딩하여 HTML로 표시
                        with open(img_path, "rb") as img_file:
                            encoded_img = base64.b64encode(img_file.read()).decode()
                            st.markdown(f"""
                            <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%" 
                                onclick="openImageModal(this.src)">
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"이미지 로드 중 오류: {str(e)}")
            else:
                st.info("이 카드에는 이미지가 없습니다.")

# 전체 도메인 학습 모드
def all_domains_study_mode():
    import random
    st.header("전체 도메인 학습 모드")
    
    data = load_data()
    domains = list(data.keys())
    
    if not domains:
        st.info("플래시카드가 없습니다. 플래시카드를 추가한 후 학습해보세요!")
        return
    
    # 도메인 선택
    selected_domains = st.multiselect("학습할 도메인 선택", domains, default=domains)
    
    if not selected_domains:
        st.warning("학습할 도메인을 선택해주세요.")
        return
    
    # 도메인:토픽 형태로 모든 플래시카드 표시 및 선택 가능하도록 추가
    domain_topic_options = []
    domain_topic_map = {}
    
    for domain in selected_domains:
        topics = data[domain]
        for topic in topics.keys():
            option = f"{domain}:{topic}"
            domain_topic_options.append(option)
            domain_topic_map[option] = {"domain": domain, "topic": topic}
    
    selected_domain_topics = st.multiselect(
        "학습할 도메인:토픽 선택 (개별 선택 가능)",
        domain_topic_options,
        default=domain_topic_options
    )
    
    if not selected_domain_topics:
        st.warning("학습할 도메인:토픽을 선택해주세요.")
        return
    
    # 선택된 도메인:토픽에서 카드 가져오기
    all_cards = []
    for domain_topic in selected_domain_topics:
        domain = domain_topic_map[domain_topic]["domain"]
        topic = domain_topic_map[domain_topic]["topic"]
        terms = data[domain][topic]
        for term, card_data in terms.items():
            all_cards.append({
                "domain": domain,
                "topic": topic, 
                "term": term, 
                "card_data": card_data
            })
    
    if not all_cards:
        st.warning("선택한 도메인:토픽에 플래시카드가 없습니다.")
        return
    
    st.write(f"총 {len(all_cards)}개의 플래시카드가 있습니다.")
    
    # 세션 상태 초기화
    if "all_study_cards" not in st.session_state:
        st.session_state.all_study_cards = all_cards.copy()
        random.shuffle(st.session_state.all_study_cards)  # 초기에 카드 섞기
        st.session_state.all_current_card_index = 0
        # 기본값을 True로 설정하여 처음부터 모든 내용이 보이도록 함
        st.session_state.all_study_show_content = True
        st.session_state.all_study_show_keyword = True
        st.session_state.all_study_show_rhyming = True
    
    # 카드가 변경되었는지 확인 (도메인 선택 변경시)
    current_cards_ids = set(f"{card['domain']}_{card['topic']}_{card['term']}" for card in all_cards)
    session_cards_ids = set(f"{card['domain']}_{card['topic']}_{card['term']}" for card in st.session_state.all_study_cards)
    
    if current_cards_ids != session_cards_ids:
        st.session_state.all_study_cards = all_cards.copy()
        st.session_state.all_current_card_index = 0
        # 토픽이 변경되어도 보기 상태 유지
        st.session_state.all_study_show_content = True
        st.session_state.all_study_show_keyword = True
        st.session_state.all_study_show_rhyming = True
    
    # 네비게이션 및 컨트롤 버튼
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
    
    with nav_col1:
        if st.button("이전", key="prev_all_card"):
            st.session_state.all_current_card_index = (st.session_state.all_current_card_index - 1) % len(st.session_state.all_study_cards)
            # 이전 카드로 이동해도 보기 상태 유지
            st.rerun()
    
    with nav_col2:
        if st.button("모두 가리기", key="hide_all_all"):
            st.session_state.all_study_show_content = False
            st.session_state.all_study_show_keyword = False
            st.session_state.all_study_show_rhyming = False
            st.rerun()
    
    with nav_col3:
        if st.button("모두 보기", key="show_all_all"):
            st.session_state.all_study_show_content = True
            st.session_state.all_study_show_keyword = True
            st.session_state.all_study_show_rhyming = True
            st.rerun()
    
    with nav_col4:
        if st.button("다음", key="next_all_card"):
            st.session_state.all_current_card_index = (st.session_state.all_current_card_index + 1) % len(st.session_state.all_study_cards)
            # 다음 카드로 이동해도 보기 상태 유지
            st.rerun()
            
    with nav_col5:
        # 카드 섞기 버튼
        if st.button("카드 섞기", key="all_study_shuffle_button"):
            shuffled_cards = all_cards.copy()
            random.shuffle(shuffled_cards)
            
            # 세션 상태 업데이트
            st.session_state.all_study_cards = shuffled_cards
            st.session_state.all_current_card_index = 0
            # 카드 섞기 후에도 보기 상태 유지
            st.session_state.all_study_show_content = True
            st.session_state.all_study_show_keyword = True
            st.session_state.all_study_show_rhyming = True
            
            st.success("카드가 섞였습니다!")
            st.rerun()
    
    # 플래시카드 보여주기
    if st.session_state.all_study_cards:
        current_card = st.session_state.all_study_cards[st.session_state.all_current_card_index]
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(f"도메인: {current_card['domain']} / 토픽: {current_card['topic']}")
        with col2:
            st.write(f"{st.session_state.all_current_card_index + 1}/{len(st.session_state.all_study_cards)}")
        
        # 카드 컨테이너 분할 (텍스트 / 이미지)
        text_col, image_col = st.columns([2, 3])
        
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
            if st.button(keyword_button_text, key="all_study_keyword_btn"):
                st.session_state.all_study_show_keyword = not st.session_state.all_study_show_keyword
                st.rerun()
                
            if st.session_state.all_study_show_keyword:
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data'].get('keyword', '정보 없음')}</h2>
                    <p>핵심키워드</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 두음 표시 - 버튼 텍스트 변경
            rhyming_button_text = "두음 가리기" if st.session_state.all_study_show_rhyming else "두음 보기"
            if st.button(rhyming_button_text, key="all_study_rhyming_btn"):
                st.session_state.all_study_show_rhyming = not st.session_state.all_study_show_rhyming
                st.rerun()
                
            if st.session_state.all_study_show_rhyming:
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data'].get('rhyming', '정보 없음')}</h2>
                    <p>두음</p>
                </div>
                """, unsafe_allow_html=True)
                
            # 내용 표시 - 버튼 텍스트 변경
            content_button_text = "내용 가리기" if st.session_state.all_study_show_content else "내용 보기"
            if st.button(content_button_text, key="all_study_content_btn"):
                st.session_state.all_study_show_content = not st.session_state.all_study_show_content
                st.rerun()
                
            if st.session_state.all_study_show_content:
                st.markdown(f"""
                <div class="card">
                    <h2>{current_card['card_data']['content']}</h2>
                    <p>내용</p>
                </div>
                """, unsafe_allow_html=True)
        
        with image_col:
            # 이미지 표시 (정의/개념을 기준으로 이미지 경로 구성)
            domain = current_card['domain']  # current_card에서 domain 가져오기
            term = current_card['term']
            image_paths = get_all_image_paths(domain, current_card['topic'], term)
            if image_paths:
                for img_path in image_paths:
                    try:
                        # 이미지를 base64로 인코딩하여 HTML로 표시
                        with open(img_path, "rb") as img_file:
                            encoded_img = base64.b64encode(img_file.read()).decode()
                            st.markdown(f"""
                            <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%" 
                                onclick="openImageModal(this.src)">
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"이미지 로드 중 오류: {str(e)}")
            else:
                st.info("이 카드에는 이미지가 없습니다.")

# 전체 도메인 퀴즈 모드
def all_domains_quiz_mode():
    import random
    st.header("전체 도메인 퀴즈 모드")
    
    data = load_data()
    domains = list(data.keys())
    
    if not domains:
        st.info("플래시카드가 없습니다. 플래시카드를 추가한 후 퀴즈를 풀어보세요!")
        return
    
    # 도메인 선택
    selected_domains = st.multiselect("퀴즈 도메인 선택", domains, default=domains)
    
    if not selected_domains:
        st.warning("퀴즈를 볼 도메인을 선택해주세요.")
        return
    
    # 도메인:토픽 형태로 모든 플래시카드 표시 및 선택 가능하도록 추가
    domain_topic_options = []
    domain_topic_map = {}
    
    for domain in selected_domains:
        topics = data[domain]
        for topic in topics.keys():
            option = f"{domain}:{topic}"
            domain_topic_options.append(option)
            domain_topic_map[option] = {"domain": domain, "topic": topic}
    
    selected_domain_topics = st.multiselect(
        "퀴즈 도메인:토픽 선택 (개별 선택 가능)",
        domain_topic_options,
        default=domain_topic_options
    )
    
    if not selected_domain_topics:
        st.warning("퀴즈를 볼 도메인:토픽을 선택해주세요.")
        return
    
    # 선택된 도메인:토픽에서 카드 가져오기
    all_cards = []
    for domain_topic in selected_domain_topics:
        domain = domain_topic_map[domain_topic]["domain"]
        topic = domain_topic_map[domain_topic]["topic"]
        terms = data[domain][topic]
        for term, card_data in terms.items():
            all_cards.append({
                "domain": domain,
                "topic": topic, 
                "term": term, 
                "card_data": card_data
            })
    
    if not all_cards:
        st.warning("선택한 도메인:토픽에 플래시카드가 없습니다.")
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
        shuffled_cards = all_cards.copy()
        random.shuffle(shuffled_cards)
        
        # 세션 상태 초기화 및 섞인 카드 설정
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
        st.session_state.all_show_quiz_image = False  # 이미지는 처음에 보이지 않도록 설정
    
    # 세션 상태 초기화
    if "all_quiz_cards" not in st.session_state or st.button("새 퀴즈 시작"):
        st.session_state.all_quiz_cards = all_cards.copy()
        random.shuffle(st.session_state.all_quiz_cards)
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
        st.session_state.all_show_quiz_image = False  # 이미지는 처음에 보이지 않도록 설정
    
    # 퀴즈가 완료되었는지 확인
    if st.session_state.all_quiz_completed:
        st.success(f"퀴즈 완료! 점수: {st.session_state.all_quiz_score}/{st.session_state.all_quiz_total}")
        if st.button("다시 풀기"):
            st.session_state.all_quiz_cards = all_cards.copy()
            random.shuffle(st.session_state.all_quiz_cards)
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
    
    # 퀴즈 타입 설정 - 항상 도메인과 토픽 보여주고 정의/개념, 특징, 내용 묻기
    st.markdown(f"""
    <div class='card'>
        <h3>문제 {st.session_state.all_current_quiz_index + 1}/{st.session_state.all_quiz_total}</h3>
        <div style="margin-bottom: 10px;">
            <span style="font-size: 14px; color: #666;">도메인: {current_card['domain']}</span><br/>
            <span style="font-size: 24px; font-weight: bold; color: #1E3A8A;">토픽: {current_card['topic']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 컨텐츠 열 분할 (퀴즈 / 이미지)
    quiz_col, image_col = st.columns([2, 3])
    
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
            if st.button("정의/개념 힌트", key="all_quiz_term_btn"):
                st.session_state.all_show_quiz_hint = not st.session_state.all_show_quiz_hint
                st.rerun()
        
        with col2:
            # 핵심키워드 힌트
            if st.button("핵심키워드 힌트", key="all_quiz_keyword_btn"):
                st.session_state.all_show_quiz_keyword = not st.session_state.all_show_quiz_keyword
                st.rerun()
        
        with col3:
            # 두음 힌트
            if st.button("두음 힌트", key="all_quiz_rhyming_btn"):
                st.session_state.all_show_quiz_rhyming = not st.session_state.all_show_quiz_rhyming
                st.rerun()
            
        with col4:
            # 내용 힌트
            if st.button("내용 힌트", key="all_quiz_content_btn"):
                st.session_state.all_show_quiz_content = not st.session_state.all_show_quiz_content
                st.rerun()
        
        with col5:
            # 이미지 힌트
            if st.button("이미지 보기", key="all_quiz_image_btn"):
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
                st.markdown(f"**핵심키워드:** {current_card['card_data'].get('keyword', '핵심키워드 정보가 없습니다.')}")
        
        # 두음 힌트
        if st.session_state.all_show_quiz_rhyming:
            hint_displayed = True
            with st.expander("두음 힌트", expanded=True):
                st.markdown(f"**두음:** {current_card['card_data'].get('rhyming', '두음 정보가 없습니다.')}")
                
        # 내용 힌트
        if st.session_state.all_show_quiz_content:
            hint_displayed = True
            with st.expander("내용 힌트", expanded=True):
                st.markdown(f"**내용:** {current_card['card_data']['content']}")
        
        # 사용자 답변 입력
        if not st.session_state.all_quiz_answer_checked:
            user_answer = st.text_area("답변", key="all_answer_input", height=100)
            if st.button("정답 확인"):
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
                if st.button("맞았어요"):
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
                if st.button("틀렸어요"):
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
            term = current_card['term']
            image_paths = get_all_image_paths(domain, current_card['topic'], term)
            if image_paths:
                for img_path in image_paths:
                    try:
                        # 이미지를 base64로 인코딩하여 HTML로 표시
                        with open(img_path, "rb") as img_file:
                            encoded_img = base64.b64encode(img_file.read()).decode()
                            st.markdown(f"""
                            <img src="data:image/png;base64,{encoded_img}" class="clickable-image" width="100%" 
                                onclick="openImageModal(this.src)">
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"이미지 로드 중 오류: {str(e)}")
            else:
                st.info("이 카드에는 이미지가 없습니다.")

if __name__ == "__main__":
    main() 