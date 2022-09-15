#!/usr/bin/env python
# coding=utf8
# -*- coding: utf8 -*-

# vim: set fileencoding=utf8 :


# Written by Rahel A. Fainchtein (raf3272[at]georgetown.edu)
#
#

import pandas as pd, numpy as np
from os import getcwd as os_getcwd


# Removal of disqualified responses from Prolific participants.
def remove_disqualified_responses(prolificPrescreen, proMainQuant):
    toKeep = prolificPrescreen['Q2.6']!='I have never had nor used a SmartDNS account'
    # Q2.6: Which of the following types of Smart DNS accounts have you had or used \n\n(including any accounts you currently have/use)?\n\n(Select all that apply.)
    #       Note: 'I have never had nor used a SmartDNS account' was an exclusive option. 

    qualifies = prolificPrescreen['Q2.3'].apply(lambda x: x=='Yes')
    #Q2.3: Do you currently use Smart DNS, or have you done so in the past?
    
    #Remove qualitative question fields and responses from participants who didn't meet qualification requirements from prescreen
    prolificPrescreen = prolificPrescreen[['PROLIFIC_PID','random_id','Q2.1','Q2.3','Q2.4','Q2.6','Q9','Q9_15_TEXT','Q3.1','Q3.2','Q13.1','Q13.2','Q13.3','Q13.4','Q13.5','Q13.5_4_TEXT','Q13.6']].where(qualifies & toKeep)
    matchRestriction = prolificPrescreen['PROLIFIC_PID'].apply(lambda x: x in set(proMainQuant['PROLIFIC_PID']))
    prolificPrescreen = prolificPrescreen.where(matchRestriction)
    matchRestriction = proMainQuant['PROLIFIC_PID'].apply(lambda x: x in set(prolificPrescreen['PROLIFIC_PID']))
    proMainQuant = proMainQuant.where(matchRestriction)
    return (prolificPrescreen, proMainQuant)


#extract mapping of dataFrame keys (e/g 'Q2.1')
# to the question to which they're referring (results returned as a dict).
def get_key_mapping(dataFrame):
    frameKeys = dataFrame.keys()
    numKeys = len(frameKeys)
    mapDict = dict()
    for i in range(numKeys):
        mapDict[frameKeys[i]] = dataFrame[frameKeys[i]][0]
    return mapDict



def parse_inputs():
    desc = "remove_disqualified.py merges data collected in the Prolific prescreen survey with that of the main survey and removes entries for prolific participants that were previously included but ultimately determined not to qualify to participate in this study."
    parser = ArgumentParser(description=desc)
    parser.add_argument('-p',
        dest='prescreen_file',
        type=str,
        default='data/SDNS-ProlificPrescreen_12July21.csv',
        help='raw data file to be read in. Default: data/SDNS-ProlificPrescreen_12July21.csv (script assumed to be running from main project dir)')
    parser.add_argument('-m',
        dest='main_survey_file',
        type=str,
        default='data/SDNS-ProlificMain_12July21.csv',
        help='Input data file containing responses to the main survey from Prolific participants. Default: data/SDNS-ProlificMain_12July21.csv (assumed to be running from main project dir)')
    parser.add_argument('-o',
            dest='outfile',
            type=str,
            default=os.getcwd()+'/prolific_datafile.csv') 
    return parser.parse_args()


