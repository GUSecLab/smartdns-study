#!/usr/bin/env python
# coding=utf8
# -*- coding: utf8 -*-

# vim: set fileencoding=utf8 :



# Written by Rahel A. Fainchtein (raf3272[at]georgetown.edu)

import json
import errno
import re
import numpy as np
import pandas as pd

from argparse import ArgumentParser
from datetime import datetime
from os import mkdir as os_mkdir,scandir as os_scandir



#extract mapping of dataFrame keys (e/g 'Q2.1')
# to the question to which they're referring (results returned as a dict).
def get_key_mapping(dataFrame):
    frameKeys = dataFrame.keys()
    numKeys = len(frameKeys)
    mapDict = dict()
    for i in range(numKeys):
        mapDict[frameKeys[i]] = dataFrame[frameKeys[i]][0]
    return mapDict

#Helper for get_service_use()
#Map Q2.3 (currently/prev. used SDNS) to boolean
#filter Q9 (Which services used/considering) to distinguish consideration vs use.
def filter_by_sdns_use(useCol, services):
     useFilter = useCol.map({'Yes':True, 'No':False},na_action='ignore')
     useFilter.fillna(False,inplace=True)
     serviceUse = services[useFilter]
     considers = services[useFilter.apply(lambda x: not(x))]
     return (serviceUse,considers)

# How many participants use/used SDNS and how many are considering?
# Usage breakdown by service (useByService), number of services used
# breakdown by services considered (with double-counting), number of services considered
def get_service_use(useCol,services):
    (serviceUse, considers) = filter_by_sdns_use(useCol,services)
    useByService = serviceUse.str.split(pat=',').explode().value_counts()
    useByServNorm = serviceUse.str.split(pat=',').explode().value_counts(normalize=True)
    numServicesUsed = serviceUse.str.split(pat=',').map(lambda x: len(x)).value_counts()
    numServUsedNorm = serviceUse.str.split(pat=',').map(lambda x: len(x)).value_counts(normalize=True)
    
    consByService = considers.str.split(pat=',').explode().value_counts()
    consByServNorm = considers.str.split(pat=',').explode().value_counts(normalize=True)
    numServConsidered = considers.str.split(pat=',').map(lambda x: len(x)).value_counts()
    numServConsNorm = considers.str.split(pat=',').map(lambda x: len(x)).value_counts(normalize=True)
    
    ret = {
            'useByService':useByService, 'useByServNorm':useByServNorm,
            'numServicesUsed':numServicesUsed, 'numServUsedNorm':numServUsedNorm,
            'consByService':consByService, 'consByServNorm': consByServNorm,
            'numServConsidered':numServConsidered, 'numServConsNorm':numServConsNorm
            }
    return ret


# Using Smart DNS when I browse the Internet provides additional security(' ')/privacy(' .1') 
def get_sec_priv_impressions(nPrivSecLikert):
    ret = {
            'moreBrowsingSec': nPrivSecLikert[' '].value_counts(),
            'browseSecNorm': nPrivSecLikert[' '].value_counts(normalize=True),
            'moreBrowsingPriv': nPrivSecLikert[' .1'].value_counts(),
            'browsePrivNorm': nPrivSecLikert[' .1'].value_counts(normalize=True)
            }
    return ret


#Handle subframes with likert value responses.
def process_likert(subframe,mapDict):
    retDict = dict()
    for col in subframe.keys():
        if col == 'random_id':
              continue
        colVal = mapDict[col]
        valDist = subframe[col][1:].value_counts()
        normValDist = subframe[col][1:].value_counts(normalize=True)
        retDict[col] = {
                           'description': colVal,
                           'distribution':valDist, 'normalized_dist':normValDist
                       }
    return retDict



# Get the relative distributions of options selected
# for each entry in a select many column
def select_many_dist(col,titleSuffix):
    colLists = col.str.split(',')
    lengths = colLists.apply(lambda x: len(x) if isinstance(x,list) else np.nan)
    lengthDist = lengths.value_counts(dropna=True)
    distributionDict = dict()
    subsetSizes = dict()
    maxVal = lengths.dropna().max()
    for i in range(1,int(maxVal)+1):
        subsetI = colLists.apply(lambda x: x if isinstance(x,list) and len(x)==i else np.nan).dropna()
        prevalenceDist = subsetI.explode().value_counts()
        distributionDict[str(i)+titleSuffix] = prevalenceDist
    return (lengthDist, distributionDict)


