import pickle
import string
import requests
from bs4 import BeautifulSoup
import re

# url
base_url = "http://api.genius.com"
# Genius_API_TOKEN: TOKEN authorized and provided by Genius API after signing up
headers = {'Authorization': 'Bearer qrcKcZhp5hgKj2a4rR4uzITeaI5GSOFxPe4oZ_EsPbCYijSjOst0z_ABCTPDw2Hp'}


def lyrics_to_dict(lyric_lists):
    '''
    Convert lyrical content (list of lists) to a dict and removes repeated values
    :param output from lyric pickle file
    :return: -unique dictionary where each key is a tuple('Song Title', 'Artists')
            dict values are a list of 3 elements being a
            string of lyrics, list of parenthetical values, list of bracket values

            -none dictionary for songs missing info
    '''

    assert isinstance(lyric_lists, list), "input is a list"
    assert all([isinstance(song, list) and len(song) == 3 for song in
                lyric_lists]), 'list elements are lists and contain title,artist,lyrics'
    assert all([isinstance(song_info, (str, type(None))) for song in lyric_lists for song_info in
                song]), 'list of list elements are strs or nonetype'

    lyric_dict = {}
    non_lyrics = {}
    for song in lyric_lists:
        if all([isinstance(song_inf, str) for song_inf in song]):
            paren = re.findall('\((.*?)\)', song[2])  # parses for parentheticals
            bracket = re.findall('\[(.*?)\]', song[2])  # parses for brackets
            parsed = re.sub('\[.*\]', '', re.sub('\(.*\)', '', song[2]))  # removes parentheticals and brackets
            title_author = song[0] + ', ' + song[1]
            lyric_dict[tuple(song[0:2])] = [title_author, parsed, paren, bracket]
        else:  # strip songs with none values
            non_lyrics[tuple(song[0:2])] = song[2]

    return lyric_dict, non_lyrics


def modify_name(name):
    """
    Moidfy the input string by only keeping letters and spaces
    :param name: input string wants to be modified
    :return: modified string
    """
    for char in name:
        if char not in string.ascii_letters:
            if char != ' ':
                if char != "\'":
                    name = name.replace(char, '')
    return name


def get_song_info(name, artist):
    """
    Try to search corresponding song information using Genius API
    :param name: Song name
    :param artist: Artist name
    :return: Corresponding Song Information if found
             else return None
    """
    name = modify_name(name)
    response = requests.get(search_url+name.replace(' ','%20'), headers=headers)
    json = response.json()
    song_info = None
    for hit in json["response"]["hits"]:
        hit_artist = hit["result"]["primary_artist"]["name"]
        if hit_artist == artist:
            song_info = hit
            break
        elif len(hit_artist) <= len(artist):
            if hit_artist in artist:
                song_info = hit
                break
        elif artist in hit_artist:
            song_info = hit
            break
    return song_info


def lyrics_from_song_api_path(song_api_path):
    """
    Scrape Lyrics from Song API Path
    :param song_api_path
    :return: string of lyrics
    """
    song_url = base_url + song_api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    # html scrapping
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    lyrics = html.find("div", class_="lyrics").get_text() #updated css where the lyrics are based in HTML
    return lyrics


def load_files(fname):
    """
    :param fname: file name of Lyrics
    :return: Lyrics_Set: List of [Song, Artist, Lyrics]
             exist: List of Exist Songs
             fail: List of Failed Songs
             data: Billboard Weekly Top 100, data scrapped from billboard_scrapping
    """
    data = pickle.load(open('Songs',"rb"))
    total_week = len(data)
    print('total weeks',total_week)
    try:
        exist = pickle.load(open('exist',"rb"))
        data = data[exist[0]:total_week]
    except:
        exist = []
        exist.append(0)

    try:
        Lyrics_Set = pickle.load(open(fname,"rb"))
    except:
        Lyrics_Set = []

    try:
        fail = pickle.load(open('fail',"rb"))
    except:
        fail = []

    return Lyrics_Set, exist, fail, data


