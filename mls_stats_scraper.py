from bs4 import BeautifulSoup
import requests
from collections import OrderedDict

DEBUG = True

class MlsStatsScraper(object):
    """
    Scraper class used to get statistics from www.mlssoccer.com
    """
    def __init__(self): #(self,db,collection):
        self.stat_type = self.getStatType()
        self.root_url = 'http://www.mlssoccer.com/'
        self.url = self.root_url + self.stat_type
        self.raw = ''
        self.data = ''
        self.next_page = ''
        self.last_page = ''

    def scrape(self):
        """
        Scrape url using requests and BeautifulSoup to get raw data.
        Input: self
        Output: None
        """

        # scrape the initial page first
        self.scrapePage(self.url)

        # now loop through all the other pages and scrape
        # if there is a next_page and we are not at the last page
        for i in range(0,int(self.last_page[0].split('page=')[1]) + 1):
            # generate the next url to scrape and append to existing data
            if len(self.next_page) > 0:
                next_url = self.root_url + self.next_page[0]
                print next_url
                self.scrapePage(next_url)

    def scrapePage(self,url):
        """
        Scrape page for the provided url
        Input: self, string - url to scrape
        Output: None
        """

        # scrape page for raw data
        r  = requests.get(url)
        self.raw = BeautifulSoup(r.text)

        # parse raw data to get headers and player stats
        self.data = self.parseData()

    def getStatType(self):
        """
        Ask user to choose which stat type they want to scrape: (1) season, (2) alltime, (3)team.
        Input: self
        Output: string (season, alltime, team)
        """
        # get input from user, if invalid print message and ask again
        choice = raw_input("Choose the stat type you want: season(s)/alltime(a)/team(t) stats?  ")
        if choice.lower() != 's' and choice.lower() != 'a' and choice.lower() != 't':
            print "'{0}' is not valid. Enter 's', 'a', or 't'.".format(choice)
            self.getStatType()
        # translate input choice to actual value to append to url
        else:
            if choice.lower() == 's':
                choice = '/stats/season'
            elif choice.lower() == 'a':
                choice = '/stats/alltime'
            else:
                choice = '/stats/team'

        return choice

    def getHeaders(self):
        """
        Get headers for the data we are about to scrape.
        Input: None
        Output: OrderedDict() with the column headers defined and all values = None
        """
        # set column headers as dict keys using ordered dict to simply data entry later
        headers = OrderedDict()
        for th in self.raw.find_all('th'):
            # if title doesn't exist or is blank get actual value
            if th.get('title') == None or th.get('title') == '':
                headers[str(th.string).replace(' ','')] = None
            else:
                headers[th.get('title').replace(' ','')] = None

        return headers

    def parseData(self):
        """
        Populate a dictionary from the raw scraped data with each column header
        as a key and all data from that column as values.
        Input: self
        Output: dict containing the structured data
        """

        if self.next_page == '':
            # First, we want to get the headers
            hdr_dict = self.getHeaders()
            # Now, we want to get the actual data for each column as values
            stat_dict = self.getStats(hdr_dict)
        else:
            stat_dict = self.getStats(self.data)

        self.next_page = [pager_next.get('href')
                            for pager_next in self.raw.find_all('a')
                            if pager_next.get('title') == 'Go to next page']
        self.last_page = [pager_last.get('href')
                            for pager_last in self.raw.find_all('a')
                            if pager_last.get('title') == 'Go to last page']

        return stat_dict

    def getStats(self,dict):
        """
        Get all data from each column in the table and set it as values in the
        appropriate key created using the headers in getHeaders().
        Input: dict containing all headers as keys
        Output: dict with headers mapped to column data as values
        """
        # loop through each data column and populate values
        for idx in range(0,len(self.raw.find_all('td'))):
            # the first iteration needs to replace the none, all other values are appended
            if idx == 0 or idx%len(dict) == 0:
                for i,k in enumerate(dict):
                    if dict[k] == None:
                        dict[k] = [str(self.raw.find_all('td')[idx+i].string)]
                    else:
                        dict[k].append(str(self.raw.find_all('td')[idx+i].string))
        return dict

if __name__ == '__main__':
    # initialize scraper class
    scraper  = MlsStatsScraper()
    scraper.scrape()