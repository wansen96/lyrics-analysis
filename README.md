# Verbal Complexity of Popular Song Lyrics
UCSD ECE 143 Course Project Group 1

### Members: 
- Jordan Field 
- Wansen Zhang
- Yuekuan Luo
- Daniel Shak

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

# Structure of the Github Repo
There is only one folder besides the main directory, which is called 'Figs' and contains all of the figures that were used in our class presentation. 

Otherwise, the following files will be present in the main directory:

1. ```Songs```: a pickled Python file which is part of the dataset (more later)
2. ```Lyrics```: another pickled Python file which is part of the data
3. ```billboard_scraping.py```: a Python script which was used to collect the data in ```Songs```.
4. ```lyrics_scrp.py```: a Python script which was used to collect the data in ```Lyrics```, along with some other files.
5. ```lyrics_functions.py```: a module containing all of the functions that we have created in order to analyze the data. The usage of these will be explained more later.
6. ```notebook.ipynb```: a Jupyter Notebook which contains example usages of the data and functions, along with some useful data visualizations

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

1. ```Lyrics```: The primary data structure containing the lyrics
2. ```exist```: A list of the songs that have been seen in the billboard lists. This prevents duplicate lyrics
3. ```fail```: A list of the songs whose lyrics could not be obtained.
4. ```fail_log.txt```: A text version of 'fail', for easier reading

The first 3 files above were similarly saved using the ```pickle``` module. 

# Data Structure
### 'Songs':
'Songs' is the file in which the artist and song names are stored for the Billboard Top 100 lists. Specifically, 'Songs' is a pickled Python variable that should be loaded into your working directory like the following:

```sh
with open('Songs','rb') as f:
    songs = pickle.load(f)
```

Once loaded, you will have a list of dictionaries. Each dictionary has several keys. The most important is 'Week', which gives a timestamp for the song rankings associated with that week. This is the same way that the Billboard site organizes the rankings. From there, you have keys from '1' to '100', which return a list of the song and artist name associated with the ranking of the key ```([Song Name, Artist Name])```.

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
The values for each of these keys are lists of the following structure: ```['Song Name, Artist Name', 'Lyrics', [Strings within parentheses], [Strings within brackets]]```. For example:

```sh
lyric_dict[('Poor Little Fool', 'Ricky Nelson')]
```
will output:
```sh
['Poor Little Fool, Ricky Nelson',
 "\n\nI used to play around with hearts\nThat hastened at my call\nBut when I met that little girl\nI knew that I would fall\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\nShe played around and teased me\nWith her carefree devil eyes\nShe'd hold me close and kiss me\nBut her heart was full of lies\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\nShe told me how she cared for me\nAnd that we'd never part\nAnd so for the very first time\nI gave away my heart\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\nThe next day she was gone\nAnd I knew she'd lied to me\nShe left me with a broken heart\nAnd won her victory\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\nWell, I'd played this game with other hearts\nBut I never thought I'd see\nThe day that someone else would play\nLove's foolish game with me\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\nPoor little fool, oh yeah\nI was a fool, uh huh\n\n\n\n",
 ['Oh oh, poor little fool',
  'I was a fool, oh yeah',
  'Oh oh, poor little fool',
  'I was a fool, oh yeah',
  'Oh oh, poor little fool',
  'I was a fool, oh yeah',
  'Oh oh, poor little fool',
  'I was a fool, oh yeah',
  'Oh oh, poor little fool',
  'I was a fool, oh yeah',
  'Oh oh, poor little fool',
  'Poor little fool'],
 []]
 ```
 
In this case, there were no strings within brackets, but some genius lyrics include them, mostly as section headers (i.e. [Verse 1]). The parentheticals and bracketed strings were separated and mostly ignored in our own analysis, but they can be included if desired. 

### 'exist'
```exist``` is also a pickled Python variable with a simple structure once loaded. It is a list of lists, where each sublist is also a pair of: ```[Song Name, Artist Name]```. This variable was mostly used for the purpose of constructing ```Lyrics```, but we include it for your information.

### 'fail' and 'fail_log.txt'
```fail``` has the same structure as ```exist```, only now it is a record of the songs whose lyrics could not be found on genius.com through our search methods. If desired, you could look for the lyrics elsewhere, but our method gathers about 84% of the songs successfully as is. 

```fail_log.txt``` has the same information as ```fail```, but is provided for ease of viewing. 

It should be noted that the majority of the analysis will be done using ```Songs``` and ```Lyrics```. 

# How to Use Data and Analysis Functions
### Daniel, fill in this section. 
Talk about the functions and the general workflow, probably don't need to be super specific, we have docstrings.

# Example Usage and Data Visualization
Provided within this Repository is a Jupyter Notebook file called ```notebook_final.ipynb``` which will contain several instances of example usage of our analysis functions as well as some key visualizations for our presentation and conclusions. 

The notebook itself is well-documented, and should serve on its own without much further comment, but it is highly recommended that you look through the notebook, as it has many useful examples of how to use the data and functions. 

Note: Any created figures will be saved to a sub-directory called 'Figs' but you must have all of the other files within the working directory of the Jupyter Notebook for it to work properly. 