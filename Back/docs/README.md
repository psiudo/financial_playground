<!-- back/docs/README.md -->
# 사용자 시나리오 문서

본 문서는 금융 상품 비교 프로젝트의 핵심 사용자 시나리오를 정리한 것이다.  
각 시나리오는 서비스 흐름, 사용자 분기, UX 흐름을 기준으로 구성되어 있으며,  
후속 ERD 설계 및 API 정의의 기준으로 활용된다.


# 1. 가상환경 생성 및 활성화 (Windows 기준 - Git Bash)
python -m venv .venv
source .venv/Scripts/activate

# 2. pip 업그레이드 및 필수 패키지 설치
pip install --upgrade pip
pip install django==4.2.20 djangorestframework==3.16.0 openai==1.82.0 \
    python-dotenv==1.1.0 requests==2.32.3 \
    rest_framework_simplejwt==0.0.2 selenium==4.32.0 \
    webdriver-manager==4.0.2 yfinance==0.2.61 \
    django-extensions pydotplus

# 3. Graphviz 설치 (수동)
https://graphviz.org/download/ → Windows 설치 후 아래 경로를 환경변수 PATH에 추가

C:\Program Files\Graphviz\bin

# 4. 설치 확인
where dot  # dot.exe 경로가 출력되어야 함

# 5. ERD 이미지 생성
python manage.py graph_models -a -o docs/erd.png

# 6. 최종 requirements.txt 생성
pip freeze > requirements.txt
