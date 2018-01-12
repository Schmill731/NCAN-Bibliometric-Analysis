==============
NCAN Bibliometric Analysis Script
==============

--------------
Created by Billy Schmitt
--------------

Introduction
-------------

The NCAN Bibliometric Analysis Script was built to cultivate a list of research publications from the URL of a PubMed Search and report several bibliometrics for each publication, as well as the yearly statistics. Bibliometrics calculated include the number of publications; iCite RCR, Weighted RCR, and Mean RCR; Thompson's Reuters' Journal Impact Factor (JIF), JIF Quartile, and JIF Percentile; and Altmetrics.com's count of citations in social media and news posts.The script has the following features:

    * It can take the URL of any PubMed search and perform an analysis.
    * It will automatically classify all articles to the appropriate Team Research & Development Division of NCAN according to whether it contains one of the following words. If it cannot be automatically classified, the user will be asked to classify it into one of the TR&Ds (1, 2, 3), a collaborative & service project (c) or none of the above (n).
        - Team Research & Development 1:
            + Spinal Cord Injury
            + Plasticity
            + H-Reflex
            + Operant Conditioning
            + Rats
        - Team Research & Development 2:
            + Brain Computer Interface
            + BCI
            + EEG
            + P300
        - Team Research & Development 3:
            + Cortical
            + Electrocorticography
            + ECoG
            + Cortex
            + Electrocorticographic
            + Epilepsy
    * It will automatically find the Journal Impact Factor for each publication's journal. Occassionally, due to errors in the abbreviated title of the journal, the script will ask the user to confirm whether a given abbreviated title matches a journal.
    * It will automatically create an Excel spreadsheet with all the data titled "NCAN Bibliometric Data.xlsx", which will be saved on the user's Desktop.


Installation
------------

The NCAN Bibliometric Analysis Script requries Python 3 to run, and must be installed prior to use. After you ensure that your system is capable of running Python 3, follow these steps for installation:

1. Download or clone the GitHub repository for the code to your own machine from: https://github.com/Schmill731/NCAN-Bibliometric-Analysis
2. Open a new terminal window
3. Navigate to the outer ``ncan_bibrun`` folder in your terminal.
4. Run ``pip3 install .``
5. All dependencies and the code should install on your system.
6. Installation complete!


Use
----

After you have properly installed ``ncan_bibrun`` to your system, you may use it by opening any terminal window and entering ``ncan-bibrun``. As it runs, the script may ask the following:

* The URL of the PubMed search that you wish to perform an analysis on.
* To assign a publication to the appropriate TR&D. Choices include 1, 2, 3, 'c' for Collaborative & Service Project, or 'n' for none of the above.
* To confirm whether a journal title abbreviation matches the name of the journal.

Occassionally, the PubMed Search URL may be too long to copy and paste into your terminal. When this occurs, you can copy and paste the URL into a ``.txt`` file and pipe the URL to the script with the following command: ``cat filename.txt - | ncan-bibrun``.

To run a sample of the script or to perform an analysis of all NCAN publications from 2013-2017, run: ``ncan-bibrun`` in your terminal and use the following as your URL: ``https://www.ncbi.nlm.nih.gov/pubmed?term=P41%20EB018783/EB/NIBIB%20NIH%20HHS/United%20States%5BGrant%20Number%5D%20OR%20%28%28%28%28%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Schalk%2C%20Gerwin%5BFull%20Author%20Name%5D%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Wolpaw%2C%20Jonathan%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Brunner%2C%20Peter%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20McFarland%20DJ%5BAuthor%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Vaughan%2C%20Theresa%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Heckman%2C%20Susan%5BFull%20Author%20Name%5D%29%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20Carp%2C%20Jonathan%5BFull%20Author%20Name%5D%29%20OR%20%28%28%222013%22%5BPDAT%5D%20%3A%20%223000%22%5BPDAT%5D%29%20AND%20McCane%20L%5BAuthor%5D%29&cmd=DetailsSearch``.

Uninstallation
--------------

To uninstall the script from your machine, open a terminal window and run ``pip3 uninstall ncan_bibrun``.
