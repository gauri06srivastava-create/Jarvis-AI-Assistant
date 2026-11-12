import os
import ctypes
import datetime
import webbrowser
import subprocess
import threading
import time

import pyttsx3
import sounddevice as sd
import speech_recognition as sr

from PIL import ImageGrab

from dotenv import load_dotenv
from groq import Groq

from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL


# ==========================================
# GLOBAL FOCUS VARIABLES
# ==========================================

focus_end_time = None
focus_active = False


# ==========================================
# LOAD GROQ API KEY
# ==========================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found in .env file.")
    exit()

client = Groq(api_key=api_key)


# ==========================================
# TEXT TO SPEECH
# ==========================================

def speak(text):

    print("Jarvis:", text)

    try:

        engine = pyttsx3.init("sapi5")

        voices = engine.getProperty("voices")

        if voices:
            engine.setProperty("voice", voices[0].id)

        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:

        print("TTS Error:", e)


# ==========================================
# SPEECH TO TEXT
# ==========================================

def listen():

    sample_rate = 16000
    duration = 5

    print("\nJarvis: Listening... 🎤")

    try:

        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio = sr.AudioData(
            recording.tobytes(),
            sample_rate,
            2
        )

        recognizer = sr.Recognizer()

        command = recognizer.recognize_google(audio)

        print("You:", command)

        return command.lower()

    except sr.UnknownValueError:

        print("Jarvis: I couldn't understand.")
        return ""

    except sr.RequestError:

        print("Jarvis: Speech recognition service is unavailable.")
        return ""

    except Exception as e:

        print("Microphone Error:", e)
        return ""


# ==========================================
# GROQ AI BRAIN
# ==========================================

def ask_ai(question):

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Jarvis, a helpful and friendly AI assistant. "
                        "Give short and clear answers because you are speaking "
                        "through voice."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        print("GROQ ERROR:", repr(e))

        return "Sorry, I could not connect to my AI brain."


# ==========================================
# TIME
# ==========================================

def tell_time():

    current_time = datetime.datetime.now().strftime("%I:%M %p")

    speak(f"The time is {current_time}")


# ==========================================
# DATE
# ==========================================

def tell_date():

    current_date = datetime.datetime.now().strftime("%d %B %Y")

    speak(f"Today's date is {current_date}")


# ==========================================
# OPEN YOUTUBE
# ==========================================

def open_youtube():

    speak("Opening YouTube")

    webbrowser.open("https://www.youtube.com")


# ==========================================
# OPEN GOOGLE
# ==========================================

def open_google():

    speak("Opening Google")

    webbrowser.open("https://www.google.com")


# ==========================================
# GOOGLE SEARCH
# ==========================================

def google_search(command):

    query = command

    query = query.replace("search google for", "")
    query = query.replace("search for", "")

    query = query.strip()

    if query == "":

        speak("What should I search for?")
        return

    speak(f"Searching Google for {query}")

    url = (
        "https://www.google.com/search?q="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)


# ==========================================
# YOUTUBE SEARCH
# ==========================================

def youtube_search(command):

    query = command

    query = query.replace("play", "")
    query = query.replace("on youtube", "")
    query = query.replace("youtube", "")

    query = query.strip()

    if query == "":

        speak("What should I play?")
        return

    speak(f"Searching YouTube for {query}")

    url = (
        "https://www.youtube.com/results?search_query="
        + query.replace(" ", "+")
    )

    webbrowser.open(url)


# ==========================================
# OPEN APPLICATION
# ==========================================

def open_app(app):

    try:

        subprocess.Popen(app)

        speak(f"Opening {app}")

    except Exception as e:

        print("App Error:", e)

        speak("I could not open that application.")


# ==========================================
# VOLUME CONTROL
# ==========================================

def change_volume(action):

    try:

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None
        )

        volume = cast(
            interface,
            POINTER(IAudioEndpointVolume)
        )

        current = volume.GetMasterVolumeLevelScalar()

        if action == "up":

            new_volume = min(
                current + 0.10,
                1.0
            )

            volume.SetMasterVolumeLevelScalar(
                new_volume,
                None
            )

            speak("Volume increased.")

        elif action == "down":

            new_volume = max(
                current - 0.10,
                0.0
            )

            volume.SetMasterVolumeLevelScalar(
                new_volume,
                None
            )

            speak("Volume decreased.")

        elif action == "mute":

            volume.SetMute(1, None)

            speak("Volume muted.")

        elif action == "unmute":

            volume.SetMute(0, None)

            speak("Volume unmuted.")

    except Exception as e:

        print("Volume Error:", e)

        speak("I could not control the volume.")


