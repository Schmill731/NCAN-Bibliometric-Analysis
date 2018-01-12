# Runs a bibliometric assessment of the given PubMed Search URL.
# Records bibliometrics using NIH's freely accessible iCite tool,
# Thompson-Reuters Journal Impact Factor (JIF), and Altmetrics.com.
#
# Created by Billy Schmitt, williamschmitt@college.harvard.edu for internal
# use at the National Center for Adaptive Neurotechnologies
# Last Modified 1/10/17
#
# Clone the GitHub Repository here: 
# https://github.com/Schmill731/NCAN-Bibliometric-Analysis


# Import Required Packages
import pkg_resources
import sys
import requests
import xlsxwriter
import collections
import csv
from difflib import SequenceMatcher
from xml.etree import ElementTree
import os

def bibrun():
    print("----------NCAN Bibliometric Assessment----------")
    print("Usage Instructions (Requires @neurotechcenter.org account): " +
        "https://docs.google.com/document/d/1Grehao_5cqiCKP3X8-6QblR93" +
        "LVuFMZcNhYH4j_Agzc/edit?usp=sharing\n\n\n")

    # Create header fields for Publications spreadsheet
    pubsHeader = set()
    pubsHeader.add("TR&D")

    #Search PubMed for IDs
    pmidList = []
    pubMedURL = input("Please copy and paste the URL from your PubMed Search: ")
    pubMedURL = pubMedURL.replace("https://www.ncbi.nlm.nih.gov/pubmed/?",
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&")
    pubMedURL = pubMedURL.replace("https://www.ncbi.nlm.nih.gov/pubmed?",
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&")
    pubMedURL = pubMedURL.replace("&cmd=DetailsSearch", "&retmax=1000")
    pubMedInfo = requests.get(pubMedURL)

    #Determine whether PubMed ID Search was Successful
    if pubMedInfo.status_code == 200:
        tree = ElementTree.fromstring(pubMedInfo.content)
        if tree.find('Count') == None:
            print(pubMedURL)
            print("Error obtaining PMIDs.")
            print("Aborting")
            return
        else:
            print(tree.find('Count').text + " PubMed IDs obtained.")
            for id in list(tree.find('IdList')):
                pmidList.append(id.text)
    else:
        print("Error obtaining PMIDs.")
        print("Response Code: " + str(pubMedInfo.status_code))
        print("Please check that you copied and pasted the URL correctly.")
        print("Aborting...")
        return

    #Search iCite for Relative Criteria Ratio
    iCite = requests.get("https://icite.od.nih.gov/api/pubs?pmids=" +
        ",".join(pmidList))
    if iCite.status_code == 200:
        print("iCite data collected.")
    else:
        print("Error getting iCite information.")
        print("Response Code: " + str(iCite.status_code))
        print("Aborting...")
        return

    #Create list of publication information
    pubs = iCite.json()["data"]
    for key in sorted(pubs[0].keys()):
        pubsHeader.add(key)
    pubsHeader.add("JIF")
    pubsHeader.add("JIF Percentile")
    pubsHeader.add("JIF Quartile")

    #Classify each publication according to its TR&D based on keywords or input
    for pub in pubs:
        pub["title"] = pub["title"].lower()

        #TR&D 1 Classifiers
        if "spinal cord injury" in pub["title"] or \
            "plasticity" in pub["title"] or \
            "h-reflex" in pub["title"] or \
            "operant conditioning" in pub["title"] or \
            "rats" in pub["title"]:
                pub["TR&D"] = 1

        #TR&D 2 Classifiers
        elif "brain" in pub["title"] and \
            "computer" in pub["title"] and \
            "interface" in pub["title"] or \
            "bci" in pub["title"] or \
            "eeg" in pub["title"] or \
            "p300" in pub["title"]:
                pub["TR&D"] = 2

        #TR&D 3 Classifiers
        elif "cortical" in pub["title"] or \
            "electrocorticography" in pub["title"] or \
            "ecog" in pub["title"] or \
            "cortex" in pub["title"] or \
            "electrocorticographic" in pub["title"] or \
            "epilepsy" in pub["title"]:
                pub["TR&D"] = 3

        #Ask for manual classification
        else:
            while True:
                trd = input('Under which TR&D does "{}" fall (1/2/3/c/n)? '.format(pub["title"]))
                if trd in ["1", "2", "3", "c", "n"]:
                    try:
                        pub["TR&D"] = int(trd)
                        break
                    except:
                        pub["TR&D"] = trd
                        break

    # Create variables to holder summary statistics and header info
    sumData = []
    sumHeaderNames = ["TR&D", "Year", "Count", "Weighted RCR", "Mean RCR",
        "Average NIH Percentile", "Num in JIF Q1", "Percent in JIF Q1", 
        "Average JIF Quartile", "Average JIF", "Sum JIF",
        "Average JIF Percentile", "Social Media Account Shares",
        "Facebook Posts", "Blog Posts", "Google Plus Posts", "News Articles",
        "Peer Review Site Posts", "Total Social Media Posts", "QNA Posts",
        "Reddit Posts", "Tweets", "Wikiepedia", "Unique Authors", "New Authors"]
    sumHeader = collections.OrderedDict()
    for info in sumHeaderNames:
        sumHeader[info] = None
    minYear = 3000
    maxYear = 0
    for pub in pubs:
        if pub["year"] < minYear:
            minYear = pub["year"]
        if pub["year"] > maxYear:
            maxYear = pub["year"]
    for trd in [1, 2, 3, 'c', 'n', "Total"]:
        for yr in range(minYear, maxYear + 1):
            sumData.append({'TR&D': trd, 'Year': yr, 'Count': 0,
                'Weighted RCR': 0, 'Mean RCR': 0, 'Average NIH Percentile': 0,
                'Num in JIF Q1': 0, 'Percent in JIF Q1': 0,
                'Average JIF Quartile': 0, 'Average JIF': 0, 'Sum JIF': 0,
                'Average JIF Percentile': 0, "Social Media Account Shares": 0,
                "Facebook Posts": 0, "Blog Posts": 0, "Google Plus Posts": 0,
                "News Articles": 0, "Peer Review Site Posts": 0,
                "Total Social Media Posts": 0, "QNA Posts": 0,
                "Reddit Posts": 0, "Tweets": 0, "Wikipedia Mentions": 0,
                "Unique Authors": 0, "New Authors": 0, "authors": []})

    # Create variables and flags to signify unique and new authors
    newAuthors = {}
    for trd in [1, 2, 3, 'c', 'n', "Total"]:
        for yr in range(minYear, maxYear + 1):
            newAuthors[(trd, yr)] = []
    same = False
    new = True
    for sumStat in sumData:
        for pub in pubs:
            authors = pub["authors"].split(", ")

            # Determine whether it's a unique author
            if pub["year"] == sumStat["Year"] and \
                (pub["TR&D"] == sumStat["TR&D"] or \
                sumStat["TR&D"] == "Total"):
                    sumStat["authors"] += [pubAuthor for pubAuthor in authors if not sameAuthor(pubAuthor, sumStat["authors"])]

            # Create a list of all authors for each summary category
            if (pub["TR&D"] == sumStat["TR&D"] or \
                sumStat["TR&D"] == 'Total') and \
                pub["year"] <= sumStat["Year"]:
                    newAuthors[(sumStat["TR&D"], sumStat["Year"])] += [pubAuthor
                        for pubAuthor in authors if not sameAuthor(pubAuthor,
                        newAuthors[(sumStat["TR&D"], sumStat["Year"])])]

        # Calculate the number of new authors and unique authors
        if sumStat["Year"] > minYear:
            for past in range(minYear, sumStat["Year"]):
                newAuthors[(sumStat["TR&D"], sumStat["Year"])] = [author
                    for author in newAuthors[(sumStat["TR&D"], sumStat["Year"])]
                    if author not in newAuthors[(sumStat["TR&D"], past)]]
            sumStat["New Authors"] = len(newAuthors[(sumStat["TR&D"], sumStat["Year"])])
        sumStat["Unique Authors"] = len(sumStat["authors"])
    
    #Determine number of publications per year
    for sumStat in sumData:
        sumStat["Count"] = len([pub for pub in pubs
            if pub["year"] == sumStat["Year"] and \
            (pub["TR&D"] == sumStat["TR&D"] or \
            sumStat["TR&D"] == "Total")])

    #Determine Weighted RCR and Mean RCR
    for sumStat in sumData:
        sumStat['Weighted RCR'] = sum([pub['relative_citation_ratio']
            for pub in pubs if pub["year"] == sumStat["Year"] and \
            pub['relative_citation_ratio'] is not None and \
            (pub["TR&D"] == sumStat["TR&D"] or sumStat["TR&D"] == "Total")])
        try:
            sumStat['Mean RCR'] = sumStat['Weighted RCR']/sumStat['Count']
        except:
            sumStat['Mean RCR'] = 0

    # Determine Average NIH Percentile
    for sumStat in sumData:
        try:
            sumStat['Average NIH Percentile'] = sum([pub['nih_percentile']
                for pub in pubs if pub["year"] == sumStat["Year"] and \
                pub['nih_percentile'] is not None and \
                (pub["TR&D"] == sumStat["TR&D"] or \
                sumStat["TR&D"] == "Total")])/sumStat['Count']
        except:
            sumStat['Average NIH Percentile'] = 0

    #Import Thompson-Reuters JIF Information
    jifHeader = ["Rank", "Full Title", "JCR Title", "JIF", "JIFPercent"]
    jifRanks = []
    path = pkg_resources.resource_filename('ncan_bibrun', 'JournalHomeGrid.csv')
    with open(path, 'r') as jifFile:
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
    pairs = {"AMYOTROPH LATERAL SCLER FRONTOTEMPORAL DEGENER": "AMYOTROPH LAT SCL FR",
        "FRONT NEUROSCI": "FRONT NEUROSCI SWITZ",
        "FRONT COMPUT NEUROSCI": "FRONT COMPUT NEUROSC",
        "J SPEECH LANG HEAR RES": "J SPEECH LANG HEAR R",
        "IEEE TRANS NEURAL SYST REHABIL ENG": "IEEE T NEUR SYS REH",
        "AM J PHYSIOL RENAL PHYSIOL": "AM J PHYSIOL RENAL",
        "ARCH PHYS MED REHABIL": "ARCH PHYS MED REHAB",
        "NEUROUROL URODYN": "NEUROUROL URODYNAM",
        "SCI REP": "SCI REP UK",
        "EPILEPSY BEHAV CASE REP": "EPILEPSY BEHAV",
        "J NEUROSCI METHODS": "J NEUROSCI METH",
        "PROC NATL ACAD SCI USA": "P NATL ACAD SCI USA",
        "REV NEUROSCI": "REV NEUROSCIENCE",
        "J PHYSIOL (LOND)": "J PHYSIOL LONDON",
        "J NEUROTRAUMA": "J NEUROTRAUM"}

    for pub in pubs:
        pub["journal"] = pub["journal"].upper()
        pub["journal"] = pub["journal"].replace(".", "")

        #Check if we've already paired it with JIF info
        if pub["journal"] in pairs.keys():
                pub["JIF"] = jifRanks[listofjournals.index(pairs[pub["journal"]])]["JIF"]
                pub["JIF Percentile"] = jifRanks[listofjournals.index(pairs[pub["journal"]])]["JIFPercent"]
                continue

        #Check if it's in the list of journals
        elif pub["journal"] in listofjournals:
            pub["JIF"] = jifRanks[listofjournals.index(pub["journal"])]["JIF"]
            pub["JIF Percentile"] = jifRanks[listofjournals.index(pub["journal"])]["JIFPercent"]
            pairs[pub["journal"]] = pub["journal"]

        # See what the top 3 similar journals are and present to user
        else:
            pub["JIF"] = 0
            pub["JIF Percentile"] = 0
            if pub["journal"] in ["FRONT INTEGR NEUROSCI", "FRONT NEUROENG"]:
                continue
            simJournals = {}
            for name in listofjournals:
                if similar(pub["journal"], name) >= 0.7 and pub["journal"][0] == name[0]:
                    simJournals[similar(pub["journal"], name)] = name
            countSim = 0
            for simJ in reversed(sorted(simJournals.keys())):
                if countSim >= 3:
                    break
                userJudge = input("Is {} the journal {} (y/n)? ".format(pub["journal"],
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
    for sumStat in sumData:
        sumStat["Num in JIF Q1"] = len([pub for pub in pubs
            if pub["year"] == sumStat["Year"] and \
            pub["JIF Quartile"] == 1 and \
            (pub["TR&D"] == sumStat["TR&D"] or sumStat["TR&D"] == "Total")])
        try:
            sumStat["Percent in JIF Q1"] = sumStat["Num in JIF Q1"]/sumStat["Count"]
        except:
            sumStat['Percent in JIF Q1'] = 0
        for pub in pubs:
            if pub["year"] == sumStat["Year"] and (pub["TR&D"] == sumStat["TR&D"] or \
                sumStat["TR&D"] == "Total"):
                try:
                    sumStat["Average JIF Quartile"] += pub["JIF Quartile"]/sumStat["Count"]
                except:
                    sumStat['Average JIF Quartile'] = 0
                sumStat["Sum JIF"] += pub["JIF"]
                try:
                    sumStat["Average JIF Percentile"] += pub["JIF Percentile"]/sumStat["Count"]
                except:
                    sumStat['Average JIF Percentile'] = 0
        try:
            sumStat["Average JIF"] += sumStat["Sum JIF"]/sumStat["Count"]
        except:
            sumStat['Average JIF'] = 0


    print("Journal Impact Factor Information Added.")

    #Get Altmetric Data
    listofinfo = []
    notFound = False
    for pmid in pmidList:
        response = requests.get("https://api.altmetric.com/v1/pmid/" + pmid)
        if response.status_code == 200:
            listofinfo.append(response.json())
        elif response.status_code == 404:
            notFound = True
        elif response.status_code != 404:
            print("Error getting article (may be rate-limited)")
    if notFound:
        print("Not all articles on Altmetric. Data will be incomplete.")

    #Add Altmetric Data
    for info in listofinfo:
        info["pmid"] = int(info["pmid"])
        for pub in pubs:
            if info["pmid"] == pub["pmid"]:
                for key in info.keys():
                    if key[0:5] == "cited":
                        if isinstance(info[key], str) and info[key].isnumeric():
                            pub[key] = int(info[key])
                            pubsHeader.add(key)
                        elif isinstance(info[key], int) or \
                            isinstance(info[key], float):
                                pub[key] = info[key]
                                pubsHeader.add(key)

    #Tally Altmetric Data
    for sumStat in sumData:
        for pub in pubs:
            if pub["year"] == sumStat["Year"] and \
                (pub["TR&D"] == sumStat["TR&D"] or \
                sumStat["TR&D"] == "Total"):
                    for key in pub.keys():
                        if key == "cited_by_accounts_count":
                            sumStat["Social Media Account Shares"] += pub["cited_by_accounts_count"]
                        if key == "cited_by_fbwalls_count":
                            sumStat["Facebook Posts"] += pub["cited_by_fbwalls_count"]
                        if key == "cited_by_feeds_count":
                            sumStat["Blog Posts"] += pub["cited_by_feeds_count"]
                        if key == "cited_by_gplus_count":
                            sumStat["Google Plus Posts"] += pub["cited_by_gplus_count"]
                        if key == "cited_by_msm_count":
                            sumStat["News Articles"] += pub["cited_by_msm_count"]
                        if key == "cited_by_peer_review_sites_count":
                            sumStat["Peer Review Site Posts"] += pub["cited_by_peer_review_sites_count"]
                        if key == "cited_by_posts_count":
                            sumStat["Total Social Media Posts"] += pub["cited_by_posts_count"]
                        if key == "cited_by_qna_count":
                            sumStat["QNA Posts"] += pub["cited_by_qna_count"]
                        if key == "cited_by_rdts_count":
                            sumStat["Reddit Posts"] += pub["cited_by_rdts_count"]
                        if key == "cited_by_tweeters_count":
                            sumStat["Tweets"] += pub["cited_by_tweeters_count"]
                        if key == "cited_by_wikipedia_count":
                            sumStat["Wikipedia Mentions"] += pub["cited_by_wikipedia_count"]

    print("Altmetric Data Added.")

    #Write NCAN Data.xlsx, start with pubData
    desktop_dir = os.path.join(os.path.expanduser('~'), "Desktop")
    workbook = xlsxwriter.Workbook(desktop_dir + '/NCAN Bibliometric Data.xlsx')
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
    for sumStat in sumData:
        for header in sumHeader:
            if header in sumStat.keys():
                summary.write(row, col, sumStat[header])
                col += 1
            else:
                col += 1
        col = 0
        row += 1
        if sumStat["Year"] == maxYear:
            for header in list(sumHeader.keys()):
                summary.write(row, col, header, bold)
                col += 1
            col = 0
            row += 1

    workbook.close()
    print("NCAN Bibliometric Assessment complete. View NCAN Data.xlsx for data")

    exit()

def similar(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

def sameAuthor(author, lst):
    same = False
    for elt in lst:
        if author.split(" ")[-1] == elt.split(" ")[-1] and \
            author[0] == elt[0]:
                same = True
    return same
