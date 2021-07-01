from __future__ import print_function
import os.path
import pickle
import pyttsx3
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import playsound
from gtts import gTTS
import datetime
import pytz
import spacy
import re

time_frames = ['hour', 'minute', 'day', 'tomorrow']

UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


# def speak(audioString):
#     print(audioString)
#     tts = gTTS(text=audioString, lang='en', tld='co.za')
#
#     # os.system("audio_main.mp3")

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


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
                'creds.json', SCOPES)
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
    if text == 'tomorrow':
        return datetime.datetime.now(IST) + datetime.timedelta(days=1)

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


def get_time(command):
    nlp = spacy.load('en_core_web_sm')
    text = nlp(command)
    for ent in text.ents:
        if ent.label_ == 'TIME' or 'DATE':
            time_information = ent.text
            # print(time_information)
    time_information = [0,0]
    for i in time_frames:
        if i in time_information:
            try:
                scale = int(re.search(r'\d+', time_information).group())
            except AttributeError:
                scale = (re.search(r'\d+', time_information))
            # print(i, scale, '\n', datetime.datetime.now(IST))
            if i == 'hour':
                effective_time = datetime.datetime.now(IST) + datetime.timedelta(hours=scale)
            elif i == 'minute':
                effective_time = datetime.datetime.now(IST) + datetime.timedelta(minutes=scale)
            elif i == 'tomorrow':
                effective_time = datetime.datetime.now(IST) + datetime.timedelta(days=1)
            else:
                effective_time = datetime.datetime.now(IST) + datetime.timedelta(days=scale)

            effective_time = str(effective_time)
            effective_time: str = effective_time[:10]+ 'T0' + effective_time[12:22]

            return effective_time
        else: effective_time = 0

    return effective_time

def add_event(description, start_time, end_time=None):
    # This function is under development. To be able to execute this properly I'll have
    # to figure out a way to extract time information from the input and convert that into
    # google calendar's format.
    # 2012-07-11T03:30:00-06:00 : Required Format
    if end_time == None:
        end_time = start_time
    service = authenticate_google()
    event = {
        'summary': 'Reminder',
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata',
            'description': description,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
    }
    print(start_time, end_time)
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    speak('Task Succesful sir.')

def get_weather():
    import requests, json

    # Enter your API key here
    api_key = "3c66fcd4dd5aceefe2cc38e0ec1d51ee"

    # base_url variable to store url
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Give city name
    city_name = 'Nellore'

    complete_url = base_url + "q=" + city_name + "&appid=" + api_key
    response = requests.get(complete_url)

    x = response.json()

    if x["cod"] != "404":
        y = x["main"]
        current_temperature = int(y["temp"]) - 273
        current_pressure = y["pressure"]
        current_humidity = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        print(" The Temperature: " +
              str(current_temperature) + ' Degrees Celsius.'
              "\n description = " +
              str(weather_description))
        speak(" The Weather in Nellure is " +
              str(current_temperature) + ' Degrees Celsius.'
              "\n  and is expected to be " +
              str(weather_description))

