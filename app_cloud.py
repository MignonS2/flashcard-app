import os
import subprocess
import threading
import time
import streamlit as st
from pyngrok import ngrok
import logging
import signal
import sys
import datetime
import atexit

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 설정
PORT = 8501
GIT_REPO_PATH = os.path.dirname(os.path.abspath(__file__))
COMMIT_INTERVAL = 300  # 5분마다 git 커밋 (변경사항이 있는 경우)

# Git 명령어 실행 함수
def run_git_command(command):
    try:
        result = subprocess.run(
            command,
            cwd=GIT_REPO_PATH,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git 명령어 실행 중 오류 발생: {e}")
        logger.error(f"오류 내용: {e.stderr}")
        return None

# Git 저장소 초기화 및 확인
def init_git_repo():
    # Git 저장소인지 확인
    if not os.path.exists(os.path.join(GIT_REPO_PATH, ".git")):
        logger.warning(f"{GIT_REPO_PATH}는 Git 저장소가 아닙니다. Git 저장소를 초기화합니다.")
        run_git_command(["git", "init"])
    
    # Git 사용자 설정 확인
    git_user = run_git_command(["git", "config", "user.name"])
    git_email = run_git_command(["git", "config", "user.email"])
    
    if not git_user or not git_email:
        logger.info("Git 사용자 정보 설정")
        if not git_user:
            run_git_command(["git", "config", "user.name", "Flashcard App User"])
        if not git_email:
            run_git_command(["git", "config", "user.email", "flashcard-app@example.com"])
    
    logger.info("Git 저장소 초기화 완료")

# 변경사항 커밋 함수
def commit_changes():
    # 변경된 파일이 있는지 확인
    status = run_git_command(["git", "status", "--porcelain"])
    
    if status:
        logger.info("변경된 파일 감지, 커밋 진행")
        # 변경된 모든 파일 추가
        run_git_command(["git", "add", "."])
        
        # 현재 시간을 포함한 커밋 메시지 생성
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Auto-commit: 플래시카드 앱 데이터 업데이트 {timestamp}"
        
        # 변경사항 커밋
        run_git_command(["git", "commit", "-m", commit_message])
        logger.info(f"커밋 완료: {commit_message}")
        
        # 원격 저장소가 설정되어 있는지 확인
        remote = run_git_command(["git", "remote"])
        if remote:
            try:
                # 원격 저장소에 푸시
                run_git_command(["git", "push"])
                logger.info("원격 저장소에 푸시 완료")
            except Exception as e:
                logger.error(f"원격 저장소 푸시 중 오류 발생: {e}")
        else:
            logger.info("원격 저장소가 설정되어 있지 않아 푸시를 건너뜁니다.")
        
        return True
    else:
        logger.info("변경된 파일이 없습니다.")
        return False

# 주기적으로 변경사항 커밋하는 함수
def periodic_commit():
    while True:
        time.sleep(COMMIT_INTERVAL)
        commit_changes()

# 앱 종료 시 변경사항 커밋
def cleanup():
    logger.info("앱 종료, 마지막 변경사항 커밋")
    commit_changes()
    
    # ngrok 터널 종료
    try:
        ngrok.kill()
        logger.info("ngrok 터널이 종료되었습니다.")
    except Exception as e:
        logger.error(f"ngrok 터널 종료 중 오류 발생: {e}")

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

# 종료 시그널 핸들러
def signal_handler(sig, frame):
    logger.info("종료 시그널 감지, 정리 작업 수행")
    cleanup()
    sys.exit(0)

if __name__ == "__main__":
    # 종료 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 종료 시 정리 함수 등록
    atexit.register(cleanup)
    
    # Git 저장소 초기화
    init_git_repo()
    
    # Streamlit 앱 실행
    run_streamlit_app()
    
    # 앱이 시작될 때까지 잠시 대기
    time.sleep(3)
    
    # ngrok 터널 설정
    public_url = setup_ngrok()
    
    if public_url:
        print(f"\n\n앱에 접속하려면 다음 URL을 방문하세요: {public_url}\n\n")
        print(f"이 앱은 로컬 Git 저장소({GIT_REPO_PATH})와 연동되어 있습니다.")
        print(f"변경사항은 {COMMIT_INTERVAL}초마다 자동으로 커밋되며, 앱 종료 시에도 커밋됩니다.")
    else:
        print("\n\n공개 URL 생성에 실패했습니다. 로그를 확인하세요.\n\n")
    
    # 주기적 커밋 스레드 시작
    commit_thread = threading.Thread(target=periodic_commit, daemon=True)
    commit_thread.start()
    
    # 터널을 유지하기 위해 메인 스레드 실행 유지
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("사용자에 의한 종료, 정리 작업 수행")
        cleanup() 