#!/usr/bin/env python
# coding=utf8
# -*- coding: utf8 -*-

# vim: set fileencoding=utf8 :




import pandas as pd, numpy as np
import plotly.graph_objects as go
import argparse




def assemble_dataframe(fullDfFile, dnsCodeFile):
    dataFrame = pd.read_csv(fullDfFile, index_col=0)#'data/fullDataset_post_drops.csv'
    dnsCodesFrame = pd.read_csv(dnsCodeFile)#'data/Response_Coding-deidentified - Q3.3-Primary.csv'

    #drop unneeded cols and header row from dnsCodesFrame
    dnsCodesFrame.drop(columns=['Q3.3', 'Code 2', 'Code 3', 'Unnamed: 5'],inplace=True)
    dnsCodesFrame.drop([0],inplace=True)
    overlapSet = set(dnsCodesFrame['ResponseId']).intersection(set(dataFrame['ResponseId']))

    includedCodes = dnsCodesFrame['ResponseId'].apply(lambda x: x in overlapSet)
    includedData = dataFrame['ResponseId'].apply(lambda y: y in overlapSet)

    dnsCodesMapping = dnsCodesFrame.where(includedCodes).dropna(how='all')
    mappingData = dataFrame.where(includedData).dropna(how='all')

    # important cols for analysis:
    # ' ': 'Smart DNS provides additional security when browsing the internet.' (Agree/Disagree - Likert)
    # ' .1': 'Smart DNS provides additional privacy when browsing the internet.' (Agree/Disagree - Likert)
    # 'Code 1': Primary Codes for 'Q3.3': 'To the best of your knowledge, explain how DNS works
    #           by describing the steps taken by your computer when you navigate to a website like http://www.example.com'
    # 'Q4.5': 'Using Smart DNS is a risk to my security and privacy.'(Agree/Disagree - Likert)
    # 'Q9.1': 'How trustworthy do you find these services overall?' (Trustworthy/Untrustworthy - Likert)
    # NOTE: It may also be worth considering code values given for Q4.6 in which participants explain answer given in Q4.5

    # Merge primary codes for Q3.3 w/other needed columns only (i.e. exclude other dataFrame cols)
    mergedFrame = dnsCodesMapping.merge(mappingData[['ResponseId',' ',' .1','Q4.5','Q9.1','Q29_2']],how='inner',on='ResponseId')
    return mergedFrame



# group assigned codes by level of familiarity with/understanding of DNS they (roughly) denote. 
# See paper's appendix (TODO: determine appendix and whether it appears in paper or extended version) for detailed description and breakdown of codes and their groupings.

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


