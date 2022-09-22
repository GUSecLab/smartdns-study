#!/usr/bin/env python
# coding=utf8
# -*- coding: utf8 -*-

import pandas as pd, numpy as np
from scipy import stats
import argparse


# Assumes df is a two-column dataframe w/the 2 
def compute_spearman(mFrame):
    estimate = mFrame['Q3.2'].to_numpy()
    assessed = mFrame['simplified_code1'].to_numpy()
    rho,pval = stats.spearmanr(estimate,assessed)
    print(f'rho = {rho} \n pval = {pval}') 
    # return (rho,pval)


def simplify_coding(mergedFrame):
    return  mergedFrame['Code 1'].apply(lambda x: simplify_helper(x))




def simplify_helper(code):
    if code in set(['sdns','protocol_unclear','don\'t_know','identifies_pc_by_ip','missing_details',np.nan]):
        return 'Low'
    elif code in set(['navigation_to_website','maps_website_to_Internet_name','maps_ip_to_domain','translates_domains_for_browsers']):
        return 'Medium'
    elif code == 'maps_website_to_ip':
        return 'Med-High'
    elif code in set(['maps_domain_to_ip','query_dns_server','query_recursive_dns']):
        return 'High'
    else:
        return code


def assemble_dataframe(fullDfFile, dnsCodeFile):
    dataFrame = pd.read_csv(fullDfFile, index_col=0)
    dnsCodesFrame = pd.read_csv(dnsCodeFile)
    dnsCodesFrame.drop(columns=['Q3.3', 'Code 2', 'Code 3', 'Unnamed: 5'],inplace=True)
    dnsCodesFrame.drop([0],inplace=True)
    overlapSet = set(dnsCodesFrame['ResponseId']).intersection(set(dataFrame['ResponseId']))
    includedCodes = dnsCodesFrame['ResponseId'].apply(lambda x: x in overlapSet)
    includedData = dataFrame['ResponseId'].apply(lambda y: y in overlapSet)

    dnsCodesMapping = dnsCodesFrame.where(includedCodes).dropna(how='all')
    mappingData = dataFrame.where(includedData).dropna(how='all')

    #Q3.1 Corresponds to question S7 in the paper, Q3.2 corresponds with S8 in the paper.  
    mergedFrame = dnsCodesMapping.merge(mappingData[['ResponseId','Q3.2']],how='inner',on='ResponseId')
    return mergedFrame



def mainMap_helper(mVal):
    if mVal in {'Low', 'I definitely do not know'}:
        return 1
    elif mVal in {'Medium','I\'m not sure I know'}:
        return 2
    elif mVal in {'Med-High', 'I somewhat know'}:
        return 3
    elif mVal in {'High','I definitely know'}:
        return 4
    else:
        return mVal









#Quick and Dirty: Getting the values in for now. Will correct to have the results read in rather than recomputed here. 
def parse_inputs():
    desc = 'dns_knowledgeSpearman.py: Measures the Spearman Rank of correlation between participants estimates of their knowledge about how DNS works, and the categories to which they were assigned in dns_understanding_alluvium.py'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-f',
                        dest='fullDfFile',
                        type=str,
                        default='data/fullDataset_post_drops.csv',
                        help='indicates the (relative or complete) filepath for the full dataset\'s DF exported as a csv (default: \'data/fullDataset_post_drops.csv\')')
    parser.add_argument('-d',
                        dest='dnsCodesFile',
                        type=str,
                        default='data/Response_Coding-deidentified - Q3.3-Primary.csv',
                        help='(full or relative) filepath to csv w/open coded values for Q3.3 responses (i.e. free-text description of DNS functionality) (default: \'data/Response_Coding-deidentified - Q3.3-Primary.csv\')')
    return parser.parse_args()





def main():
    params = parse_inputs()
    mergedFrame = assemble_dataframe(params.fullDfFile, params.dnsCodesFile)
    mergedFrame['simplified_code1'] = simplify_coding(mergedFrame)
    numericMframe = mergedFrame[['Q3.2','simplified_code1']].applymap(lambda x:mainMap_helper(x))
    # rho,pval = 
    compute_spearman(numericMframe)
    # print('Spearman rank values: ')
    # print(f'rho = {rho} \n pval = {pval}')



if __name__=='__main__':
    main()
