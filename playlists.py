import loadsongs
import numpy as np
import random

def get_slow_song(all_songs, b):
# Finds and returns a random song with bpm less than b
    w = np.zeros(all_songs.size)
    for n,s in enumerate(all_songs):
        if s.bpm < b:
            w[n] = True

    indices = np.where(w)[0]
    return all_songs[indices[random.randint(0, indices.size-1)]]

def get_fast_song(all_songs, b):
# Finds and returns a random song in all_songs with bpm greater than b
    w = np.zeros(all_songs.size)
    for n,s in enumerate(all_songs):
        if s.bpm > b:
            w[n] = True

    indices = np.where(w)[0]
    return all_songs[indices[random.randint(0, indices.size-1)]]

def gen_playlist(b,N, bstd = 10):
# Returns a playlist containing N songs with an average bpm within bstd (default 10) of b
    spotify = loadsongs.get_authorized()
    username = "skycrab"
    all_songs = loadsongs.load_playlist()
    starter_songs = loadsongs.get_playlist(spotify, "Starter Songs", username)
    my_playlist = loadsongs.Playlist(starter_songs[random.sample(range(0, starter_songs.size-1), 5)])

    while my_playlist.size < N or np.abs(b - my_playlist.avg_bpm()) > bstd:

        # Randomly remove a song that is too fast or too slow
        if my_playlist.size >= N:
            sgn = np.sign(s.bpm - b)
            w = np.zeros(my_playlist.size)
            for n,s in enumerate(my_playlist.songs):
                if s.bpm > b + sgn*bstd:
                    w[n] = True
                indices = np.where(w)[0]
                randind = indices[random.randint(0, indices.size-1)]

                my_playlist -= my_playlist.songs[randind]

        if my_playlist.avg_bpm() > b: # Too fast
            my_playlist += get_slow_song(all_songs, b-bstd)
        else: # Too slow
            my_playlist += get_fast_song(all_songs, b+bstd)

    return my_playlist

def main():
    spotify = loadsongs.get_authorized()
    pl = gen_playlist(100, 30)
    pl.display_songs()
    print(pl.avg_bpm())

if __name__ == "__main__":
    main()
