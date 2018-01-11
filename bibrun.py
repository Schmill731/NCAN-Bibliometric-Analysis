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
from xml.etree import ElementTree

def main():
    # Header fields for Pubs worksheet
    pubsHeader = set()
    pubsHeader.add("TR&D")

    #Search PubMed for IDs
    pmidList = []
    pubMedInfo = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db" +
        "=pubmed&term=P41%20EB018783/EB/NIBIB%20NIH%20HHS/United%20States" +
        "%5BGrant%20Number%5D%20OR%20%28%28%28%28%28%28%222013%22%5BPDAT%" +
        "5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Schalk%2C%20Gerwin%5B" +
        "Full%20Author%20Name%5D%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%2" +
        "0%223000%22%5BPDAT%5D%29%20AND%20Wolpaw%2C%20Jonathan%5BFull%20Aut" +
        "hor%20Name%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%2230" +
        "00%22%5BPDAT%5D%29%20AND%20Brunner%2C%20Peter%5BFull%20Author%20Na" +
        "me%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5" +
        "BPDAT%5D%29%20AND%20McFarland%20DJ%5BAuthor%5D%29%29%20OR%20%28%28" +
        "%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Vaugh" +
        "an%2C%20Theresa%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%222" +
        "013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Heckman" +
        "%2C%20Susan%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%22201" +
        "3%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Carp%2C%2" +
        "0Jonathan%5BFull%20Author%20Name%5D%29%20OR%20%28%28%222013%22%5B" +
        "PDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20McCane%20L%5BAuthor" +
        "%5D%29&retmax=1000")
    if pubMedInfo.status_code == 200:
        tree = ElementTree.fromstring(pubMedInfo.content)
        print(tree.find('Count').text + " PubMed IDs obtained.")
        for id in list(tree.find('IdList')):
            pmidList.append(id.text)
    else:
        print("Error getting PMIDs.")
        return

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

    #Ask about TR&D
    for pub in pubs:
        pub["title"] = pub["title"].lower()
        if "spinal" in pub["title"] and "cord" in pub["title"] and \
            "injury" in pub["title"] or "plasticity" in pub["title"] or \
            "h-reflex" in pub["title"] or "operant" in pub["title"] or \
            "rats" in pub["title"]:
            pub["TR&D"] = 1
        elif "brain" in pub["title"] and "computer" in pub["title"] and \
            "interface" in pub["title"] or "bci" in pub["title"] or \
            "eeg" in pub["title"] or "p300" in pub["title"]:
            pub["TR&D"] = 2
        elif "cortical" in pub["title"] or "electrocorticography" in pub["title"] or \
            "ecog" in pub["title"] or "cortex" in pub["title"] or \
            "electrocorticographic" in pub["title"] or "neural" in pub["title"]:
            pub["TR&D"] = 3
        else:
            while True:
                trd = input('Under which TR&D does "{}" fall (1/2/3)? '.format(pub["title"]))
                if trd in ["1", "2", "3"]:
                    pub["TR&D"] = int(trd)
                    break

    # Create variable to hold summary data
    sumData = []
    sumHeader = collections.OrderedDict()
    sumHeader["TR&D"] = None
    sumHeader["Year"] = None
    sumHeader["Count"] = None
    sumHeader["Weighted RCR"] = None
    sumHeader["Mean RCR"] = None
    sumHeader["Average NIH Percentile"] = None
    sumHeader["Num in JIF Q1"] = None
    sumHeader["Percent in JIF Q1"] = None
    sumHeader["Average JIF Quartile"] = None
    sumHeader["Average JIF"] = None
    sumHeader["Sum JIF"] = None
    sumHeader["Average JIF Percentile"] = None
    sumHeader["Social Media Account Shares"] = None
    sumHeader["Facebook Posts"] = None
    sumHeader["Blog Posts"] = None
    sumHeader["Google Plus Posts"] = None
    sumHeader["News Articles"] = None
    sumHeader["Peer Review Site Posts"] = None
    sumHeader["Total Social Media Posts"] = None
    sumHeader["QNA Posts"] = None
    sumHeader["Reddit Posts"] = None
    sumHeader["Tweets"] = None
    sumHeader["Wikipedia Mentions"] = None
    for trd in [1, 2, 3, "Total"]:
        for yr in [2013, 2014, 2015, 2016, 2017]:
            sumData.append({'TR&D': trd, 'Year': yr, 'Count': 0, 'Weighted RCR': 0,
                'Mean RCR': 0, 'Average NIH Percentile': 0, 'Num in JIF Q1': 0,
                'Percent in JIF Q1': 0, 'Average JIF Quartile': 0, 'Average JIF': 0,
                'Sum JIF': 0, 'Average JIF Percentile': 0, "Social Media Account Shares": 0,
                "Facebook Posts": 0, "Blog Posts": 0, "Google Plus Posts": 0,
                "News Articles": 0, "Peer Review Site Posts": 0, "Total Social Media Posts": 0,
                "QNA Posts": 0, "Reddit Posts": 0, "Tweets": 0, "Wikipedia Mentions": 0})
    
    #Determine number of publications per year
    for year in sumData:
        for pub in pubs:
            if pub["year"] == year["Year"] and (pub["TR&D"] == year["TR&D"] or \
                year["TR&D"] == "Total"):
                year["Count"] += 1

    #Determine Weighted RCR and Mean RCR
    for year in sumData:
        for pub in pubs:
            if pub["year"] == year["Year"] and pub['relative_citation_ratio'] is not None and \
            (pub["TR&D"] == year["TR&D"] or year["TR&D"] == "Total"):
                year['Weighted RCR'] += pub['relative_citation_ratio']
                year['Mean RCR'] += pub['relative_citation_ratio']/year['Count']

    # Determine Average NIH Percentile
    for year in sumData:
        for pub in pubs:
            if pub["year"] == year["Year"] and pub['nih_percentile'] is not None and \
            (pub["TR&D"] == year["TR&D"] or year["TR&D"] == "Total"):
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
        "FRONT NEUROSCI": "FRONT NEUROSCI SWITZ", "FRONT COMPUT NEUROSCI": "FRONT COMPUT NEUROSC",
        "J SPEECH LANG HEAR RES": "J SPEECH LANG HEAR R", "IEEE TRANS NEURAL SYST REHABIL ENG": 
        "IEEE T NEUR SYS REH", "AM J PHYSIOL RENAL PHYSIOL": "AM J PHYSIOL RENAL", "ARCH PHYS MED REHABIL": 
        "ARCH PHYS MED REHAB", "NEUROUROL URODYN": "NEUROUROL URODYNAM", "SCI REP": "SCI REP UK",
        "EPILEPSY BEHAV CASE REP": "EPILEPSY BEHAV", "J NEUROSCI METHODS": "J NEUROSCI METH",
        "PROC NATL ACAD SCI USA": "P NATL ACAD SCI USA", "REV NEUROSCI": "REV NEUROSCIENCE",
        "J PHYSIOL (LOND)": "J PHYSIOL LONDON", "J NEUROTRAUMA": "J NEUROTRAUM"}
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

    #Determine JIF Quartiles
    for pub in pubs:
        if pub["JIF Percentile"] >= 75:
            pub["JIF Quartile"] = 1
        elif pub["JIF Percentile"] >= 50:
            pub["JIF Quartile"] = 2
        elif pub["JIF Percentile"] >= 25:
            pub["JIF Quartile"] = 3
        else:
            pub["JIF Quartile"] = 4

    # Determine JIF Metrics
    for year in sumData:
        for pub in pubs:
            if pub["year"] == year["Year"] and pub["JIF Quartile"] == 1 and \
            (pub["TR&D"] == year["TR&D"] or year["TR&D"] == "Total"):
                year["Num in JIF Q1"] += 1
            if pub["year"] == year["Year"] and (pub["TR&D"] == year["TR&D"] or \
                year["TR&D"] == "Total"):
                year["Average JIF Quartile"] += pub["JIF Quartile"]/year["Count"]
                year["Average JIF"] += pub["JIF"]/year["Count"]
                year["Sum JIF"] += pub["JIF"]
                year["Average JIF Percentile"] += pub["JIF Percentile"]/year["Count"]
    for year in sumData:
        year["Percent in JIF Q1"] = year["Num in JIF Q1"]/year["Count"]


    print("Journal Impact Factor Information Added.")

    # DEBUG TEST
    listofinfo = []
    with open("altmetric.csv", "r") as altmetricFile:
        altmetricData = csv.DictReader(altmetricFile)
        listofinfo = list(altmetricData)

    # #Get Altmetric Data
    # listofinfo = []
    # for pmid in pmidList:
    #     response = requests.get("https://api.altmetric.com/v1/pmid/" + pmid)
    #     if response.status_code == 200:
    #         listofinfo.append(response.json())
    #     elif response.status_code != 404:
    #         print("Error getting article (may be rate-limited)")

    #Add Altmetric Data
    for info in listofinfo:
        info["pmid"] = int(info["pmid"])
        for pub in pubs:
            if info["pmid"] == pub["pmid"]:
                for key in info.keys():
                    if key[0:5] == "cited":
                        if info[key].isnumeric():
                            pub[key] = int(info[key])
                            pubsHeader.add(key)

    #Tally Altmetric Data
    for year in sumData:
        for pub in pubs:
            if pub["year"] == year["Year"] and (pub["TR&D"] == year["TR&D"] or year["TR&D"] == "Total"):
                for key in pub.keys():
                    if key == "cited_by_accounts_count":
                        year["Social Media Account Shares"] += pub["cited_by_accounts_count"]
                    if key == "cited_by_fbwalls_count":
                        year["Facebook Posts"] += pub["cited_by_fbwalls_count"]
                    if key == "cited_by_feeds_count":
                        year["Blog Posts"] += pub["cited_by_feeds_count"]
                    if key == "cited_by_gplus_count":
                        year["Google Plus Posts"] += pub["cited_by_gplus_count"]
                    if key == "cited_by_msm_count":
                        year["News Articles"] += pub["cited_by_msm_count"]
                    if key == "cited_by_peer_review_sites_count":
                        year["Peer Review Site Posts"] += pub["cited_by_peer_review_sites_count"]
                    if key == "cited_by_posts_count":
                        year["Total Social Media Posts"] += pub["cited_by_posts_count"]
                    if key == "cited_by_qna_count":
                        year["QNA Posts"] += pub["cited_by_qna_count"]
                    if key == "cited_by_rdts_count":
                        year["Reddit Posts"] += pub["cited_by_rdts_count"]
                    if key == "cited_by_tweeters_count":
                        year["Tweets"] += pub["cited_by_tweeters_count"]
                    if key == "cited_by_wikipedia_count":
                        year["Wikipedia Mentions"] += pub["cited_by_wikipedia_count"]

    print("Altmetric Data Added.")

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
        if year["Year"] == 2017:
            for header in list(sumHeader.keys()):
                summary.write(row, col, header, bold)
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