def main():
    params = parse_inputs()
    prolificPrescreen = pd.read_csv(params.prescreen_file)
    prolificMain = pd.read_csv(params.main_survey_file)
    piiCols = ['IPAddress','RecipientLastName',
                'RecipientFirstName', 'RecipientEmail',
                'LocationLatitude', 'LocationLongitude',
                'Status']
    prolificPrescreen.drop(columns=piiCols, inplace=True)
    prolificMain.drop(columns=piiCols, inplace=True)

    # Note: For data from Prolific participants the Prolific_PID field 
    # was used to map records collected in the prescreen survey to 
    # reponses from the same participants given in the main survey.
    # Once all Prolific data had been assembled, the Prolific_PID field was deleted. 

    #dataFrame.drop(1,inplace=True)#drop qualtrics column IDs

    prescreenNoNeed = ['StartDate','EndDate',
                 'Progress','UserLanguage',
                 'Duration (in seconds)','Finished',
                 'DistributionChannel','urlPart',
                 'idURL','Q1.3',
                 'Q1.4','Q1.5','Rejected',
                 'RecordedDate','ExternalReference',
                 'SESSION_ID','STUDY_ID']

    # Participants were not allowed to proceed w/the survey unless 
    # they indicated they were 18 or older (Q1.3-prescreen, Q114-Main), 
    # they had and understood the informed consent (Q1.4-prescreen, Q113-Main),
    # and they consented to participate in the study (Q1.5-prescreen, Q112-Main).
   
    # Responses to the prescreen where it was determined that the respondent did not qualify for the main survey
    # were marked with the 'Rejected' field, and only responses that were not marked with this field (i.e. where it was null) were exported. 

    mainNoNeed = ['StartDate','EndDate',
           'Progress','UserLanguage',
           'Duration (in seconds)','Finished',
           'DistributionChannel', 'urlPart',
           'idURL','Q114',
           'Q113','Q112',
           'Low_quality','RecordedDate',
           'ResponseId', 'ExternalReference',
           'STUDY_ID', 'SESSION_ID']

    # Responses to the main survey determined to be of low quality (e.g. participant did not give descriptive answers)
    # were marked with the 'Low_quality' field, and only responses that were not marked with this field (i.e. where it was null) were exported. 

    prolificPrescreen.drop(columns=prescreenNoNeed, inplace=True)
    prolificMain.drop(columns=mainNoNeed, inplace=True)
    
    #get mapping dicts
    prescreenMap = get_key_mapping(prolificPrescreen)
    mainMap = get_key_mapping(prolificMain)
    prolificPrescreen.drop([0,1],inplace=True)#remove field-desc from dataFrame - use prescreenMap instead
    prolificMain.drop([0,1],inplace=True)#remove field-desc from dataFrame - use mainMap instead


    #split off qualitative question responses from quantitative ones. (This script only handles quantitative ones):
    #The following questions are qualitative:
    # Prescreen:
    # Q2.2: What are Smart DNS services primarily used for?
    # Q3.3: To the best of your knowledge, explain how DNS works by describing the steps taken by your computer
    #       when you navigate to a website like http://www.example.com
    
    # Note: Q107 is an attention check. If a participants failed it, we manually reviewed their response to assess its quality.
    #       All 5 such responses to the prescreen were otherwise of good quality and were therefore included.  

    
    # Main Survey:
    # Q4.6 Please explain why you think Smart DNS can affect your security and privacy in the way(s) you indicated.
    # Q6.2 What was your main goal in using a Smart DNS service?
    # Q6.4 Like other services Smart DNS services come with a specific set of strengths and weaknesses.
    #      Given that Smart DNS services are not the only offerings capable of unblocking geo-fenced (geoblocked) websites 
    #      (for example some VPN services can do this as well), what motivated you to specifically use Smart DNS?
    # Q9.2: Please describe your view on the overall trustworthiness of Smart DNS.
    # Q10.3: If previously blocked by a content provider when using Smart DNS: How do you think they determined you were using Smart DNS?
    # Q11.3: Please explain your prior response: [Using Smart DNS to access content blocked in my geographic region is/is not ethical]
    # Q11.5: Please explain your prior response: [Using Smart DNS to access content blocked in my geographic region is/is not legal]
    
    # prescreenQual = prolificPrescreen[['Q2.2','Q3.3']]
    # mainQual = prolificMain[['Q4.6','Q6.2','Q6.4','Q9.2','Q10.3','Q11.3','Q11.5']]
    prolificPrescreen.drop(columns=['Q2.2','Q3.3'],inplace=True)
    prolificMain.drop(columns=['Q4.6','Q6.2','Q6.4','Q9.2','Q10.3','Q11.3','Q11.5'],inplace=True)

    # Remove remaining disqualified responses:
    (prolificPrescreen, prolificMain) = remove_disqualified_responses(prolificPrescreen, prolificMain)

    # Align responses in both dataFrames and merge 
    prolificMerged = prolificPrescreen.dropna(how='all').merge(prolificMain.dropna(how='all'),how='inner', on='PROLIFIC_PID')    
    
    #remove responses where participants used a provider that has never offered SDNS, and does not currently offer it.
    prolificMerged = prolificMerged['Q9_15_TEXT'].apply(lambda x: x not in ['KutoVpn','OperaVPN','protonvpn','Mullvad'])
    prolificMerged.drop(columns=['PROLIFIC_PID'],inplace=True)
    prolificMerged.to_csv(path_or_buf=params.outfile)




if __name__ =='__main__':
        main()

