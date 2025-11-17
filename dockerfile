# 이 Docker의 이미지의 기본 os, python 설정
# python3.11이 설치된 최소 linux 이미지(Debian Slim) 
# 즉, 이 이미지를 기반으로 새 이미지를 만듦
FROM python:3.11-slim

# working 디렉토리를 컨테이너 내부의 작업 디렉토리를 /app으로 설정
# 이후 COPY / RUN / CMD 명령의 기준 경로가 /app이 됨 없으면 자동으로 생성
WORKDIR /app

# 로컬 프로젝트의 requirements.txt 파일을 컨테이너 /app/ 경로에 복사
# pip install을 하기 위해 우선 requirements만 복사하는 이유는 최적화 때문
COPY requirements.txt /app/

## 컨테이너 안에서 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 현재 폴더(opensw HW2) 전체를 컨테이너 /app/으로 복사 
# 즉, Django 프로젝트 전체 파일이 컨테이너로 돌아감
COPY . /app/

# 컨테이너가 8000번 포트를 사용함을 문서화
# 컨테이너 외부에서 접근하려면 실행 시 -p 8000:8000 옵션 필요
EXPOSE 8000

# 컨테이너가 실행될 때 가장 마지막에 실행되는 명령
# Django 개발 서버 실행
# 0.0.0.0:8000 -> 외부 접속 허용 (localhost만 허용하는 기본 127.0.0.1과 다름)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
