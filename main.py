import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import re
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cal = Calendar()
cal.add('prodid', '-//UHS Academic Calendar//')
cal.add('version', '2.0')
cal.add('x-wr-calname', '협성대 학사일정')
cal.add('x-wr-timezone', 'Asia/Seoul')

KST = pytz.timezone('Asia/Seoul')
current_year = datetime.now().year

target_periods = []
for m in range(1, 13):
    target_periods.append((current_year, m))
for m in range(1, 3):
    target_periods.append((current_year + 1, m))

url = "https://www.uhs.ac.kr/uhs/121/subview.do?enc=Zm5jdDF8QEB8JTJGc2NoZHVsbWFuYWdlJTJGdWhzJTJGMSUyRnZpZXcuZG8lM0Y%3D"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.uhs.ac.kr/'
}

session = requests.Session()

# 💡 캘린더 일정이 여러 달에 걸쳐 중복으로 등록되는 것을 막는 메모장입니다.
added_events = set()

for year, month in target_periods:
    payload = {
        'year': str(year),
        'month': str(month)
    }
    
    try:
        response = session.post(url, headers=headers, data=payload, verify=False, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sche_comt = soup.find('div', class_='sche-comt')
        if not sche_comt:
            time.sleep(1)
            continue
            
        rows = sche_comt.find_all('tr')
        
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            
            if th and td:
                date_text = th.get_text(strip=True)
                event_text = td.get_text(strip=True)
                
                dates = re.findall(r'(\d{1,2})[\./월]\s*(\d{1,2})', date_text)
                
                if dates and event_text:
                    try:
                        start_month, start_day = int(dates[0][0]), int(dates[0][1])
                        
                        # 💡 핵심 버그 수정: 1~2월 달력에서 11~12월 일정을 발견하면 무조건 작년으로 뺍니다!
                        start_year = year
                        if month <= 2 and start_month >= 11:
                            start_year = year - 1
                            
                        start_date = datetime(start_year, start_month, start_day, tzinfo=KST)
                        
                        if len(dates) > 1:
                            end_month, end_day = int(dates[1][0]), int(dates[1][1])
                            end_year = start_year
                            
                            if end_month < start_month:
                                end_year += 1
                                
                            end_date = datetime(end_year, end_month, end_day, tzinfo=KST) + timedelta(days=1)
                        else:
                            end_date = start_date + timedelta(days=1)
                            
                        # 💡 중복 검사: 이미 달력에 넣은 일정이면 건너뜁니다.
                        event_key = f"{event_text}_{start_date.strftime('%Y%m%d')}"
                        if event_key in added_events:
                            continue
                        added_events.add(event_key)
                            
                        event = Event()
                        event.add('summary', event_text)
                        event.add('dtstart', start_date.date())
                        event.add('dtend', end_date.date())
                        cal.add_component(event)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"서버 연결 에러 ({year}년 {month}월): {e}")
        
    time.sleep(1)

with open('academic_calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"{current_year}년 1월 ~ {current_year+1}년 2월 학사일정 크롤링 완료!")
