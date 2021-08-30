import sqlalchemy
import pandas as pd 
from sqlalchemy.orm import sessionmaker
import requests
import json
from datetime import datetime
import datetime
import sqlite3
import pymongo

mongoclient = pymongo.MongoClient("mongodb://localhost:27017/")

data_lake = mongoclient["raw_spotify"]
DATABASE_LOCATION = "sqlite:///my_daily_tracks.sqlite"
USER_ID = "asamirr" # your Spotify username 
TOKEN = "BQAkWMwtziPfics-soeFOGZbTS0eSJ2ux_RIS-s7JIETENICQWuX1zCrDG59Np0QwHx4AVjQCKdEwnBze5YCxk35PKwVW7zEa3rsogs8jUEQHP7kPUmw3QYVsEtyMDOSYaie_txH9JKT" # your Spotify API token

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False 

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are of yesterday's date
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        if datetime.datetime.strptime(timestamp, '%Y-%m-%d') != yesterday:
            raise Exception("At least one of the returned songs does not have a yesterday's timestamp")

    return True

if __name__ == "__main__":
    headers = {
        "Accept": "application/json",
        "Content_Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers=headers)
    
    data = r.json()
    
    with open('raw_data.json', 'w+') as f:
        json.dump(data, f)
    collection = data_lake["raw_" + datetime.datetime.now().strftime('%d-%m-%Y')]
    with open('raw_data.json') as f:
        json_file_data = json.load(f)
    
    collection.insert_one(json_file_data)

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        
    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    with open('clean_data.csv', 'a') as f:
        song_df.to_csv(f, mode='a', header=f.tell() == 0, index=False)
    
    # print(song_df)
    if check_if_valid_data(song_df):
        print("Data valid! Now go and load the shit out of it!")

    # Load

    engine = sqlalchemy.create_engine(DATABASE_LOCATION)
    conn = sqlite3.connect('my_daily_tracks.sqlite')
    cursor = conn.cursor()

    sql_query = """
        CREATE TABLE IF NOT EXISTS my_daily_tracks(
            song_name VARCHAR(200),
            artist_name VARCHAR(200),
            played_at VARCHAR(200),
            timestamp VARCHAR(200),
            CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
        )        
    """
    cursor.execute(sql_query)
    print("Opened database successfully")

    try:
        song_df.to_sql("my_daily_tracks", engine, if_exists='append', index=False)
    except:
        print("Data already exists in the database")
    conn.close()

    print("Close database successfully")