def save_files(fname,Lyrics_Set, exist, fail):
    """
    save files
    :param fname: file name of Lyrics
    :param Lyrics_Set: List of [Song, Artist, Lyrics]
    :param exist: List of Exist Songs
    :param fail: Billboard Weekly Top 100, data scrapped from billboard_scrapping
    """
    with open(fname, 'wb') as f:
        pickle.dump(Lyrics_Set, f)

    with open('exist', 'wb') as f:
        pickle.dump(exist, f)

    with open('fail', 'wb') as f:
        pickle.dump(fail, f)

def get_song(Song):
    """
    Using different kind of searching method trying to obtain song information
    :param Song: [Song name, Artist name]
    :return: Corresponding Song Information if found
    """
    song_name = Song[0]
    artist = Song[1]
    # get song info
    song_info = get_song_info(song_name, artist)
    if song_info:
        return song_info

    # search by song + artist
    song_info = get_song_info(song_name + ' ' + artist, artist)
    if song_info:
        return song_info

    # delete words between bracket
    if '(' in song_name:
        song_name = re.sub(r'\([^)]*\)', '', song_name)
        song_info = get_song_info(song_name + ' ' + artist, artist)
    if song_info:
        return song_info

    # shorten song_name by ('and', '&', 'with')
    song_name = song_name.lower()
    if 'and' in artist:
        SongName = song_name.split('And', 1)[0]
        song_info = get_song_info(SongName + ' ' + artist, artist)
    if song_info:
        return song_info

    if '&' in artist:
        SongName = song_name.split('&', 1)[0]
        song_info = get_song_info(SongName + ' ' + artist, artist)
    if song_info:
        return song_info

    if 'with' in artist:
        SongName = song_name.split('with', 1)[0]
        song_info = get_song_info(SongName + ' ' + artist, artist)
    if song_info:
        return song_info

    # shorten artist name by ('and', '&', 'with')
    artist = artist.lower()
    if 'and' in artist:
        Artist = artist.split('And', 1)[0]
        song_info = get_song_info(song_name + ' ' + Artist, Artist)
    if song_info:
        return song_info

    if '&' in artist:
        Artist = artist.split('&', 1)[0]
        song_info = get_song_info(song_name + ' ' + Artist, Artist)
    if song_info:
        return song_info

    if 'with' in artist:
        Artist = artist.split('with', 1)[0]
        song_info = get_song_info(song_name + ' ' + Artist, Artist)
    if song_info:
        return song_info
    print(f'Unable to scrap {song_name}')
    return song_info

if __name__ == "__main__":
    search_url = base_url+"/search?q="
    fname = 'Lyrics'
    Lyrics_Set, exist, fail, data = load_files(fname)

    for week in data:
        for i in range(1, 101):
            # Check if index out of range
            try:
                Song = week[i]
            except KeyError:
                break

            # Check if Song exist
            if len(exist) > 501:
                EX = exist[-500:-1]
            else:
                EX = exist

            if Song in EX:
                continue

            exist.append(Song)

            # Scrape Lyrics
            song_info = get_song(Song)
            if song_info:
                print(Song, 'Success')
                song_api_path = song_info["result"]["api_path"]
                lyrics = lyrics_from_song_api_path(song_api_path)
                Song.append(lyrics)
                Lyrics_Set.append(Song)
            else:
                fail.append(Song)
                with open('fail_log.txt', 'a') as f:
                    f.writelines('--------------------------------------------------\n')
                    f.writelines('Song Name: '+Song[0]+'\n'+'Artist: '+Song[1]+'\n')
                    f.close()

        # count the number of songs
        exist[0] += 1
        print(f'{exist[0]} week finished')
        # save files
        save_files(fname, Lyrics_Set, exist, fail)

    # Convert Lyrics Set into dictionary
    Lyrics = lyrics_to_dict(Lyrics_Set)
    with open('Lyrics_Dict', 'wb') as f:
        pickle.dump(Lyrics, f)
    print('lyrics scraping finished')



