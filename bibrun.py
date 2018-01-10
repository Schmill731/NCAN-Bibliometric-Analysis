#!/usr/bin/env python3

# Runs a bibliometric assessment of the given list of PMIDs
# Expects the filename of a .txt file of a list of PMIDs to be given
# Runs on Python 3, will not work with Python 2
#
# Created by Billy Schmitt, williamschmitt@college.harvard.edu
# Last Modified 1/10/17

# List of imports
import sys
import requests
import xlsxwriter
import collections
import csv
from difflib import SequenceMatcher

def main():
    # Header fields for Pubs worksheet
    pubsHeader = set()
    pubsHeader.add("TR&D")

    # Load in list of PMIDs
    if len(sys.argv) == 2:
        pmidFile = sys.argv[1]
    else:
        pmidFile = 'pubmed_result.txt'

    with open(pmidFile, 'r') as file:
        pmidList = file.read().rstrip()

    pmidList = pmidList.split('\n')

    #Search iCite for Relative Criteria Ratio
    iCite = requests.get("https://icite.od.nih.gov/api/pubs?pmids=" +
        ",".join(pmidList))
    if iCite.status_code == 200:
        print("iCite Data Collected")
    else:
        print("Error getting iCite information.")
        print("Response Code: " + str(iCite.status_code))
        print("Aborting...")
        return

    #List of publication information
    pubs = iCite.json()["data"]
    for key in sorted(pubs[0].keys()):
        pubsHeader.add(key)
    pubsHeader.add("JIF")
    pubsHeader.add("JIF Percentile")
    pubsHeader.add("JIF Quartile")

    # Create variable to hold summary data
    sumData = []
    sumHeader = collections.OrderedDict()
    sumHeader["TR&D"] = None
    sumHeader["Year"] = None
    sumHeader["Count"] = None
    sumHeader["Weighted RCR"] = None
    sumHeader["Mean RCR"] = None
    sumHeader["Average NIH Percentile"] = None
    sumData.append({'Year': 2013, 'Count': 0, 'Weighted RCR': 0,
        'Mean RCR': 0, 'Average NIH Percentile': 0})
    sumData.append({'Year': 2014, 'Count': 0, 'Weighted RCR': 0,
        'Mean RCR': 0, 'Average NIH Percentile': 0})
    sumData.append({'Year': 2015, 'Count': 0, 'Weighted RCR': 0,
        'Mean RCR': 0, 'Average NIH Percentile': 0})
    sumData.append({'Year': 2016, 'Count': 0, 'Weighted RCR': 0,
        'Mean RCR': 0, 'Average NIH Percentile': 0})
    sumData.append({'Year': 2017, 'Count': 0, 'Weighted RCR': 0,
        'Mean RCR': 0, 'Average NIH Percentile': 0})
    
    #Determine number of publications per year
    for pub in pubs:
        for year in sumData:
            if pub["year"] == year["Year"]:
                year["Count"] += 1
                break

    #Determine Weighted RCR and Mean RCR
    for pub in pubs:
        for year in sumData:
            if pub["year"] == year["Year"] and pub['relative_citation_ratio'] is not None:
                year['Weighted RCR'] += pub['relative_citation_ratio']
                year['Mean RCR'] += pub['relative_citation_ratio']/year['Count']

    # Determine Average NIH Percentile
    for pub in pubs:
        for year in sumData:
            if pub["year"] == year["Year"] and pub['nih_percentile'] is not None:
                year['Average NIH Percentile'] += pub['nih_percentile']/year['Count']

    #Import Thompson-Reuters JIF Information
    jifHeader = ["Rank", "Full Title", "JCR Title", "JIF", "JIFPercent"]
    jifRanks = []
    with open('JournalHomeGrid.csv', 'r') as jifFile:
        jifRankings = csv.DictReader(jifFile, fieldnames=jifHeader)
        jifRanks = list(jifRankings)
    jifRanks = [journal for journal in jifRanks if journal["Rank"].isnumeric()]
    for journal in jifRanks:
        try:
            journal["Rank"] = int(journal["Rank"])
        except:
            jifRanks.remove(journal)
        try:
            journal["JIF"] = float(journal["JIF"])
        except:
            journal["JIF"] = float(0)
        try:
            journal["JIFPercent"] = float(journal["JIFPercent"])
        except:
            journal["JIFPercent"] = float(0)

    # Compare each pub against JIF info
    listofjournals = [journal["JCR Title"].replace("-", " ") for journal in jifRanks]
    listofnames = [journal["Full Title"] for journal in jifRanks]
    pairs = {"AMYOTROPH LATERAL SCLER FRONTOTEMPORAL DEGENER": "AMYOTROPH LAT SCL FR",
        "FRONT NEUROSCI": "FRONT NEUROSCI SWITZ"}
    for pub in pubs:
        pub["journal"] = pub["journal"].upper()
        pub["journal"] = pub["journal"].replace(".", "")
        if pub["journal"] in pairs.keys():
                pub["JIF"] = jifRanks[listofjournals.index(pairs[pub["journal"]])]["JIF"]
                pub["JIF Percentile"] = jifRanks[listofjournals.index(pairs[pub["journal"]])]["JIFPercent"]
                continue
        elif pub["journal"] in listofjournals:
            pub["JIF"] = jifRanks[listofjournals.index(pub["journal"])]["JIF"]
            pub["JIF Percentile"] = jifRanks[listofjournals.index(pub["journal"])]["JIFPercent"]
            pairs[pub["journal"]] = pub["journal"]
        else:
            pub["JIF"] = 0
            pub["JIF Percentile"] = 0
            simJournals = {}
            for name in listofjournals:
                if similar(pub["journal"], name) >= 0.7 and pub["journal"][0] == name[0]:
                    simJournals[similar(pub["journal"], name)] = name
            countSim = 0
            for simJ in reversed(sorted(simJournals.keys())):
                if countSim >= 3:
                    break
                userJudge = input("Is {} the journal {}? Enter y/n: ".format(pub["journal"],
                    jifRanks[listofjournals.index(simJournals[simJ])]["Full Title"]))
                if userJudge == 'y':
                    pub["JIF"] = jifRanks[listofjournals.index(simJournals[simJ])]["JIF"]
                    pub["JIF Percentile"] = jifRanks[listofjournals.index(simJournals[simJ])]["JIFPercent"]
                    pairs[pub["journal"]] = simJournals[simJ]
                    break
                else:
                    countSim += 1
                    continue




    print("Journal Impact Factor Information Added.")

    #Write NCAN Data.xlsx, start with pubData
    workbook = xlsxwriter.Workbook('NCAN Data.xlsx')
    bold = workbook.add_format({'bold': True})
    pubData = workbook.add_worksheet('pubData')
    row = 0
    col = 0
    for header in sorted(pubsHeader):
        pubData.write(row, col, header.replace("_", " ").title(), bold)
        col += 1
    col = 0
    row += 1
    for pub in pubs:
        for header in sorted(pubsHeader):
            if header in pub.keys():
                pubData.write(row, col, pub[header])
                col += 1
            else:
                col += 1
        col = 0
        row += 1

    #Write Summary
    summary = workbook.add_worksheet('Summary')
    row = 0
    col = 0
    for header in list(sumHeader.keys()):
        summary.write(row, col, header, bold)
        col += 1
    col = 0
    row += 1
    for year in sumData:
        for header in sumHeader:
            if header in year.keys():
                summary.write(row, col, year[header])
                col += 1
            else:
                col += 1
        col = 0
        row += 1

    workbook.close()
    print("NCAN Bibliometric Assessment complete. View NCAN Data.xlsx for data")

def similar(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

# Run the program!
if __name__ == "__main__":
    main()
