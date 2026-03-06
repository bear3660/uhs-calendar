import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cal = Calendar()
cal.add('prodid', '-//UHS Academic Calendar//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '협성대 학사일정')
cal.add('x-wr-timezone', 'Asia/Seoul')

KST = pytz.timezone('Asia/Seoul')
current_year = datetime.now().year

url = "https://www.uhs.ac.kr/uhs/121/subview.do?enc=Zm5jdDF8QEB8JTJGc2NoZHVsbWFuYWdlJTJGdWhzJTJGMSUyRnZpZXcuZG8lM0Y%3D"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 1월부터 12월까지 총 12번 반복해서 데이터 가져오기
for month in range(1, 13):
    # 서버에 몇 월 데이터를 줄지 요청하는 데이터 꾸러미
    payload = {
        'year': str(current_year),
        'month': str(month)
    }
    
    # 데이터를 요청(POST)하고 홈페이지 내용 받아오기
    response = requests.post(url, headers=headers, data=payload, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 캡처에서 확인한 <div class="sche-comt"> 구조 찾기
    sche_comt = soup.find('div', class_='sche-comt')
    if not sche_comt:
        continue
        
    rows = sche_comt.find_all('tr')
    
    for row in rows:
        th = row.find('th') # 날짜 (예: 03.01 ~ 03.01)
        td = row.find('td') # 일정 (예: 2026학년도 1학기 개시)
        
        if th and td:
            date_text = th.get_text(strip=True)
            event_text = td.get_text(strip=True)
            
            # 정규식으로 숫자(월, 일) 패턴 추출
            dates = re.findall(r'(\d{1,2})[\./월]\s*(\d{1,2})', date_text)
            
            if dates and event_text:
                try:
                    start_month, start_day = int(dates[0][0]), int(dates[0][1])
                    start_date = datetime(current_year, start_month, start_day, tzinfo=KST)
                    
                    if len(dates) > 1:
                        end_month, end_day = int(dates[1][0]), int(dates[1][1])
                        end_date = datetime(current_year, end_month, end_day, tzinfo=KST) + timedelta(days=1)
                    else:
                        end_date = start_date + timedelta(days=1)
                        
                    event = Event()
                    event.add('summary', event_text)
                    event.add('dtstart', start_date.date())
                    event.add('dtend', end_date.date())
                    cal.add_component(event)
                except ValueError:
                    continue

# 완성된 1년 치 달력 저장
with open('academic_calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print("1년 치 학사일정 크롤링 완료!")
