# 워드프레스 주식 블로그 자동화 (WordPress Stock Blog Automation)

이 프로젝트는 매일 자동으로 주식 시장 데이터나 금융 뉴스를 수집하고, AI를 사용하여 블로그 포스팅을 생성한 후 워드프레스에 자동으로 게시하는 파이썬 스크립트입니다.

## 주요 기능

1.  **데이터 수집 자동화**:
    *   **화요일 ~ 토요일**: 전날의 나스닥(NASDAQ) 시장 데이터를 수집합니다. (`yfinance` 사용)
    *   **일요일 ~ 월요일**: 구글 파이낸스(Google Finance)에서 주요 금융 뉴스를 크롤링합니다.
2.  **AI 콘텐츠 생성 (SEO 최적화)**:
    *   수집된 데이터를 바탕으로 Google Gemini API를 사용하여 한국어 블로그 포스팅을 작성합니다.
    *   **구조화된 템플릿**: 제목, 서론, 주요 요점, 상세 분석, 결론으로 구성된 체계적인 글을 작성합니다.
    *   **SEO 강화**: 메타 설명(Meta Description)과 태그(Tags)를 자동으로 생성하여 검색 엔진 최적화를 지원합니다.
    *   HTML 형식(H2, H3, 리스트 등)으로 포맷팅되어 가독성을 높입니다.
3.  **워드프레스 자동 포스팅 및 카테고리 관리**:
    *   생성된 콘텐츠를 워드프레스 REST API를 통해 자동으로 게시합니다.
    *   **카테고리 자동 관리**: '미국주식', '한국주식' 카테고리를 자동으로 생성하고 글을 분류합니다. (현재는 주로 '미국주식'에 할당)
    *   태그 및 요약글(Excerpt)도 함께 등록됩니다.

## 설치 및 실행 방법

### 1. 필수 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정 (.env)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 아래 정보를 입력하세요.

```env
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_application_password
GEMINI_API_KEY=your_gemini_api_key
```

### 3. 실행

```bash
python run_automation.py
```

또는 `run_automation.bat` 파일을 실행하여 간편하게 실행할 수 있습니다.

## 파일 구조

*   `run_automation.py`: 메인 자동화 스크립트 (카테고리 로직 및 SEO 프롬프트 포함)
*   `requirements.txt`: 필요한 파이썬 라이브러리 목록
*   `.env`: 환경 변수 (GitHub에 업로드되지 않음)
*   `.gitignore`: Git 제외 파일 목록

## 라이선스

이 프로젝트는 개인적인 용도로 작성되었습니다.
