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
from PIL import Image, ImageTk
import os

load_dotenv()

# Initialize the pyttsx3 engine globally
engine = pyttsx3.init()
engine_lock = threading.Lock() # create a lock for the speech engine

#function to speak using text using pyttsx3 
def speak(text):
    with engine_lock: # Ensure that only one thread can access the engine at a time
        print(text)
        engine.say(text)
        engine.runAndWait()

# Function to listen for voice commands using speech recognition
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
        
# get weather information using the openweather api key
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

#get movie recommendations using TMDB api key 
def get_movie_recommendations():
    api_key = os.getenv("TMDB_API_KEY")
    url =  f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    recommendations = [movie['title'] for movie in data['results'][:5]]
    return recommendations

#uses Rawg api key to get  game recommendations 
def get_game_recommendations():
    api_key = os.getenv("RAWG_API_KEY")
    url = f"https://api.rawg.io/api/games?key={api_key}"
    response = requests.get(url)
    data = response.json()
    recommendations = [game['name'] for game in data['results'][:5]]
    return recommendations

#Uses spotify api to get the song recommendations
def get_song_recommendations():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    results = sp.recommendations(seed_genres=['pop'], limit=5)
    recommendations = [track['name'] for track in results['tracks']]
    return recommendations

#Takes mathematical expression and returns the result using smpy 
def evaluate_math_expression(expression):
    try:
        result = sp.sympify(expression)
        return result
    except sp.SympifyError:
        return "Invalid mathematical expression"

# Function to search the web using duck duck go api
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

# Function to open application in native os
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


class AwajApp:
    def __init__(self, root):
        #Initialize the main window and GUI elements
        self.root = root
        self.root.title("Awaj - Voice Assistant")
        self.root.geometry("600x400")
        self.root.minsize(600, 400)  
        self.is_listening = False
        self.dark_mode = False
        self.listening_lock = threading.Lock() # lock to manage the listening state
        self.listening_thread = None

        #load animation frames for the listening animation 
        self.animation_frames = [self.load_image(f"./voiceassistant/assets/animation/frame_{i}.png", self.dark_mode) for i in range(1, 5)]
        self.current_frame = 0

        #Initialize gui elements
        self.animation_label = tk.Label(root)
        self.animation_label.place_forget()

        self.start_button = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_button.place(relx=0.5, rely=0.1, anchor="center")

        self.stop_button = tk.Button(root, text="Stop Listening", command=self.stop_listening)
        self.stop_button.place(relx=0.5, rely=0.5, anchor="center")
        
        #load images for dark and light mode toggle
        self.light_image = self.load_image("./voiceassistant/assets/light_mode.png", False)
        self.dark_image = self.load_image("./voiceassistant/assets/dark_mode.png", True)
        self.toggle_button = tk.Button(root, image=self.light_image, command=self.toggle_dark_mode, borderwidth=0)
        self.toggle_button.place(relx=1.0, rely=0, anchor="ne")

        self.output_label = tk.Label(root, text="", wraplength=300)
        self.output_label.place(relx=0.5, rely=0.6, anchor="center")

        self.animate_id = None

    #Function to load an image and apply background color
    def load_image(self, path, is_dark_mode):
        # Load the image with PIL and apply background color based on mode
        image = Image.open(path)
        if is_dark_mode:
            background = Image.new('RGBA', image.size, (0, 0, 0))
        else:
            background = Image.new('RGBA', image.size, (255, 255, 255))
        
        # Paste the image on the background to apply the background color
        background.paste(image, (0, 0), image)
        return ImageTk.PhotoImage(background)
    
    #Function to toggle between dark and light mode
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.update_ui_mode()

    #Function to update GUI elements based on dark/light mode
    def update_ui_mode(self):
        if self.dark_mode:
            self.root.config(bg="black")
            self.start_button.config(bg="black", fg="white")
            self.stop_button.config(bg="black", fg="white")
            self.output_label.config(bg="black", fg="white")
            self.toggle_button.config(image=self.dark_image)
            #load animation frames with dark mode theme 
            self.animation_frames = [self.load_image(f"./voiceassistant/assets/animation/frame_{i}.png", True) for i in range(1, 5)]
        else:
            self.root.config(bg="white")
            self.start_button.config(bg="white", fg="black")
            self.stop_button.config(bg="white", fg="black")
            self.output_label.config(bg="white", fg="black")
            self.toggle_button.config(image=self.light_image)
            #load animation frames with light mode theme 
            self.animation_frames = [self.load_image(f"./voiceassistant/assets/animation/frame_{i}.png", False) for i in range(1, 5)]

    # Function to start listening for voice commands
    def start_listening(self):
        with self.listening_lock:
            if self.is_listening:
                return
            self.is_listening = True
            self.animation_label.place(relx=0.5, rely=0.3, anchor="center")
            self.animate()  # Start the animation
            self.listening_thread = threading.Thread(target=self.listen_loop)
            self.listening_thread.start()

    #Funtion to stop listening for voice commands
    def stop_listening(self):
        with self.listening_lock:
            self.is_listening = False
            self.animation_label.place_forget()
            if self.animate_id is not None:
                self.root.after_cancel(self.animate_id)
                self.animate_id = None
    # Function to continuously listen for voice commands
    def listen_loop(self):
        while True:
            with self.listening_lock:
                if not self.is_listening:
                    break
            command = listen()
            if command:
                self.output_label.config(text=f"You said: {command}")
                if not handle_command(command):
                    break
    # Function to animate the listening animation
    def animate(self):
        if not self.is_listening:
            return
        self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
        self.animation_label.config(image=self.animation_frames[self.current_frame])
        self.animate_id = self.root.after(200, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = AwajApp(root)
    root.mainloop()
