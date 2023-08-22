# 파이썬 베이스 이미지 사용
FROM python:3.11.4

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 컨테이너에 복사
COPY . /app

# 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 앱 실행 명령
CMD sleep infinity