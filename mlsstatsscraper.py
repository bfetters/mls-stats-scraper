import requests
import json
import pandas as pd

from bs4 import BeautifulSoup
from collections import defaultdict
from itertools import product


class MlsStatsScraper(object):
    """ Scraper used to get statistics from www.mlssoccer.com """

    def __init__(self, output_dir, root_url, endpoint, params):
        """ Initialize new instance of the class """

        self.output_dir = output_dir
        self.root_url = root_url
        self.endpoint = endpoint
        self.params = params
        self.next_page = ''
        self.last_page = ''
        self.franchises = []
        self.years = []
        self.season_types = []
        self.groups = []

    def scrape_root(self):
        """
        Scrape root page first to retrieve last_page value and all possible menu
        options available from stats form for params/url generation downstream.
        """

        # Start at root page
        r = requests.get(self.root_url + self.endpoint, params=self.params)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Get the last page with data. Add one because we start at page 0.
        self.last_page = int(soup.select('.pager-last')[0].a['href'].split('=')[1])
        self.last_page += 1

        # Build lists of all possible menu options for table
        for menu in soup.select('select[name]'):
            if menu['name'] == 'franchise':
                self.franchises = [(option['value'], option.contents[0])
                                   for option in menu.find_all('option')
                                   if option['value'] != 'select']
            elif menu['name'] == 'year':
                self.years = [option['value']
                              for option in menu.find_all('option')
                              if option['value'] != 'select']
            elif menu['name'] == 'season_type':
                self.season_types = [option['value']
                                     for option in menu.find_all('option')
                                     if option['value'] != 'select']
            elif menu['name'] == 'group':
                self.groups = [option['value']
                               for option in menu.find_all('option')
                               if option['value'] != 'select']

        # Create list of all parameter combinations using menus
        self.menu_options = [self.season_types, self.groups, self.years]
        self.build_param_list()

    def build_param_list(self):
        """
        Based on scraped menus build a comprehensive list of all params
        combinations in dict form to use with requests call.
        pass in to api.
        """

        self.params_list = [{'season_type': params[0],
                             'group': params[1],
                             'year': params[2]}
                            for params in list(product(*self.menu_options))]

    def scrape_branches(self):
        """
        Crawl all branches of the stats form by using the param_list built
        with every combination of parameters.
        """

        # Loop through every parameter combination and scrape the page
        for params in self.params_list:

            data = defaultdict(list)
            fname = '_'.join([params['season_type'],
                              params['year'],
                              params['group']])

            print 'Scraping... {}'.format(params)

            # Each parameter list might contain multiple pages, so we need to
            # loop through each page of the results until we get to the end
            for page in xrange(self.last_page):

                # Add current page to our params
                params['page'] = page

                r = requests.get(self.root_url + self.endpoint, params=params)
                soup = BeautifulSoup(r.text, 'html.parser')

                # Loop through each row of statistics
                for item in soup.select('tr[class]'):

                    # Loop through each column and get the (key,value)
                    # to load into dictionary
                    for column in item.find_all('td'):

                        # Last page is shared across all statistics tables, so
                        # we don't always need to loop through all pages.
                        if column.contents[0] == 'Stats Unavailable':
                            break

                        # Set key to column title
                        key = column['data-title']

                        # The player data includes a link to the player profile,
                        # which we split to only get the relevant piece.
                        if key == 'Player':
                            # Just get player name, not link to profile
                            try:
                                profile = column.a['href']
                                name = column.a.contents[0]
                            # For cases where there isn't a link to the profile
                            except:
                                profile = None
                                name = column.contents[0]
                            value = (profile, name)

                            data['Profile'].append(profile)
                            data['Name'].append(name)
                        else:
                            value = column.contents[0]
                            data[key].append(value)

            # Save newly scraped data to file
            with open('./data/' + fname + '.txt', 'w') as f:
                json.dump(data, f)

    def __describe__(self):
        """ Print all current attributes of the class """

        attrs = vars(self)
        print '\n'.join("%s: %s" % item for item in attrs.items())

if __name__ == '__main__':

    # Hardcoded initalization variable(s)
    OUTPUT_DIR = './data/'
    ROOT_URL = 'http://www.mlssoccer.com/stats/'
    ENDPOINT = 'season'
    PARAMS = {'page': 0}
    VERBOSE = False

    # Initialize scraper
    scraper = MlsStatsScraper(OUTPUT_DIR, ROOT_URL, ENDPOINT, PARAMS)

    # Scrape root page first then crawl branches.
    print "Scraping root..."
    scraper.scrape_root()
    print "Scraping branches..."
    scraper.scrape_branches()