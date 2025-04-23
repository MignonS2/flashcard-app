import os
import subprocess
import threading
import time
import streamlit as st
from pyngrok import ngrok
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 설정
PORT = 8501

# Streamlit 앱 실행 함수
def run_streamlit_app():
    try:
        # 앱 실행 (백그라운드)
        subprocess.Popen(["streamlit", "run", "app.py", "--server.port", str(PORT)])
        logger.info(f"Streamlit 앱이 포트 {PORT}에서 실행 중입니다.")
    except Exception as e:
        logger.error(f"Streamlit 앱 실행 중 오류 발생: {e}")

# ngrok 터널 설정 함수
def setup_ngrok():
    # ngrok 인증 토큰 설정 (환경 변수 또는 secrets.toml에서 가져오기)
    ngrok_token = os.environ.get("NGROK_TOKEN", st.secrets.get("ngrok_token", ""))
    
    if ngrok_token:
        try:
            ngrok.set_auth_token(ngrok_token)
            logger.info("ngrok 인증 완료")
        except Exception as e:
            logger.error(f"ngrok 인증 중 오류 발생: {e}")
    
    try:
        # ngrok HTTP 터널 생성
        public_url = ngrok.connect(PORT)
        logger.info(f"앱 공개 URL: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"ngrok 터널 설정 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    # Streamlit 앱 실행
    run_streamlit_app()
    
    # 앱이 시작될 때까지 잠시 대기
    time.sleep(3)
    
    # ngrok 터널 설정
    public_url = setup_ngrok()
    
    if public_url:
        print(f"\n\n앱에 접속하려면 다음 URL을 방문하세요: {public_url}\n\n")
    else:
        print("\n\n공개 URL 생성에 실패했습니다. 로그를 확인하세요.\n\n")
    
    # 터널을 유지하기 위해 메인 스레드 실행 유지
    while True:
        time.sleep(60) 