# ==========================================
# SCREENSHOT
# ==========================================

def take_screenshot():

    try:

        filename = "jarvis_screenshot.png"

        screenshot = ImageGrab.grab()

        screenshot.save(filename)

        print("Screenshot saved as:", filename)

        speak("Screenshot taken successfully.")

    except Exception as e:

        print("Screenshot Error:", e)

        speak("I could not take the screenshot.")


# ==========================================
# OPEN FOLDER
# ==========================================

def open_folder(folder):

    try:

        paths = {

            "downloads":
                os.path.join(
                    os.path.expanduser("~"),
                    "Downloads"
                ),

            "documents":
                os.path.join(
                    os.path.expanduser("~"),
                    "Documents"
                ),

            "desktop":
                os.path.join(
                    os.path.expanduser("~"),
                    "Desktop"
                )
        }

        path = paths.get(folder)

        if path and os.path.exists(path):

            os.startfile(path)

            speak(f"Opening {folder}")

        else:

            speak(
                f"I could not find the {folder} folder."
            )

    except Exception as e:

        print("Folder Error:", e)

        speak("I could not open that folder.")


# ==========================================
# FIND FILE
# ==========================================

def find_file(filename):

    home = os.path.expanduser("~")

    search_folders = [

        os.path.join(home, "Desktop"),

        os.path.join(home, "Documents"),

        os.path.join(home, "Downloads")
    ]

    print(f"Searching for: {filename}")

    found = []

    for folder in search_folders:

        if not os.path.exists(folder):
            continue

        for root, dirs, files in os.walk(folder):

            for file in files:

                if filename.lower() in file.lower():

                    found.append(
                        os.path.join(root, file)
                    )

    if found:

        print("\nFiles found:")

        for file in found[:5]:

            print(file)

        speak(
            f"I found {len(found)} matching files."
        )

    else:

        speak(
            f"I could not find {filename}."
        )


# ==========================================
# LOCK PC
# ==========================================

def lock_pc():

    speak("Locking your computer.")

    ctypes.windll.user32.LockWorkStation()


# ==========================================
# SHUTDOWN / RESTART
# ==========================================

def system_action(action):

    speak(
        f"Are you sure you want to {action} the computer?"
    )

    confirmation = listen()

    if (
        "yes" in confirmation
        or "confirm" in confirmation
    ):

        if action == "shutdown":

            speak("Shutting down the computer.")

            os.system("shutdown /s /t 5")

        elif action == "restart":

            speak("Restarting the computer.")

            os.system("shutdown /r /t 5")

    else:

        speak("Okay, I cancelled the action.")


# ==========================================
# FOCUS MODE
# ==========================================

def start_focus_mode():

    global focus_end_time
    global focus_active

    focus_active = True

    focus_end_time = time.time() + (50 * 60)

    speak(
        "Focus mode activated. "
        "You have 50 minutes. Stay focused."
    )

    def timer():

        global focus_end_time
        global focus_active

        time.sleep(50 * 60)

        focus_end_time = None

        focus_active = False

        speak(
            "Focus session complete. "
            "You can take a break now."
        )

    thread = threading.Thread(
        target=timer
    )

    thread.daemon = True

    thread.start()


# ==========================================
# MAIN JARVIS
# ==========================================