# Q7.1: Which other services do SDNS providers offer (if any)? 
# Q7.2: Were participants mainly looking to use SDNS when they signed up w/their (respective) service provider(s)?
# Q7.4: Which (if any) of the additional services (other than SDNS) did participants use?
def analyze_other_offerings(otherServices,mapDict):
    offersAndMotives = process_likert(otherServices[['Q7.1','Q7.2']],mapDict)
    (countsByNumOffered,offerPrevalence) = select_many_dist(otherServices['Q7.3'][1:],' service(s)') 
    (countsByNumUsed,usePrevalence) = select_many_dist(otherServices['Q7.4'][1:],'service(s)')
    ret =  (countsByNumOffered ,offerPrevalence ,
            countsByNumUsed, usePrevalence
            )
    return ret


def parse_inputs():
    desc = "scrub_records.py removes PII fields from qualtrics data (based on field names) and splits quantitative and qualitative results into two separate data files."
    parser = ArgumentParser(description=desc)
    parser.add_argument('-f',
                        dest='infile',
                        type=str,
                        default='data/SDNS_RedditData_raw.csv',
                        help='raw data file to be read in and scrubbed of PII. Default: data/SDNS_RedditData_raw.csv (assumed to be running from main project dir)')
    parser.add_argument('-d',
                        dest='newDirs',
                        action='store_true',
                        help='If specified, create new directories for the quantitative and qualitative data if they don\'t already exist. NOTE: directory names required if this option is specified. Default behavior: output files to the current working directory.')
    parser.add_argument('-qn',
                        dest='quantDir',
                        nargs='?',
                        const='quantitative_metrics',
                        help='Path to directory for quantitative output data files. Flag is required if -d is specified. Path value defaults to the current_working_dir/quantitative_metrics ')
    parser.add_argument('-ql',
                        dest='qualDataDir',
                        nargs='?',
                        help='Path to directory for qualitative output files. Flag is required if -d is specified. Path value defaults to the current_working_dir/qual_data_metrics')
    return parser.parse_args()



def main():
    params = parse_inputs()
    dataFrame = pd.read_csv(params.infile)
    piiCols = ['IPAddress','RecipientLastName',
                'RecipientFirstName', 'RecipientEmail',
                'LocationLatitude', 'LocationLongitude',
                'Status']
    dataFrame.drop(columns=piiCols, inplace=True)
    # Note: For data from Prolific participants the Prolific_PID field 
    # was used to map records collected in the prescreen survey to 
    # reponses from the same participants given in the main survey.
    # Once all Prolific data had been assembled, the Prolific_PID field was deleted. 

    dataFrame.drop(1,inplace=True)#drop qualtrics column IDs

    noneedCols = ['Progress','UserLanguage',
                  'DistributionChannel','urlPart',
                  'idURL','Q1.3',
                  'Q1.4','Q1.5']#'EndDate','StartDate']#specifically removed from Reddit data
    
    # utm fields were mainly used to determine the most effective means of participant recruitment through Reddit
    # and were not needed for additional analysis. These fields were not present in data collected via Prolific. 
    # dataFrame.drop(columns=[ 'Source', 'utm_source', 'utm_medium', 'utm_campaign'], inplace=True)

    mapDict = get_key_mapping(dataFrame)
    dataFrame.drop(0,inplace=True)#remove field-desc from dataFrame - use mapDict instead
    
    # sanity check: Review the names of the fields to ensure initial PII has been scrubbed. 
    print(dataFrame.keys()[:20])
    print(dataFrame.keys()[60:])
   


    # Split off smaller dataFrame (copies) to perform analysis.
   
    # demographics dataFrame
    demographics = dataFrame[['random_id','Q13.1','Q13.2','Q13.3','Q13.4','Q13.5','Q13.5_4_TEXT','Q13.6']]
    # Q13.1: What is your age? 
    # Q13.2: What is the highest level of school you have completed or the highest degree you have received?
    # Q13.3: In which country do you live?
    # Q13.4: What is your nationality?
    # Q13.5: What is the gender to which you most closely identify?
    # Q13.6: What is your annual income in US Dollars?

    demogStats = process_likert(demographics,mapDict) 

    otherServices = dataFrame[['Q7.1','Q7.2','Q7.3','Q7.4']]
    # Q7.1: Which other services do SDNS providers offer (if any)? 
    # Q7.2: Were participants mainly looking to use SDNS when they signed up w/their (respective) service provider(s)?
    # Q7.3: Which other services does/did your Smart DNS provider offer? (Select all that apply)
    # Q7.4: Which (if any) of the additional services (other than SDNS) did participants use?


    # perform analysis
    (countsByNumOffered,offerPrevalence, countsByNumUsed, usePrevalence) = analyze_other_offerings(otherServices,mapDict) 

    #Quantitative analysis fields

    #Q6.5 Factors 

    # SDNS usage:
    


if __name__ =='__main__':
    main()
