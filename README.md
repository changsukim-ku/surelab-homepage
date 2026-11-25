# SuRe Lab homepage

Superintelligence Representation Lab (SuRe Lab), School of Electrical Engineering, Korea University.

정적 HTML 사이트입니다. 빌드 과정 없이 이 폴더를 그대로 웹 서버에 올리면 됩니다.

- `index.html`, `people.html`, `publications.html`, `join.html`, `seminars.html`: 페이지
- `images/`: 사진
- `_source/`: 페이지를 만드는 원본과 스크립트 (웹에 노출되어도 문제없음)

내용 수정은 교수님이 Claude와 함께 이 저장소에 직접 올립니다. 서버는 아래처럼 한 번만 설정하면 됩니다.

## 서버 설정 (처음 한 번)

### 1. 저장소 받기

```bash
sudo git clone https://github.com/changsukim-ku/surelab-homepage.git /var/www/surelab
```

### 2. 자동 갱신 (5분마다)

```bash
sudo crontab -e
# 아래 한 줄 추가
*/5 * * * * cd /var/www/surelab && git pull -q
```

### 3. 웹 서버 설정 (nginx 예시)

```nginx
server {
    listen 80;
    server_name mcl.korea.ac.kr;          # 새 도메인이 나오면 surelab.korea.ac.kr 로 바꾼다
    root /var/www/surelab;
    index index.html;
    location / { try_files $uri $uri/ =404; }
}
```

Apache를 쓴다면 `DocumentRoot /var/www/surelab` 로 같은 효과를 낸다. HTTPS는 certbot(Let's Encrypt)으로 붙인다.

### 4. 새 도메인이 나온 뒤

surelab.korea.ac.kr 이 이 서버를 가리키게 되면, mcl.korea.ac.kr 로 들어오는 웹 접속은 모두 새 주소로 넘긴다.

```nginx
server {
    listen 80;
    server_name mcl.korea.ac.kr;
    return 301 https://surelab.korea.ac.kr/;
}
```

## 주의

- **mcl.korea.ac.kr 도메인 자체와 메일(MX) 설정은 절대 건드리지 않는다.** @mcl.korea.ac.kr 메일은 Google Workspace로 계속 쓴다.
- 기존 WordPress 사이트와 데이터베이스는 지우지 말고 백업해 둔다. 옛 사진과 논문 목록을 옮길 때 필요하다.
