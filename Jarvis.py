# Add common Abort statements globally
# Bring in the morning briefing


import datetime
import webbrowser
from utils import get_events, get_date, speak, get_all_events, note, read_note, get_time, add_event, get_weather
from random import randint
import pywhatkit
from googlesearch import search
import speech_recognition as sr

intro = ['Hello. I am Jarvis. Yashwanths Personal Assistant.']

wish = ['hi', 'hey', 'whats up', 'are you there']

wish_reply = [ 'As always sir',
              'I am at your disposal sir.']

greetings = ['Hello sir.', 'Good to see you sir.', 'I am glad you are back sir.', 'Been a while Sir.']

task_fails = ['I might have to disappoint you sir. That is currently out of my capabilities.',
              'Unfortunately, I do not recognize this task sir, perhaps it is time for you to develop that.',
              'I am sorry sir, I am not sure if I can do it yet.']

questions = ['who', 'where', 'which', 'when', 'why', 'what', 'how', 'search', 'show']

CALENDAR_STRS = ["what do i have", "do i have plans", "busy", 'schedule']

processing = ['On it sir.',
              'Let me see what I can do.',
              'Right sir. Understood']

functions = ['I can currently,', 'do a websearch, ', 'keep track of your upcoming events, ',
             'Play a specific video on youtube, '
             'take a quick note..', 'many more under developement.']

r = sr.Recognizer()
# r.energy_threshold = 11470.226149936585  # 2435.247887648958   # 1920.5755112995746
r.pause_threshold = 0.8

speak(intro[0])
trigger = 'jarvis'


def take_command():
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in').lower()
        print(query)
    except Exception as e:
        query = ''
        # speak(query)
        print(e)
    return query


def run_jarvis(*args):
    if args == ():
        command = take_command()
    else:
        command = args(1)
    print('Task Ready...')
    fail = 1
    for i in wish:
        if i in command:
            speak(greetings[randint(0, len(greetings)-1)])
            fail = 0
            break
    if fail:
        speak(processing[randint(0, len(processing) - 1)])
    if 'play' in command:
        song = command.replace('play', '')
        speak('playing ' + song)
        pywhatkit.playonyt(song)
        fail = 0
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        speak('Current time is ' + time)
        fail = 0
    elif 'note' in command:
        speak('What do you want me to take down sir?')
        fail = 0
        flag = 1
        while flag:
            task = take_command()
            print(task)
            speak(task + 'Is that correct, sir?')
            response = take_command()
            print(response)
            if 'positive' in response or 'correct' in response:
                note(task)
                speak('is there anything else you would like to add sir?')
                cont = take_command()
                if 'positive' in cont or 'correct' in cont:
                    print(cont)
                    flag = 1
                else:
                    flag = 0
            else:
                speak('I beg your pardon sir')
    elif 'read' in command:
        read_note()
        fail = 0
    elif 'quit' in command:
        return 0
    elif 'remind' in command or 'add' in command:
        inp = command
        while True:
            if get_time(inp):
                add_event(description=inp, start_time=get_time(inp))
                fail = 0
                break
            else:
                speak('Please provide a time window sir')
                inp = take_command()
            if 'quit' in command:
                break
    else:
        for phrase in CALENDAR_STRS:
            if phrase not in command:
                pass
            else:
                fail = 0
                date = get_date(command)
                print(date)
                if date:
                    get_events(date)
                else:
                    get_all_events()
        if ('perform' in command or 'do' in command) and fail:
            word = ''
            for i in functions:
                word = word + i
            speak(word)
            fail = 0
        for i in questions:
            # print(i,fail)
            if i in command and fail:
                print('here')
                url = (search(command, num_results=1))
                for j in url:
                    fail = 0
                    link = j
                    webbrowser.open(link)

    if fail:
        speak(task_fails[randint(0, len(task_fails) - 1)])
    return 1




if (int(datetime.datetime.now().hour) >= 4) and (int(datetime.datetime.now().hour) < 12):
    speak('Good Morning sir')
    get_weather()
    get_events(get_date('today'))
while True:
    command = take_command()
    if trigger in command:
        speak('At your service sir.')
        while True:
            status = run_jarvis()
            if not status:
                break
