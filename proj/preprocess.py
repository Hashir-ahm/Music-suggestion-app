import os
import pandas as pd
import librosa
import numpy as np
from pymongo import MongoClient

mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['music_features']
mongo_collection = mongo_db['mfcc_data']

music_folder = 'music_collection'

music_df = pd.read_csv('tracks.csv', skiprows=2, header=0)
music_df = music_df[['title', 't_id', 'genres_all']]

def compute_mfcc(audio_path):
    audio, sample_rate = librosa.load(audio_path, sr=20000)
    mfcc_features = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
    mfcc_means = np.mean(mfcc_features, axis=1)
    return mfcc_means.tolist()

for root, dirs, files in os.walk(music_folder):
    for music_file in files:
        if music_file.endswith('.mp3'):
            try:
                t_id = str(music_file.split('.')[0].lstrip('0'))
                t_info = music_df[music_df['t_id'] == t_id]
                
                if not t_info.empty:
                    genre = t_info['genres_all'].iloc[0]
                    title = t_info['title'].iloc[0]

                    audio_path = os.path.join(root, music_file)
                    mfcc_data = compute_mfcc(audio_path)

                    music_data = {
                        't_id': music_file,
                        'genre_all': genre,
                        'title': title,
                        'mfcc_features': mfcc_data
                    }
                    mongo_collection.insert_one(music_data)
                    print(f"mfcc feature that are store are  {audio_path} in MongoDB.")
                else:
                    print(f"track no match find for  {t_id}")
            except Exception as error:
                print(f"there is error in process of  {music_file}: {error}")