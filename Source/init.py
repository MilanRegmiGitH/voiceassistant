import tkinter as tk
from tkinter import messagebox
import threading
import pyttsx3
import speech_recognition as sr
import requests
import spotipy
import re
import sympy as sp
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

def speak(text):
    print(text)
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return None

def get_weather(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        main = data["main"]
        weather_description = data["weather"][0]["description"]
        temperature = main["temp"]
        humidity = main["humidity"]
        weather_report = (f"Temperature: {temperature}°C\n"
                          f"Humidity: {humidity}%\n"
                          f"Description: {weather_description}")
        return weather_report
    else:
        return "City not found."

def get_movie_recommendations():
    api_key = os.getenv("TMDB_API_KEY")
    url =  f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    recommendations = [movie['title'] for movie in data['results'][:5]]
    return recommendations

def get_game_recommendations():
    api_key = os.getenv("RAWG_API_KEY")
    url = f"https://api.rawg.io/api/games?key={api_key}"
    response = requests.get(url)
    data = response.json()
    recommendations = [game['name'] for game in data['results'][:5]]
    return recommendations

def get_song_recommendations():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    results = sp.recommendations(seed_genres=['pop'], limit=5)
    recommendations = [track['name'] for track in results['tracks']]
    return recommendations

def evaluate_math_expression(expression):
    try:
        result = sp.sympify(expression)
        return result
    except sp.SympifyError:
        return "Invalid mathematical expression"

def search_web(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()
    if 'AbstractText' in data and data['AbstractText']:
        return data['AbstractText']
    elif 'RelatedTopics' in data and data['RelatedTopics']:
        return data['RelatedTopics'][0]['Text']
    else:
        return "I couldn't find any information on that."

def open_application(app_name):
    if "discord" in app_name:
        os.system(r'start "" "%LOCALAPPDATA%\Discord\Update.exe" --processStart "Discord.exe"')
    elif "browser" in app_name or "web browser" in app_name or "chrome" in app_name or "microsoft edge" in app_name:
        os.system("start https://www.google.com")
    elif "notepad" in app_name:
        os.system("start notepad")
    elif "viber" in app_name:
        os.system(r'start "" "C:\Users\hp\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Viber" ')
    elif "calculator" in app_name:
        os.system("start calc")
    else:
        speak(f"Sorry, I can't open {app_name} yet.")

    

def handle_command(command):
    if not command:
        return True
    command = command.lower()

    if "hello" in command:
        speak("Hello! How can I help you?")
    elif "your name" in command:
        speak("I am Lila.")
    elif "time" in command:
        from datetime import datetime
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        speak(f"The current time is {current_time}")
    elif "your age" in command:
        speak("I am not sure of what age means.I am timeless")
    elif "weather" in command:
        speak("Which city?")
        done = False
        while done == False:
            city = listen()
            if city:
                weather_report = get_weather(city)
                speak(weather_report)
                done = True
    elif "recommend movie" in command or "recommend movies" in command or "movies" in command:
        movies = get_movie_recommendations()
        speak("Here are some movie recommendations:   " + ", ".join(movies))
    elif "recommend music" in command or "recommend song" in command or "recommend songs" in command or "songs" in command:
        songs = get_song_recommendations()
        speak("Here are some song recommendations:    " + "," .join(songs))
    elif "recommend game" in command or "recommend games" in command or "games" in command:
        games = get_game_recommendations()
        speak("Here are some game recommendations:   " + ", ".join(games))
    elif "open" in command:
        app_name = command.replace("open", "").strip()
        open_application(app_name)
    elif "stop" in  command or "goodbye" in command or "see you" in command or "bye" in command:
        speak("Goodbye!")
        return False
    else:
        math_expression = re.findall(r'[\d\.\+\-\*\/\(\)]+', command)
        if math_expression:
            expression = ''.join(math_expression)
            result = evaluate_math_expression(expression)
            speak(f"The result is {result}")
        else:
            search_result = search_web(command)
            speak(search_result)
    return True

# if __name__ == "__main__":
#     speak("Hello, how can I assist you today?")
#     active = True
#     while active:
#         command = listen()
#         if command:
#             active = handle_command(command)

class AwajApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Awaj - Voice Assistant")
        self.root.geometry("400x300")
        self.is_listening = False

        self.start_button = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=20)

        self.stop_button = tk.Button(root, text="Stop Listening", command=self.stop_listening)
        self.stop_button.pack(pady=20)

        self.output_label = tk.Label(root, text="", wraplength=300)
        self.output_label.pack(pady=20)
    
    def start_listening(self):
        self.is_listening = True
        self.output_label.config(text="Listening....")
        self.listen_thread = threading.Thread(target=self.listen_for_commands)
        self.listen_thread.start()
    
    def stop_listening(self):
        self.is_listening = False
        self.output_label.config(text="Stopped Listening")

    def listen_for_commands(self):
        while self.is_listening:
            command = listen()
            if command:
                self.output_label.config(text=f"You said: {command}")
                if not handle_command(command):
                    self.stop_listening()
                    break

if __name__ == "__main__":
    root = tk.Tk()
    app = AwajApp(root)
    root.mainloop()