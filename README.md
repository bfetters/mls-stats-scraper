MLS Statistics Scraper
============

Simple web scraper built to crawl through Major League Soccer statistics available from [mlssoccer.com](http://www.mlssoccer.com/) and write to text files for analysis.

Usage
--------

Copy ```mlsstatsscraper.py``` to preferred directory and update ```OUTPUT_DIR``` parameter to the location you want the text files written.

To run: ```python mlsstatsscraper.py```

#### Dependencies
- ```requests```
- ```BeautifulSoup```

Future Plans
--------

- Allow user to specify initialized values.
- Scrape player profiles for features like age, birthplace, nationality, etc.