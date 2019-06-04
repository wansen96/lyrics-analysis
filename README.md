# Verbal Complexity of Popular Song Lyrics
UCSD ECE 143 Course Project Group 1
Members: Jordan Field, Wansen Zhang, Yuekuan Luo, Daniel Shak

This GitHub repository contains code and data files for the end-term project of ECE 143 at UC San Diego. The project in question was designed in order to analyze the verbal complexity of popular song lyrics, as recorded by the Billboard Top 100 lists. 

There are a few files representing the data, as well as scripts for obtaining the dataset from scratch, if you should choose to do so. There is also a script containing various functions that can be used to analyze the data files, as well as a Jupyter Notebook contains several instances of example usage as well as data visualization.

# Package Dependencies
There are several 3rd-party packages used throughout the project, which are listed here:

- bs4
- requests
- pandas
- numpy
- wordcloud
- matplotlib

# Collecting the Data
There are 2 primary tasks involved in collecting our dataset:

1. Collecting the artist and song names from the Billboard website
2. Collecting the lyrics for these songs using the genius.com API

In order to achieve the first step, the ```billboard_scraping.py``` script must be used from the command line, similar to:

```sh
python billboard_scraping.py
```
This script will retrieve data from the Billboard Top 100 lists on billboard.com and save the data using the ```pickle``` module to your current directory under the name 'Songs'

In order to achieve the second step, the ```lyrics_scrp.py``` script will also be used in the command line, as follows:

```sh
python lyrics_scrp.py
```

This script uses web scraping alongside the API provided by genius.com in order to obtain the lyrics for the songs whose names and artists were gathered earlier. This script will save 4 files to your directory:

1. 'Lyrics': The primary data structure containing the lyrics
2. 'exist': A list of the songs that have been seen in the billboard lists. This prevents duplicate lyrics
3. 'fail': A list of the songs whose lyrics could not be obtained.
4. 'fail_log.txt': A text version of 'fail', for easier reading

The first 3 files above were similarly saved using the ```pickle``` module. 

# Data Structure
### 'Songs':
'Songs' is the file in which the artist and song names are stored for the Billboard Top 100 lists. Specifically, 'Songs' is a pickled Python variable that should be loaded into your working directory like the following:

```sh
with open('Songs','rb') as f:
    songs = pickle.load(f)
```

Once loaded, you will have a list of dictionaries. Each dictionary has several keys. The most important is 'Week', which gives a timestamp for the song rankings associated with that week. This is the same way that the Billboard site organizes the rankings. From there, you have keys from '1' to '100', which return a list of the song and artist name associated with the ranking of the key ([Song Name, Artist Name]).

For example:
```songs[0]``` will return:

```sh
{'Week': '1958-08-04',
 1: ['Poor Little Fool', 'Ricky Nelson'],
 2: ['Patricia', 'Perez Prado And His Orchestra'],
 3: ['Splish Splash', 'Bobby Darin']
 ...
 100: ['Judy', 'Frankie Vaughan']}
 ```

When the provided 'Songs' file in this GitHub Repository was created, the ```billboard_scraping.py``` script was run in order to obtain all Top 100 lists until the current list, which was ```May 11, 2019```. If you were to run the script for yourself, it would get all of the lists until whatever the current list is (hello future person!)

### 'Lyrics':

'Lyrics' is the file in which the lyrics of the songs are stored, and associated with the song and artist names. Like 'Songs', it is a pickled Python variable that should be loaded in the same way.

Once loaded, it will be a dictionary. The keys of the dictionary are tuples with the following structure: ```(Song Name, Artist Name)```
