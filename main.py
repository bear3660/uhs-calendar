import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz

# 1. 캘린더 만들기 준비
cal = Calendar()
cal.add('prodid', '-//UHS Calendar Test//')
cal.add('version', '2.0')

# 2. 임시 테스트 일정 생성 (나중에 이 부분을 학교 웹페이지 긁어오는 코드로 바꿀 거예요!)
event = Event()
event.add('summary', '학사일정 로봇 테스트 완료!')
# 2026년 3월 10일 일정을 하나 만들어 봅니다.
event.add('dtstart', datetime(2026, 3, 10, tzinfo=pytz.timezone('Asia/Seoul')))
event.add('dtend', datetime(2026, 3, 11, tzinfo=pytz.timezone('Asia/Seoul')))
cal.add_component(event)

# 3. 구글 캘린더가 읽을 수 있는 ics 파일로 저장하기
with open('academic_calendar.ics', 'wb') as f:
    f.write(cal.to_ical())

print("테스트 캘린더 파일이 성공적으로 만들어졌습니다!")
