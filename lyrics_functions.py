import pickle
import re
import pandas as pd
import string
import time
import numpy as np
from collections import Counter

'''
API to deal with the web scrapped data structures.
Workflow follows as:
    billboard_scraping.py -> lyrics_scrp.py -> data structures to use with lyrics_functions.py
'''

def to_timeframe(song_list,lyric_dict,timeframe='year'):
    '''
    gathers all information for specific timeframes (week, month, year, decade)
    
    Input:
        song_list - the list of dictionaries loaded from the unpickled file data_final, further description below of this format
        lyric_dict - dictionary of unique songs, generated from function lyrics_to_dict()
        timeframe - indiates over which timeperiod to get the stats, ['week','month','year', 'decade']
        
    Output:
        dict_out - dictionary of dictionaries, first dict keys are the timeperiods - values are dicts
        	second dict keys are ['num_songs',titles_authors','lyrics','words','parens','bracketed'] - 
        
    iterate over binned output to generate stats for each bin, where a bin is a timeframe
    '''
    assert isinstance(song_list,list)
    assert all([isinstance(week,dict) for week in song_list])
    
    assert isinstance(lyric_dict,dict)
    assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(lyric_dict.values(),lyric_dict.keys())])
    
    assert any([timeframe == period for period in ['week','month','year', 'decade']])
    
    time = {'year':0, 'month':1, 'week':2, 'decade':0}[timeframe]   
    binned = {}
    current_time = -1
    
    translator = str.maketrans('','',string.punctuation) #remove punctuation
    trans_newline = str.maketrans('\n',' ') #replace newline with space
    
    for i, week in enumerate(song_list):
        tf = '-'.join(week['Week'].split('-')[0:time+1])
        if timeframe == 'decade':
            tf = tf[0:3]+"0s"
        #print(tf)
        if tf != current_time: #create new bin
            binned[tf] = {}
            binned[tf]['num_songs'] = 0
            binned[tf]['titles_authors'] = []
            binned[tf]['lyrics'] = []
            binned[tf]['parens'] = []
            binned[tf]['bracketed'] = []
            binned[tf]['words'] = []
            binned[tf]['unique_words'] = []
            
            
            if i!= 0:#Change from string concatenation since slow, new method is append to lists then join
                #Check here for more info:
                #https://stackoverflow.com/questions/3055477/how-slow-is-pythons-string-concatenation-vs-str-join
                binned[current_time]['lyrics'] = ''.join(binned[current_time]['lyrics'])

        for song in week.values(): #update values for specific tf
            if isinstance(song,list) and tuple(song) in lyric_dict.keys():
                binned[tf]['num_songs'] += 1
                binned[tf]['titles_authors'].append(song)
                binned[tf]['lyrics'].append(lyric_dict[tuple(song)][1])
                song_words = lyric_dict[tuple(song)][1].translate(translator).translate(trans_newline).lower().split() #list of words

                binned[tf]['unique_words'].append(len(set(song_words)))
                binned[tf]['words'] += song_words
                
                for paren in lyric_dict[tuple(song)][2]:
                    binned[tf]['parens'].append(paren)
                for bracket in lyric_dict[tuple(song)][3]:
                    binned[tf]['bracketed'].append(bracket)

        current_time = tf
         
    #Have to join last element at end of for loop, is not caught with
    binned[current_time]['lyrics'] = ''.join(binned[current_time]['lyrics'])
    
    return binned

    
