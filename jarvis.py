import os
import speech_recognition as sr
from gtts import gTTS
import datetime
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib.parse
import requests
import re
import threading
import time
from playsound import playsound

# Spotify API credentials
SPOTIPY_CLIENT_ID = '585a0d1699fc474f981a4d9be9161ed0'
SPOTIPY_CLIENT_SECRET = '1dfd2766fae149a49c692b32368ffdb5'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read user-read-playback-state user-modify-playback-state'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=SCOPE))

# Function to speak text
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")
    playsound("output.mp3")
    os.remove("output.mp3")

# Function to get user input through voice
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)  # Timeout to avoid hanging
            query = recognizer.recognize_google(audio)
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError:
            speak("Sorry, I'm having trouble connecting to the service.")
            return None

# Function to handle commands
def handle_command(command):
    if 'hello' in command:
        speak("Hello! How can I assist you today?")
    elif 'what time' in command:
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        speak(f"The time is {time_str}")
    elif 'play spotify' in command:
        speak("Opening Spotify.")
        webbrowser.open("https://open.spotify.com/")
    elif 'play' in command and 'on spotify' in command:
        song_name = command.split('play', 1)[1].split('on spotify', 1)[0].strip()
        if song_name:
            search_and_play_song(song_name)
        else:
            speak("Please specify the song you want to play.")
    elif 'play' in command and 'on youtube' in command:
        video_name = command.split('play', 1)[1].split('on youtube', 1)[0].strip()
        if video_name:
            search_and_play_youtube_video(video_name)
        else:
            speak("Please specify the video you want to play.")
    elif 'search' in command:
        query = command.split('search', 1)[1].strip()
        if query:
            search_google(query)
        else:
            speak("Please specify what you want to search for.")
    elif 'exit' in command:
        speak("Goodbye!")
        return True
    else:
        speak("Sorry, I didn't catch that.")
    return False

# Function to search Google
def search_google(query):
    query = urllib.parse.quote(query)
    search_url = f"https://www.google.com/search?q={query}"
    speak(f"Searching Google for {query}.")
    webbrowser.open(search_url)

# Function to search for a song on Spotify and autoplay it
def search_and_play_song(song_name):
    results = sp.search(q=song_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        speak(f"Playing {track['name']} by {track['artists'][0]['name']}.")
        sp.start_playback(uris=[track['uri']])
    else:
        speak("Sorry, I couldn't find that song.")

# Function to search for a video on YouTube and autoplay it
def search_and_play_youtube_video(video_name):
    query = urllib.parse.quote(video_name)
    video_id = get_youtube_video_id(query)
    if video_id:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        speak(f"Opening YouTube and playing {video_name}.")
        webbrowser.open(youtube_url)
    else:
        speak("Sorry, I couldn't find that video.")

# Function to get YouTube video ID from search query
def get_youtube_video_id(query):
    search_url = f"https://www.youtube.com/results?search_query={query}"
    html = requests.get(search_url).text
    video_id = re.findall(r'watch\?v=(\S{11})', html)
    if video_id:
        return video_id[0]
    else:
        return None

# Function to periodically ask if help is needed
def periodic_check():
    while True:
        time.sleep(1800)  # Sleep for 30 minutes
        speak("Do you need any help?")

# Main function
def main():
    speak("What's up Saad? Jenny Here. What can I do for you? Want music or something to search?")
    
    # Start periodic check in a separate thread
    threading.Thread(target=periodic_check, daemon=True).start()
    
    while True:
        command = listen()
        if command:
            if handle_command(command):
                break

if __name__ == "__main__":
    main()
