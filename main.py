import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import urllib3

# 보안 경고창 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. 캘린더 초기 세팅
cal = Calendar()
cal.add('prodid', '-//UHS Academic Calendar//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '협성대 학사일정') # 캘린더 이름
cal.add('x-wr-timezone', 'Asia/Seoul')

KST = pytz.timezone('Asia/Seoul')
current_year = datetime.now().year

# 2. 학교 웹페이지 접속해서 정보 가져오기
url = "https://www.uhs.ac.kr/uhs/121/subview.do?enc=Zm5jdDF8QEB8JTJGc2NoZHVsbWFuYWdlJTJGdWhzJTJGMSUyRnZpZXcuZG8lM0Y%3D"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')

# 3. 달력 일정 찾아내기 (표 구조 분석)
# 일반적인 대학교 학사일정 표(Table) 형태를 기준으로 데이터를 찾습니다.
tables = soup.find_all('table')

for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        # 칸이 2개 이상인 줄만 분석 (보통 '날짜', '일정내용' 순서)
        if len(cols) >= 2:
            date_text = cols[0].get_text(strip=True)
            event_text = cols[1].get_text(strip=True)
            
            # '03.02' 또는 '3월 2일' 같은 숫자 패턴(월, 일) 찾아내기
            dates = re.findall(r'(\d{1,2})[\./월]\s*(\d{1,2})', date_text)
            
            if dates and event_text:
                try:
                    # 첫 번째 찾은 날짜 = 시작일
                    start_month, start_day = int(dates[0][0]), int(dates[0][1])
                    start_date = datetime(current_year, start_month, start_day, tzinfo=KST)
                    
                    # 두 번째 찾은 날짜가 있으면 = 종료일
                    if len(dates) > 1:
                        end_month, end_day = int(dates[1][0]), int(dates[1][1])
                        # 구글 캘린더 종일 일정은 종료일이 '다음날 0시'여야 함
                        end_date = datetime(current_year, end_month, end_day, tzinfo=KST) + timedelta(days=1)
                    else:
                        end_date = start_date + timedelta(days=1)
                        
                    # 일정 파일에 추가하기
                    event = Event()
                    event.add('summary', event_text)
                    event.add('dtstart', start_date.date())
                    event.add('dtend', end_date.date())
                    cal.add_component(event)
                except ValueError:
                    continue # 날짜 모양이 이상하면 건너뜀

# 4. 최종 ics 파일로 저장
with open('academic_calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print("진짜 학사일정 캘린더 업데이트 완료!")