# Build up constructor fields and then initialize graph object (go)
def build_sdnsTrustworthiness_plot(mergedFrame):
    riskMap ={
             'Very trustworthy':0, 'Slightly trustworthy':1,
             'Neither trustworthy nor untrustworthy':2, 
             'Slightly untrustworthy':3, 'Very untrustworthy':4
           }
    dnsKnowledgeMap = {
           'Low': 5, 'Medium': 6,
           'Med-High': 7, 'High': 8
           }
    
    labelList = [
           'Very Trustworthy', 'Slightly Trustworthy',
           'Neither',
           'Slightly Untrustworthy','Very Untrustworthy',
           'Low', 'Medium',
           'Med-High','High'
           ]
    
    # stringDist is a series where the index is of the form  source,target     <count>
    # where source is the starting (or input) val (in this case from Q9.1),
    # target is the output or outcome val (in this case originating from the groupings for Q3.3),
    # and <count> is the number of times a mapping from source to target appeared in the concatenated frame
    # (i.e. in mergedFrame['Q9.1'].str.cat(simplify_coding(mergedFrame),sep=',') ).
    stringDist =  mergedFrame['Q9.1'].str.cat(simplify_coding(mergedFrame),sep=',').value_counts()
    
    # split off the index and make it into a data-frame
    srcDests = stringDist.index.to_series(index=[x for x in range(0,stringDist.size)])
    srcDests = srcDests.str.split(',',expand=True)
    
    # map the names to their numerical values (given in riskMap), same idea for targets
    sourceList = srcDests[0].map(riskMap).to_list()
    targetList = srcDests[1].map(dnsKnowledgeMap).to_list()#destination links to join/map to
    valueList = stringDist.to_list()#relative thicknesses of links
    #colors of the nodes within the diagram listed in columnwise order (i.e. order within col 1(source) followed by that in col2(target), etc.)
    # in this case: the same ordering as that of labelList
    node_colors = [
            '#053061','#4393c3',
            '#efa882','#d6604d',
            '#b2182b','#67001f',
            '#b2182b','#efa882',
            '#053061',
            ]
    colorDict = {
           0:'#053061', 1:'#4393c3',
           2:'#efa882', 3:'#d6604d',
           4:'#b2182b', 5:'#67001f'
           } 
    # A total of 14 links. Link Coloring will be based on source's color
    # Links go 
    # 1 (Slightly Trustworthy): 5 (Low)
    # 0 (Very Trustworthy) : 8 (High)
    # 1 (Slightly Trustworthy) : 7 (Med-High)
    # 1 (Slightly Trustworthy) : 8 (High)
    # 0 (Very Trustworthy) : 7 (Med-High)
    # 0 (Very Trustworthy) : 5 (Low)
    # 1 (Slightly Trustworthy): 6 (Medium)
    # 2 (Niether) : 5 (Low)
    # 2 (Niether) : 7 (Med-High)
    # 3 (Slightly Untrustworthy) : 8 (High)
    # 0 (Very Trustworthy) : 6 (Medium)
    # 3 (Slightly Untrustworthy) : 7 (Med-High)
    # 3 (Slightly Untrustworthy) : 5 (Low)
    # 2 (Niether) : 8 (High)
    
    link_colors = [colorDict[x] for x in sourceList] 

    node_x=[0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.9, 0.9]
    node_y=[0.1 ,0.3, 0.5, 0.7, 0.1, 0.3, 0.5, 0.7]
    #controls size, color and font of node labels within the graph
    txtFont = go.sankey.Textfont(size=15)
    linkDict = dict(source=sourceList, target=targetList, value=valueList, color=link_colors)
    nodeDict = dict(label=labelList, pad=50, thickness=30, x=node_x, y=node_y, color=node_colors)
    graphData = go.Sankey(arrangement='snap',link=linkDict,node=nodeDict,textfont=txtFont)
    fig = go.Figure(data=[graphData])
    fig.update_layout(title_text='SDNS Trustworthiness vs. DNS Knowledge', font_size=20)
    fig.show()
    fig.write_image('figures/sdnsAlluvians/trustworthyVDns.pdf',format=pdf,scale=1.0)#todo: make this a passed in parameter rather than hard-coded
    return



# ' ' Smart DNS provides additional security when browsing the internet. (agree/disagree-Likert) 
# Build up constructor fields and then initialize graph object (go)
def build_sdnsSecurity_plot(mergedFrame):
    impactMap ={
        'Strongly agree':0, 'Agree':1,
        'Somewhat agree':2,'Neither agree nor disagree':3, 
        'Somewhat disagree':4, 'Disagree':5,
        'Strongly disagree':6
    }
    dnsKnowledgeMap = {
        'Low': 7, 'Medium': 8,
        'Med-High': 9, 'High': 10
        }

    labelList = [
        'Strongly Agree', 'Agree',
        'Somewhat Agree','Neither Agree Nor Disagree',
        'Somewhat Disagree','Disagree',
        'Strongly Disagree',
        'Low', 'Medium',
        'Med-High','High'
        ]

    # See <fx'n name> (line )  for an explanation of the fields  
    stringDist =  mergedFrame[' '].str.cat(simplify_coding(mergedFrame),sep=',').value_counts()

    # split off the index and make it into a data-frame
    srcDests = stringDist.index.to_series(index=[x for x in range(0,stringDist.size)])
    srcDests = srcDests.str.split(',',expand=True)

    # map the names to their numerical values (given in impactMap), same idea for targets
    sourceList = srcDests[0].map(impactMap).to_list()
    targetList = srcDests[1].map(dnsKnowledgeMap).to_list()#destination links to join/map to
    valueList = stringDist.to_list()#relative thicknesses of links
    #colors of the nodes within the diagram listed in columnwise order (i.e. order within col 1(source) followed by that in col2(target), etc.)
    # in this case: the same ordering as that of labelList
    node_colors = [
        '#67001f','#a42747',
        '#f4a582','#fddbc7',
        '#92c5de','#2166ac',
        '#053061','#67001f',
        '#efa882','#92c5de',
        '#053061'
        ]

    node_x=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.9, 0.9]
    node_y=[0.1 ,0.2, 0.3, 0.5, 0.6, 0.7, 0.1, 0.3, 0.4, 0.6]

    
    # [2, 0, 2, 1, 1, 0, 2, 1, 5, 1, 0, 3, 4, 5, 3, 2, 4, 3, 0]#TODO: Fix node colors accordingly
    # A total of 19 links. Link Coloring will be based on source's color
    colorDict = {
        0:'#67001f', 1:'#a42747',
        2:'#f4a582', 3:'#fddbc7',
        4:'#92c5de', 5:'#2166ac',
        6:'#053061'
        }

    link_colors = [colorDict[x] for x in sourceList]
    #controls size, color and font of node labels within the graph
    txtFont = go.sankey.Textfont(size=15)
    linkDict = dict(source=sourceList, target=targetList, value=valueList, color=link_colors)
    nodeDict = dict(label=labelList, pad=40, x=node_x, y=node_y,thickness=30, color=node_colors)
    graphData = go.Sankey(arrangement='snap',link=linkDict,node=nodeDict,textfont=txtFont)
    fig = go.Figure(data=[graphData])
    fig.update_layout(title_text='SDNS Improves Sec. v. DNS Knowledge', font_size=20)
    fig.show()
    fig.write_image('figures/sdnsAlluvians/improvesSecVDns.pdf')#todo: make this a passed in parameter rather than hard-coded
    return




