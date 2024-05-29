import pyttsx3
import speech_recognition as sr
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def speak(text):
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
    api_key = "e533079ea64cd0f3a99944e669f96f1e"
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
    api_key = "e62875cb06ff19cb5892360b45c1713c"
    url =  f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    recommendations = [movie['title'] for movie in data['results'][:5]]
    return recommendations

def get_game_recommendations():
    api_key = "87d36ca23c7e4c0292b1ad6463ccc21c"
    url = f"https://api.rawg.io/api/games?key={api_key}"
    response = requests.get(url)
    data = response.json()
    recommendations = [game['name'] for game in data['results'][:5]]
    return recommendations

def get_song_recommendations():
    client_id = "2830910abd894b2b9b2df0ffb5ca851e"
    client_secret = "392bc937881a409f9aae35e9c8727c5e"
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    results = sp.recommendations(seed_genres=['pop'], limit=5)
    recommendations = [track['name'] for track in results['tracks']]
    return recommendations
    

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
    elif "stop" in command:
        speak("Goodbye!")
        return False
    else:
        speak("I can not do that yet, but I am learning new things every day!")
    return True

if __name__ == "__main__":
    speak("Hello, how can I assist you today?")
    active = True
    while active:
        command = listen()
        if command:
            active = handle_command(command)
