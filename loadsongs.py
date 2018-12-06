import numpy as np
import matplotlib.pyplot as plt
import spotipy as sp
import spotipy.util as util
import os
import spotipy.oauth2 as oauth2


class Song():
# Song class contains useful information about a song including
# ident (str): Spotify song id
# name (str): Name of a song
# artists (str): Primary artist of a song
# bpm (float): beats per minute of a song as determined by Spotify audio analysis
# time (float): length of song (in seconds)
    def __init__(self, ident, name, artists, bpm, time = 0., num_plays = 0):
        self.ident = ident
        if isinstance(name, unicode):
            name = name.encode('utf-8').strip()
        self.name = name.replace('\t',' ')
        if isinstance(artists, unicode):
            artists = artists.encode('utf-8').strip()
        self.artists = artists.replace('\t', ' ')
        self.bpm = float(bpm)
        self.time = float(time)
        self.num_plays = num_plays

    def __eq__(self, other):
    # Overloaded == operator; if rhs is Song instance, check if Songs have equal idents
    # If rhs is string instance, check if self.ident == string
        if isinstance(other, Song):
            return self.ident == other.ident
        elif isinstance(other, str) or isinstance(other, unicode):
            return self.ident == other

class Playlist():
# Playlist class is a wrapper class for a np.array of Songs
# Contains several helper methods for managing this array
# songs (dict): dict of songs, key is the ident of the song
# size (ing): length of songs
    def __init__(self, songs = {}):
        self.songs = songs
        self.size = len(songs)

    def avg_bpm(self):
    # Returns average bpm of Songs in songs
        b = 0.
        for ident in self.songs:
            b += self.songs[ident].bpm

        return b/self.size

    def total_length(self):
    # Return total run time of songs (in seconds)
        return sum([self.songs[ident].time for ident in self.songs])

    def display_songs(self):
    # Prints all songs line-by-line
        for n,ident in enumerate(self.songs):
            print(str(n) + ": " + self.songs[ident].name + ", " + str(self.songs[ident].bpm)
                    + ", " + str(self.songs[ident].num_plays))

    def add_song(self, song):
    # If song not in songs, add it and return True
    # Else, return False
        if song.ident not in self:
            self.songs[song.ident] = song
            self.size += 1
            return True
        return False

    def remove_song(self, song):
    # If song is in songs, remove it and return True
    # Else, return False
        try:
            del self.songs[song.ident]
            self.size -= 1
            return True
        except KeyError:
            return False


    def __contains__(self, song):
    # Overloaded in operator
    # Checks if a song is contained by the Playlist
        if isinstance(song, str) or isinstance(song, unicode):
            return song in self.songs
        else:
            return song.ident in self.songs


    def __add__(self, other):
    # Overloaded + operator
    # If other is an instance of Song, add it to songs
    # If other is an instance of Playlist, add all songs in other.songs to songs
        if isinstance(other, Song):
            self.add_song(other)
        elif isinstance(other, Playlist):
            for s in other.songs:
                self.add_song(s)

        return self

    def __iadd__(self, other):
    # Overload += operator
    # Calls + on self and other
        return self + other

    def __sub__(self, other):
    # Overloaded - operator
    # If other is an instance of Song, remove it from songs
    # If other is an instance of Playlist, remove all songs in other.songs to songs
        if isinstance(other, Song):
            self.remove_song(other)
        elif isinstance(other, Playlist):
            for s in other.songs:
                self.remove_song(s)

        return self

    def __isub__(self, other):
    # Overloaded -= operator
    # Calls - on self and other
        return self - other

    def __getitem__(self, index):
    # Overloaded indexing operator for easy access to songs from outside
        return self.songs[index]

def get_authorized():
# Returns an instance of Spotify with an authorized token
    try:
        client_id = os.environ['SPOTIPY_CLIENT_ID']
        client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
        redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
        username = 'skycrab'
        scope = 'user-modify-playback-state'

        token = util.prompt_for_user_token(username, scope, client_id,
                                           client_secret, redirect_uri)
    except:
        credentials = oauth2.SpotifyClientCredentials(
               client_id=client_id,
               client_secret=client_secret)

        token = credentials.get_access_token()
    return sp.Spotify(auth=token)