def build_sdnsPrivacy_plot(mergedFrame):
    impactMap ={
        'Strongly agree':0, 'Agree':1,
        'Somewhat agree':2,'Neither agree nor disagree':3,
        'Somewhat disagree':4, 'Disagree':5,
        'Strongly disagree':6
        }
    dnsKnowledgeMap = {
        'Low': 7, 'Medium': 8,
        'Med-High': 9, 'High': 10
        }

    labelList = [
        'Strongly Agree', 'Agree',
        'Somewhat Agree','Neither Agree Nor Disagree',
        'Somewhat Disagree','Disagree',
        'Strongly Disagree',
        'Low', 'Medium',
        'Med-High','High'
        ]

        # See <fx'n name> (line )  for an explanation of the fields  
    stringDist =  mergedFrame[' .1'].str.cat(simplify_coding(mergedFrame),sep=',').value_counts()

    # split off the index and make it into a data-frame
    srcDests = stringDist.index.to_series(index=[x for x in range(0,stringDist.size)])
    srcDests = srcDests.str.split(',',expand=True)

    # map the names to their numerical values (given in impactMap), same idea for targets
    sourceList = srcDests[0].map(impactMap).to_list()
    targetList = srcDests[1].map(dnsKnowledgeMap).to_list()#destination links to join/map to
    valueList = stringDist.to_list()#relative thicknesses of links
    
    #colors of the nodes within the diagram listed in columnwise order (i.e. order within col 1(source) followed by that in col2(target), etc.)
    # in this case: the same ordering as that of labelList
    node_colors = [
        '#67001f','#a42747',
        '#f4a582','#fddbc7',
        '#92c5de','#2166ac',
        '#053061','#67001f',
        '#efa882','#92c5de',
        '#053061'
        ]

    node_x=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.9, 0.9]
    node_y=[0.1 ,0.2, 0.3, 0.5, 0.6, 0.7, 0.1, 0.3, 0.4, 0.6]

    colorDict = { 
        0:'#67001f', 1:'#a42747',
        2:'#f4a582', 3:'#fddbc7',
        4:'#92c5de', 5:'#2166ac',
        6:'#053061'
        }

    link_colors = [colorDict[x] for x in sourceList]

    # A total of 18 links. Link Coloring will be based on source's color
    # link_colors = [
    #     '#67001f', '#a42747',
    #     '#f4a582', '#a42747',
    #     '#a42747', '#67001f',
    #     '#f4a582', '#a42747',
    #     '#fddbc7', '#2166ac',
    #     '#92c5de', '#2166ac',
    #     '#67001f', '#f4a582',
    #     '#fddbc7', '#fddbc7',
    #     '#67001f', '#f4a582'
    #     ]
    #controls size, color and font of node labels within the graph
    txtFont = go.sankey.Textfont(size=20)
    linkDict = dict(source=sourceList, target=targetList, value=valueList, color=link_colors)
    nodeDict = dict(label=labelList, pad=40, x=node_x, y=node_y,thickness=30, color=node_colors)
    graphData = go.Sankey(arrangement='snap',link=linkDict,node=nodeDict,textfont=txtFont)
    fig = go.Figure(data=[graphData])
    fig.update_layout(title_text='SDNS Improves Priv. v. DNS Knowledge', font_size=20)
    fig.show()
    fig.write_image('figures/sdnsAlluvians/improvesPrivVDns.pdf')#todo: make this a passed in parameter rather than hard-coded
    return






def parse_inputs():
    desc = 'dns_understanding_alluvium.py: Data analysis file -constructs Alluvium plots between users\' understanding/familiarity w/DNS and their beliefs on SDNS\'s impact on their security/privacy'
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
    build_sdnsTrustworthiness_plot(mergedFrame)
    build_sdnsSecurity_plot(mergedFrame)
    build_sdnsPrivacy_plot(mergedFrame)





if __name__=='__main__':
        main()