def jarvis():

    speak(
        "Jarvis is ready. "
        "Say hey Jarvis to wake me up."
    )

    while True:

        command = listen()

        # ==================================
        # NOTHING UNDERSTOOD
        # ==================================

        if command == "":
            continue


        # ==================================
        # WAKE WORD
        # ==================================

        if (
            "hey jarvis" not in command
            and "jarvis" not in command
        ):

            print("Jarvis is sleeping...")

            continue


        # ==================================
        # REMOVE WAKE WORD
        # ==================================

        command = command.replace(
            "hey jarvis",
            ""
        )

        command = command.replace(
            "jarvis",
            ""
        )

        command = command.strip()


        # ==================================
        # ONLY WAKE WORD
        # ==================================

        if command == "":

            speak(
                "Yes, how can I help you?"
            )

            continue


        # ==================================
        # HELLO
        # ==================================

        if (
            "hello" in command
            or "hi" in command
        ):

            speak(
                "Hello! How can I help you?"
            )


        # ==================================
        # STOP FOCUS MODE
        # ==================================

        elif "stop focus mode" in command:

            focus_active = False
            focus_end_time = None

            speak(
                "Focus mode stopped."
            )


        # ==================================
        # START FOCUS MODE
        # ==================================

        elif "start focus mode" in command:

            start_focus_mode()


        # ==================================
        # FOCUS TIME LEFT
        # ==================================

        elif (
            "how much time is left" in command
            or "time left" in command
            or "focus time" in command
        ):

            if focus_end_time is not None:

                remaining = int(
                    focus_end_time - time.time()
                )

                if remaining > 0:

                    minutes = remaining // 60

                    seconds = remaining % 60

                    speak(
                        f"You have {minutes} minutes "
                        f"and {seconds} seconds remaining."
                    )

                else:

                    speak(
                        "Your focus session is complete."
                    )

            else:

                speak(
                    "No focus session is currently active."
                )


        # ==================================
        # TIME
        # ==================================

        elif "time" in command:

            tell_time()


        # ==================================
        # DATE
        # ==================================

        elif "date" in command:

            tell_date()


        # ==================================
        # SHUTDOWN
        # ==================================

        elif "shutdown" in command:

            system_action("shutdown")


        # ==================================
        # RESTART
        # ==================================

        elif "restart" in command:

            system_action("restart")


        # ==================================
        # SCREENSHOT
        # ==================================

        elif (
            "take screenshot" in command
            or "screenshot" in command
        ):

            take_screenshot()


        # ==================================
        # YOUTUBE SEARCH
        # ==================================

        elif (
            "play" in command
            and "youtube" in command
        ):

            youtube_search(command)


        # ==================================
        # OPEN YOUTUBE
        # ==================================

        elif "open youtube" in command:

            open_youtube()


        # ==================================
        # OPEN GOOGLE
        # ==================================

        elif "open google" in command:

            open_google()


        # ==================================
        # GOOGLE SEARCH
        # ==================================

        elif "search google for" in command:

            google_search(command)


        elif "search for" in command:

            google_search(command)


        # ==================================
        # FIND FILE
        # ==================================

        elif "find " in command:

            filename = command.replace(
                "find ",
                ""
            ).strip()

            if filename:

                find_file(filename)

            else:

                speak(
                    "What file should I find?"
                )


        # ==================================
        # LOCK PC
        # ==================================

        elif (
            "lock my pc" in command
            or "lock computer" in command
        ):

            lock_pc()


        # ==================================
        # OPEN CHROME
        # ==================================

        elif "open chrome" in command:

            open_app("chrome")


        # ==================================
        # OPEN NOTEPAD
        # ==================================

        elif "open notepad" in command:

            open_app("notepad")


        # ==================================
        # OPEN CALCULATOR
        # ==================================

        elif "open calculator" in command:

            open_app("calc")


        # ==================================
        # VOLUME UP
        # ==================================

        elif (
            "volume up" in command
            or "increase volume" in command
        ):

            change_volume("up")


        # ==================================
        # VOLUME DOWN
        # ==================================

        elif (
            "volume down" in command
            or "decrease volume" in command
        ):

            change_volume("down")


        # ==================================
        # MUTE
        # ==================================

        elif "mute" in command:

            change_volume("mute")


        # ==================================
        # UNMUTE
        # ==================================

        elif "unmute" in command:

            change_volume("unmute")


        # ==================================
        # OPEN DOWNLOADS
        # ==================================

        elif "open downloads" in command:

            open_folder("downloads")


        # ==================================
        # OPEN DOCUMENTS
        # ==================================

        elif "open documents" in command:

            open_folder("documents")


        # ==================================
        # OPEN DESKTOP
        # ==================================

        elif "open desktop" in command:

            open_folder("desktop")


        # ==================================
        # EXIT
        # ==================================

        elif (
            "exit" in command
            or "quit" in command
            or "goodbye" in command
        ):

            speak(
                "Goodbye! See you later."
            )

            break


        # ==================================
        # AI
        # ==================================

        else:

            answer = ask_ai(command)

            speak(answer)


# ==========================================
# START JARVIS
# ==========================================

if __name__ == "__main__":

    jarvis()