def count_newlines(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        count_newlines(binned = binned_data)
        count_newlines(binned=binned_data,dataframe=exisiting_df)
        count_newlines(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    data = [binned[tf]['lyrics'].count('\n') for tf in dataframe.columns] #list of calculated values
    dataframe.loc['Num_Newlines'] = data #appends list with index name
    
    return dataframe

def count_brackets(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        count_brackets(binned = binned_data)
        count_brackets(binned=binned_data,dataframe=exisiting_df)
        count_brackets(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    data = [len(binned[tf]['bracketed']) for tf in binned.keys()] #list of calculated values
    dataframe.loc['Num_Brackets'] = data #appends list with index name    
    
    return dataframe

def count_parens(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        count_parens(binned = binned_data)
        count_parens(binned=binned_data,dataframe=exisiting_df)
        count_parens(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    data = [len(binned[tf]['parens']) for tf in binned.keys()] #list of calculated values
    dataframe.loc['Num_Parentheticals'] = data #appends list with index name    
    
    return dataframe

def count_punctuation(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe

    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates

    example usage for the 3 input methods:
        count_punctuation(binned = binned_data)
        count_punctuation(binned=binned_data,dataframe=exisiting_df)
        count_punctuation(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))

    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())

    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())

    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    data = {punct: [0]*len(dataframe.columns) for punct in string.punctuation}
    #translator = str.maketrans('','',string.ascii_letters+string.digits)
    
    for i, tf in enumerate(dataframe.columns):
        #for char in binned[tf]['lyrics'].translate(translator):
        for char in binned[tf]['lyrics']:
            if char in string.punctuation:
                data[char][i]+=1

    for punct in data.keys():
        dataframe.loc[f'Counted_{punct}'] = data[punct] #appends list with index name
    
    return dataframe


def avg_wrd_len(binned=None,dataframe=None,raw_data=None,unique=True):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
        unique - bool, determines if the average is calculated over unqiue words or not, default = true
        
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        avg_wrd_len(binned = binned_data)
        avg_wrd_len(binned=binned_data,dataframe=exisiting_df)
        avg_wrd_len(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    assert isinstance(unique,bool)
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    avgs = []
    for tf in dataframe.columns:
        if unique == True:
            word_len = [len(word) for word in set(binned[tf]['words'])]
        else:
            word_len = [len(word) for word in binned[tf]['words']]
        avgs.append(np.mean(word_len))

    dataframe.loc['Avg_Word_Len'] = avgs #appends list with index name
        
    return dataframe

def median_wrd_len(binned=None,dataframe=None,raw_data=None,unique=True):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
            unique - bool, determines if the average is calculated over unqiue words or not, default = true

    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        median_wrd_len(binned = binned_data)
        median_wrd_len(binned=binned_data,dataframe=exisiting_df)
        median_wrd_len(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    
    med = []
    for tf in dataframe.columns:
        if unique == True:
            word_len = [len(word) for word in set(binned[tf]['words'])]
        else:
            word_len = [len(word) for word in binned[tf]['words']]
        med.append(np.median(word_len))

    dataframe.loc['Median_Word_Len'] = med #appends list with index name
        
    return dataframe
    
def num_unique_words(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        num_unique_words(binned = binned_data)
        num_unique_words(binned=binned_data,dataframe=exisiting_df)
        num_unique_words(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'    
    
    unique = []
    for tf in dataframe.columns:
        unique.append(len(set(binned[tf]['words'])))

    dataframe.loc['Num_unique_words'] = unique #appends list with index name
    
    return dataframe

def variance_words(binned=None,dataframe=None,raw_data=None,unique=True):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
            unique - bool, determines if the average is calculated over unqiue words or not, default = true
    
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        variance_words(binned = binned_data)
        variance_words(binned=binned_data,dataframe=exisiting_df)
        variance_words(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    var = []
    for tf in dataframe.columns:
        if unique == True:
            word_len = [len(word) for word in set(binned[tf]['words'])]
        else:
            word_len = [len(word) for word in binned[tf]['words']]
        var.append(np.var(word_len))

    dataframe.loc['Variance_word_length'] = var #appends list with index name
    
    return dataframe
    
def sort_word_len(num_words=10,binned=None,dataframe=None,raw_data=None,track_words=None,omit_words=["i", "and","she","he","that","this","a","they","you"]):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
	For each input method above you have the option to indicate the number of words to return (top words from period), specific words to track, or specific words to omit

    Input:
        num_words - top number of words returned and the number of times repeated
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
        track_words: list of strings, words to track, if value entered, overrides all other tracking metrics
        omit_words: list of strings, words to remove from top counted
        
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    ex:
        function(binned = binned_data)
        function(binned=binned_data,dataframe=exisiting_df)
        function(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    assert isinstance(track_words,(list,type(None)))
    if isinstance(track_words,list):
        assert all([isinstance(word,str) and len(word)>0 for word in track_words])
    assert isinstance(omit_words,(list,type(None)))
    if isinstance(omit_words,list):
        assert all([isinstance(word,str) and len(word)>0 for word in omit_words])
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    counted = []
    for tf in dataframe.columns:
        counted.append(Counter(binned[tf]['words']))

    if track_words != None:
        for word in track_words:
            dataframe.loc[f'tracked_words: {word}'] = [counted_dict[word] for counted_dict in counted]
    
    else:
        if omit_words != None:
            for word in omit_words:
                for counted_dict in counted:
                    del counted_dict[word]
        for i in range(num_words):
            dataframe.loc[f'{i+1}_most_repeated_words'] = [item.most_common(num_words)[i] for item in counted] #appends list with index name
        
    return dataframe

def num_song_repeats(num_songs=10,binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe

    For each input method above you have the option to indicate the number of songs to include in the return
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    ex:
        function(binned = binned_data)
        function(binned=binned_data,dataframe=exisiting_df)
        function(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    counted = []
    for tf in dataframe.columns:
        flattened = [', '.join(title) for title in binned[tf]['titles_authors']]
        counted.append(Counter(flattened).most_common(num_songs))
        
    for i in range(num_songs):
        dataframe.loc[f'{i+1}_most_repeated_songs'] = [item[i] for item in counted] #appends list with index name
        
    return dataframe

def avg_title_len(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        avg_title_len(binned = binned_data)
        avg_title_len(binned=binned_data,dataframe=exisiting_df)
        avg_title_len(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'

    lens = []
    for tf in dataframe.columns:
        titles = [len(auth_title[0]) for auth_title in binned[tf]['titles_authors']]
        lens.append(np.mean(titles))
        
    dataframe.loc['Avg_title_length'] = lens #appends list with index name
        
    return dataframe

def avg_artist_len(binned=None,dataframe=None,raw_data=None):
    '''
    3 input methods
    1. only binned data, function will create the associated dataframe
    2. binned data and matching dataframe, function will append to dataframe
    3. raw data as a list of [song_list, lyric_dict, timeframe='year'], same input to_timeframe function,
        this function will call to_timeframe method on raw data and then return corresponding dataframe
    
    Input:
        binned - output of to_timeframe function, dictionary of dictionaries
        dataframe - exisiting dataframe with column headers matching binned data, data will be appended to
        raw_data - expects a list of 3 elements, [song_list, lyric_dict, timeframe='year']
            song_list - is import from Jordan's function, is a list of dictionaries, each dictionary is a week
            lyric_dict - output of lyrics_to_dict, keys are tuples of ('song title', 'author'), 4 values
                str: 'title, author', str: 'lyric data', list: each element is a parenthetical, list: each element containts bracket content
    Output:
        dataframe - column headers are the binned keys(), rows are the feature each function calculates
        
    example usage for the 3 input methods:
        avg_artist_len(binned = binned_data)
        avg_artist_len(binned=binned_data,dataframe=exisiting_df)
        avg_artist_len(raw_data=[songs,lyric_dict,'week'])
    '''
    assert isinstance(binned,(dict,type(None))) 
    assert isinstance(dataframe,(pd.DataFrame,type(None)))
    assert isinstance(raw_data,(list,type(None)))
    
    if binned == None: #No binned data given, create binned data by calling to_timeframe function
        assert isinstance(raw_data,list)
        assert (len(raw_data)==3)
        assert isinstance(raw_data[0],list)
        assert all([isinstance(week,dict) for week in raw_data[0]])
        assert isinstance(raw_data[1],dict)
        assert all([isinstance(song,list) and isinstance(info,tuple) for song,info in zip(raw_data[1].values(),raw_data[1].keys())])
        assert any([raw_data[2] == period for period in ['week','month','year']])

        binned = to_timeframe(raw_data[0],raw_data[1],timeframe=raw_data[2])
        dataframe = pd.DataFrame(columns=binned.keys())
    
    if type(dataframe) == type(None): #If no dataframe given, create new one based off of binned keys
        dataframe = pd.DataFrame(columns=binned.keys())
    
    assert all([isinstance(ele,dict) for ele in binned.values()])
    assert all([col in binned.keys() for col in dataframe.columns]),'dataframe column headers need to match binned.keys()'
    
    
    lens = []
    for tf in dataframe.columns:
        names = [len(auth_title[1]) for auth_title in binned[tf]['titles_authors']]
        lens.append(np.mean(names))
        
    dataframe.loc['Avg_artist_name_length'] = lens #appends list with index name
        
    return dataframe