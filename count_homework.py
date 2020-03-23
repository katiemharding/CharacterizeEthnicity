#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import sys

def initial_manipulation(data, probe):
    # This is just to get the data in the format I need.
    data_cols = [col for col in data if col.startswith(probe)]
    short_data = data.drop(columns = data_cols)
    return(short_data)

def find_duplicates(data, non_data, chosen_ethnicity):
    # Steps (from above)
    # 1) Characterize the non_ probes by finding the mean value for the sample
    # 2) For each sample divide the mean non_ probe value by the individual probe counts
    # 3) Find problematic probes by examining the variability of those counts
    # 4) Label each probe as deletions/duplications
    # separate out one ethnicity
    data_eth = data.loc[data.ethnicity == chosen_ethnicity].copy()
    non_eth = non_data.loc[non_data.ethnicity == chosen_ethnicity].copy()
    # Dropping old Name columns so we don't have problems when dividing later
    non_eth.drop(columns =["ethnicity"], inplace = True)
    data_eth.drop(columns =["ethnicity"], inplace = True) 
    mean_sample = pd.Series(non_eth.mean(1)) # one indicates find mean of each row
    data_divide = data_eth.div(mean_sample, axis = 0) 
    # for data visualization, and subsequent steps, I want one long column of data
    # to do this I need one long column of data
    # melt will stack the columns as I need them
    my_columns = [col for col in data if col.startswith('probe_')]
    data_melt = pd.melt(data_divide, value_vars=my_columns, value_name='proportion')
    # I want the probe to be listed as just a number (makes the graphs cleaner)
    # to do this I split on "_" and take the last string
    data_melt['number'] = data_melt['variable'].str.split('_').str[-1]
    # making separate last name column from new data frame 
    data_melt.drop(columns =['variable'], inplace = True) # Dropping old Name columns 
    # add leading zeros so they appear in order
    data_melt['number'] = data_melt['number'].str.zfill(2)
    return(data_melt)

def find_duplicates_non(non_data, chosen_ethnicity):
    # Steps (see find_duplicates)
    # separate out one ethnicity
    non_eth = non_data.loc[non_data.ethnicity == chosen_ethnicity].copy()
    # Dropping old Name columns so we don't have problems when dividing later
    non_eth.drop(columns =["ethnicity"], inplace = True)
    mean_sample = pd.Series(non_eth.mean(1)) # one indicates find mean of each row
    data_divide = non_eth.div(mean_sample, axis = 0)
    # for data visualization, and subsequent steps, I want one long column of data
    # to do this I need one long column of data
    # melt will stack the columns as I need them
    my_columns = [col for col in non_data if col.startswith('non_probe_')]
    data_melt = pd.melt(data_divide, value_vars=my_columns, value_name='proportion')
    # I want the probe to be listed as just a number (makes the graphs cleaner)
    # to do this I split on "_" and take the last string
    data_melt['number'] = data_melt['variable'].str.split('_').str[-1]
    # making separate last name column from new data frame
    data_melt.drop(columns =['variable'], inplace = True) # Dropping old Name columns
    # add leading zeros so they appear in order
    data_melt['number'] = data_melt['number'].str.zfill(2)
    return(data_melt)

def find_variability(data, CV):
    proportion_mean = data.groupby('number')['proportion'].mean()
    proportion_std = data.groupby('number')['proportion'].std()
    proportion_data = pd.concat([proportion_mean, proportion_std ], axis = 1)
    proportion_data.columns = ['mean', 'std']
    proportion_data['CV']= proportion_data['std']/proportion_data['mean']
    probe_list = []
    for index, row in proportion_data.iterrows():
        if row['CV'] > CV:
            probe_list.append(index)
    return(probe_list)

def find_problem_probes(data):
    varibility_dict = {}
    # linspace gives evenly spaced numbers over a given interval.  
    # range only works with integers
    for variability in np.linspace(0.1, 0.15, 6): 
        prob_list = find_variability(data, (variability))
        print(str(round(variability*100)) +"%: count =" + str(len(prob_list)) + ";  Problem Probes:")
        print(prob_list)
        varibility_dict[variability] = prob_list
    return(varibility_dict)

def label_duplicates(data):
    deletions_count = data.groupby('number')['proportion'].apply(lambda x: x[x < .5].count())
    total_count = data.groupby('number')['proportion'].count()
    duplications_count = data.groupby('number')['proportion'].apply(lambda x: x[x > 1.5].count())
    count_data = pd.concat([total_count, deletions_count, duplications_count ], axis = 1)
    count_data.columns = ['total', 'deletions', 'duplications']
    count_data['percent_del']= count_data['deletions']/count_data['total']
    count_data['percent_dup']= count_data['duplications']/count_data['total']
    count_data.reset_index(level=0, inplace=True)
    return(count_data)

def find_continuous(x): 
    it = iter(x) # creates an object which can be iterated one element at a time    
    prev = next(it) # the next item in the list (starts with 0)
    result = [] 
    while prev is not None: # allows the loop to end
        start = next(it, None) # finds the next value
        if prev + 1 == start: 
            result.append(prev) # if prev is one more than the next, append to list
        elif result: 
            yield list(result + [prev]) # yield returns an answer, but allows you to keep going
            result = [] # if start is more than 1 more than prev, create a new list
        prev = start # go to the next number and begin again.
# taken from: https://www.geeksforgeeks.org/python-find-groups-of-strictly-increasing-numbers-in-a-list/

def return_probes(data, CV):
    #Steps:
    #1) find percent duplications and deletions (this must be in the answer)
    eth_counts = label_duplicates(data)
    eth_counts_short = eth_counts[['number', 'percent_del', 'percent_dup']]
    eth_series = (eth_counts[["percent_del", "percent_dup"]].max(axis=1)).to_frame()

    #2) label problem probes: these should be included in the numbers (we should skip over these probes)
    problem_probes = find_variability(data, CV)
    for index in problem_probes:
        eth_series.at[int(index), 0] = 0.99

    #3) get list of max values
    del_list = []
    for index, row in eth_series.iterrows():
        if row[0]> 0.6:
            del_list.append(index)
    sorted_del_list = sorted(del_list) # just in case, sort the list

    #4) get list of continuous probes len >4
    cont_probe_list = list(find_continuous(sorted_del_list))
    len_4_list = []
    for sub_list in cont_probe_list:
        if len(sub_list) >3:
            len_4_list.append(sub_list)
    concat_list = [j for i in len_4_list for j in i]
    concat_list_str = [str(i).zfill(2) for i in concat_list] 
    prob_percent = eth_counts_short[eth_counts_short.number.isin((concat_list_str))]
    return(prob_percent)

def give_percent_del_all(data, CV):
    eth_list = list(data.ethnicity.unique())
    result = pd.DataFrame()
    for eth in eth_list:
        prob_data = initial_manipulation(data, 'non_probe')
        non_prob_data = initial_manipulation(data, 'probe')
        first_ethnicity = find_duplicates(prob_data, non_prob_data, eth)
        one_eth_prob = return_probes(first_ethnicity, CV)
        one_eth_prob['Ethnicity'] = eth 
        result = result.append(one_eth_prob)
    return(result)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("please provide file name and CV in that order")
        exit(1)
    new_CV = float(sys.argv[2])
    new_file = pd.read_csv(sys.argv[1], index_col =0)
    print("file loaded", sys.argv[1])
    file_name = "test_output.csv"
    test1 = give_percent_del_all(new_file, new_CV)
    print("data run with CV:", new_CV)
    test1.to_csv(file_name, index = False)
    print(file_name, "file created")
    

