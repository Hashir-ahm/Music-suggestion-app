import os
from flask import Flask, render_template, send_file

web_app = Flask(name)

# Function to retrieve MP3 filenames from music_files.txt
def get_mp3_filenames(file_list):
    with open(file_list, 'r') as file:
        mp3_filenames = [line.strip() for line in file.readlines()]
    return mp3_filenames

# Funct for path
def find_mp3_path(root_directory, file_name):
    for folder, subdirs, files in os.walk(root_directory):
        if file_name in files:
            return os.path.join(folder, file_name)
    return None

# Route to render the home page with a list of MP3 files
@web_app.route('/')
def home():
    mp3_filenames = get_mp3_filenames('tracks.txt')
    return render_template('home.html', mp3_files=mp3_filenames)

# Route to play an MP3 file
@web_app.route('/play/<filename>')
def play_music(filename):
    music_directory = "music_collection"  # Specify the root directory to search in
    music_path = find_mp3_path(music_directory, filename)
    if music_path:
        return send_file(music_path)
    else:
        return "there is no file", 404

if name == 'main':
    web_app.run(debug=True)