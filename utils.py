from __future__ import print_function
import os.path
import pickle
import pytz
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import os
import subprocess
from gtts import gTTS

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def speak(audioString):
    print(audioString)
    tts = gTTS(text=audioString, lang='en', tld='co.za')
    tts.save("audio_main.mp3")
    os.system("mpg123 audio_main.mp3")


def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/home/babayaga/PycharmProjects/Jarvis/creds.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service


def get_events(day):
    service = authenticate_google()
    # Call the Calendar API
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    # print('before:', date)
    end = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    # print('after:', date)
    end = end.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start[:19], event['summary'])
    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start[:19], event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])  # get the hour the event starts
            if int(start_time.split(":")[0]) < 12:  # if the event is in the morning
                start_time = start_time[:8] + " am"
            else:
                start_time = str(int(start_time.split(":")[0]))  # convert 24 hour time to regular
                start_time = start_time[:8] + " pm"
            print(event["summary"])
            speak(event['start'] + event["summary"] + " at " + start_time)


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
        year = year + 1

        # This is slighlty different from the video but the correct version
    if month == -1 and day != -1:  # if we didn't find a month, but we have a day
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

        # if we only found a dta of the week
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)

def get_all_events():
    service = authenticate_google()
    now = datetime.datetime.utcnow().isoformat()  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])  # get the hour the event starts
            if int(start_time.split(":")[0]) < 12:  # if the event is in the morning
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12)  # convert 24 hour time to regular
                start_time = start_time + "pm"

            speak(event["summary"] + " at " + start_time)

def note(text):
    file_name = 'memo.txt'
    print(text)
    speak('Got it sir. Writing it down.')
    with open(file_name, "a") as f:
        text = '\n'+text+'.'
        f.write(text)


def read_note():
    file = open('memo.txt', 'r')
    speak(file.read())

def add_event(title, start_time, end_time=None):
    # This function is under developement. To be able to execute this properly I'll have
    # to figure out a way to extract time information from the input and convert that into
    # google calendar's format.
    # 2012-07-11T03:30:00-06:00 : Required Format
    if end_time == None:
        end_time = start_time
    service = authenticate_google()
    event = {
        'summary': title,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
    }
    print(start_time, end_time)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def remove_event(title):
    service = authenticate_google()
    event = {'summary' : title}
    service.events().delete(calendarId='primary', eventId='eventId').execute()
    print('Event deleted: %s' % (event.get('htmlLink')))

# add_event('Take GRE exam', start_time='2021-07-11T03:30:00-06:00')

# there might be a potential clash with the event summary and phrase-key. Better to call get time
# seperately



