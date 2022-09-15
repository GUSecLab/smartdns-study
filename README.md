# User Perceptions of the Privacy and Usability of Smart DNS -supplemental artifacts
This repository contains supplemental material to enable replication of our study as submitted to the [artifact evaluation for ACSAC 2022](https://www.acsac.org/2022/submissions/papers/artifacts/).


* Both versions of the survey as QSF-files
* Analysis script(s) used for quantitative analysis
* Codebooks used for qualitative analysis
* scripts for computing IRR and a breakdown of calculated IRR by round and IRR results

## Repository Structure:
* __html__: (html, js) source files and scripts used to run the study recruitment page. 
* __scripts__: (python) scripts used for data preprocessing and analysis
* __analysis__: analysis artifact files, mainly from our qualitative analysis. These include a copy of our [qualitative codebooks](analysis/qualitative_analysis/codebook.pdf) and records of our [inter-rater reliability while coding](analysis/qualitative_analysis/SDNS_irr_tracking.csv).  
* __survey_instruments__: The surveys as given to Reddit and Prolific participants as Qualtrics export (QSF) files (see below for details). 


### QSF Files:
Each QSF-file contains survey questions exported from Qualtrics and can easily be re-imported into there. There are two versions of the survey:
* The Survey as presented to participants from Reddit (survey_instruments/reddit/Smart_DNS.qsf)
* The prescreen ([survey_instruments/prolific/SmartDNS-Prescreen.qsf](survey_instruments/prolific/SmartDNS-Prescreen.qsf)) and main survey ([survey_instruments/prolific/SDNS_-Main_Survey.qsf](survey_instruments/prolific/SDNS_-Main_Survey.qsf)) as presented to Prolific participants.

Note that all of the surveys require Javascript and therefore will not work with free Qualtrics accounts.
The surveys have multiple sections as outlined in the paper. These sections are modeled in the Qualtrics survey. Refer to the Qualtrics documentation in order to learn how to import the survey back into Qualtrics.

#### DNS Test:
Though we did not include it in the QSF files, the original surveys contained a hidden question in which participants computers accessed (and thus requested the DNS resolution for) a domain under our control of the form <unique_id>.smartdnsstudy.com, where <unique_id> was a nonce assigned to the each unique participant session and *.smartdnsstudy.com was a wildcard domain for which we owned the authoritative name server. 
(Per the conditions of our IRB approval and to protect participant privacy, we only stored records of the DNS resolution requests in our server logs.)  
We then compared the DNS resolver IP addresses to a set of known SDNS resolvers to try and determine whether participants had configured SDNS to run on their computers and forgotten to disable it. 
However, since our results were inconclusive, we ultimately decided not to report them in our paper and have omitted them from our artifacts. 
