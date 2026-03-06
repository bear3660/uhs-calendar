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
target_years = [current_year, current_year + 1] # 올해와 내년, 총 2년 치를 목표로 설정

url = "https://www.uhs.ac.kr/uhs/121/subview.do?enc=Zm5jdDF8QEB8JTJGc2NoZHVsbWFuYWdlJTJGdWhzJTJGMSUyRnZpZXcuZG8lM0Y%3D"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 1. 연도 반복 (예: 2026년 한 바퀴, 끝나면 2027년 한 바퀴)
for year in target_years:
    # 2. 월 반복 (1월부터 12월까지)
    for month in range(1, 13):
        payload = {
            'year': str(year),
            'month': str(month)
        }
        
        response = requests.post(url, headers=headers, data=payload, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sche_comt = soup.find('div', class_='sche-comt')
        if not sche_comt:
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
                        start_date = datetime(year, start_month, start_day, tzinfo=KST)
                        
                        if len(dates) > 1:
                            end_month, end_day = int(dates[1][0]), int(dates[1][1])
                            end_year = year
                            
                            # 만약 시작 월보다 종료 월이 작다면(예: 시작 12월, 종료 1월), 해가 넘어간 것으로 간주
                            if end_month < start_month:
                                end_year += 1
                                
                            end_date = datetime(end_year, end_month, end_day, tzinfo=KST) + timedelta(days=1)
                        else:
                            end_date = start_date + timedelta(days=1)
                            
                        event = Event()
                        event.add('summary', event_text)
                        event.add('dtstart', start_date.date())
                        event.add('dtend', end_date.date())
                        cal.add_component(event)
                    except ValueError:
                        continue

with open('academic_calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print(f"{current_year}년 및 {current_year+1}년 학사일정 크롤링 완료!")