def load_playlist():
# Returns a Playlist containing every song written in songs.txt
    my_playlist = Playlist()
    try:
    # If songs.txt is found, load all songs
        with open("songs.txt","r") as f:
            lines = f.readlines()

            for line in lines[1:]:
                l = [k.strip() for k in line.split('\t')]
                my_playlist += Song(l[0],l[1],l[2],l[3],0)

    except IOError:
    # Couldn't find songs.txt, don't bother
        pass
    return my_playlist

def save_playlist(my_playlist):
# Converts a Playlist object into a .txt file
    songs = [my_playlist.songs[i] for i in my_playlist.songs]
    ids = [s.ident for s in songs]
    names = [s.name for s in songs]
    artists = [s.artists for s in songs]
    bpm = [s.bpm for s in songs]
    num_plays = [s.num_plays for s in songs]

    idfmt = "{:<24}"
    namefmt = "{:<30}"
    artistfmt = "{:<30}"
    bpmfmt = "{:<5}"
    numfmt = "{:<3}"

    with open('songs.txt','w') as f:
        f.write(idfmt.format("Song ID") + namefmt.format("Name")
                + artistfmt.format("Artist") + bpmfmt.format("BPM") + '\n')
        for n,i in enumerate(ids):
            f.write(idfmt.format(ids[n]) + '\t')
            f.write(namefmt.format(names[n]) + '\t')
            f.write(artistfmt.format(artists[n]) + '\t')
            f.write(bpmfmt.format(str(bpm[n])) + '\t')
            f.write(numfmt.format(str(num_plays[n])) + '\n')

def get_num_plays(spotify, username, playlist):
    playlists = spotify.user_playlists(username)
    for ident in playlist.songs:
        playlist[ident].num_plays = 0

    for i in playlists['items']:
        if i['name'][0:8] == "Bwestie ":
            tracks = spotify.user_playlist(username, i['id'], fields="tracks,next")['tracks']
            for item in tracks:
                track = item['track']
                if track['id'] in playlist:
                    playlist[track['id']].num_plays += 1
        while tracks['next']:
            tracks = spotify.next(tracks)
            for item in tracks:
                track = item['track']
                if track['id'] in playlist:
                    playlist[track['id']].num_plays += 1


def get_playlist(spotify, name, username, my_playlist = Playlist()):
# Given a username and a playlist name, returns a Playlist object containing all songs
# contained in the Spotify playlist. If my_playlist is passed, will only add songs not
# already contained in my_playlist
    playlists = spotify.user_playlists(username)
    playlist = None

    # Finding specific playlist
    for i in playlists['items']:
        if i['name'] == name:
            playlist = spotify.user_playlist(username, i['id'], fields="tracks,next") 
    # If playlist is found, load songs from it
    if playlist != None:
        tracks = playlist['tracks']


        # Loading tracks from Playlist
        for item in tracks['items']:
            track = item['track']
            if track['id'] not in my_playlist:
                my_playlist += Song(track['id'], track['name'],
                    track['artists'][0]['name'], 
                    spotify.audio_features(tracks=[track['id']])[0]['tempo'])


        while tracks['next']:
            tracks = spotify.next(tracks)
            for item in tracks['items']:
                track = item['track']
                if track['id'] not in my_playlist:
                    my_playlist += Song(track['id'], track['name'],
                        track['artists'][0]['name'], 
                        np.round(spotify.audio_features(tracks=[track['id']])[0]['tempo']))
    # If playlist is not found, return empty Playlist and print a message
    else:
        print(name + " was not found.")

    return my_playlist



def main():
    spotify = get_authorized()

    username = 'skycrab'
    my_playlist = load_playlist()
    archived = ['Westie', 'Westie (Fast)', 'Westie (Slow)']

    for playlist in archived:
        my_playlist = get_playlist(spotify, playlist, username, my_playlist)

    get_num_plays(spotify, username, my_playlist)
    my_playlist.display_songs()
    save_playlist(my_playlist)


if __name__ == "__main__":
    main()








