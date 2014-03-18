from bs4 import BeautifulSoup
from selenium import webdriver
import string, re
from itertools import tee, izip

def get_page(url):

    print "getting url: " + url
    driver = webdriver.PhantomJS()
    driver.get(url)
    data = driver.page_source

    driver.quit()
    soup = BeautifulSoup(data)

    return soup

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def make_seasons_array():
    base = '20'
    arr = []
    ret = []
    for num in range(3,15): 
        if len(str(num)) < 2:
            start = base + '0' + str(num)
        else:
            start = base + str(num)
        arr.append(start)
    for start, end in pairwise(arr):
        season = start + '-' + end
        ret.append(season)
    return (arr, ret)

def get_stats():

    teamFile = open('textfiles/teams_statsheet.txt', 'r')
    
    # TargetURL
    # http://statsheet.com/mcb/teams/syracuse/team_stats?season=2013-2014&type=all
    
    (years, seasons) = make_seasons_array()
    # url = 'http://statsheet.com/mcb/teams/syracuse/team_stats?type=all'
    
    tflines = teamFile.readlines()
    teamurls = [x.strip('\n').split(',')[1] for x in tflines]
    teams = [x.strip('\n').split(',')[0] for x in tflines]
    for url, name in zip(teamurls,teams):
        for season in seasons:
            full_url = url + '/players?season=' + season
            soup = get_page(full_url)
            tables = soup.findAll("table")
            if len(tables) > 6:
                characteristics = tables[6]
                #gamestats = tables[7]
                #fgstats = tables[8]
                #totalstats = tables[9]
                #assiststats = tables[10]
                #foulstats = tables[11]
                trs = characteristics.findAll("tr")
                valueStr = ""
                for tr in trs:
                    tds = tr.findAll("td")

                    # this are the values
                    if len(tds):
                        height = str(tds[2].text).split("-")
                        if len(height) == 1 and height[0] != '':
                            height = str(int(height[0])*12)
                        elif height[0] != '':
                            height = str(int(height[0])*12 + int(height[1]))
                        else:
                            height = ''
                        valueStr += name + "," + str(tds[1].text) + "," + height + "," + str(tds[3].text) + "," + str(tds[4].text) + "\n"

                if valueStr != "":
                    valueStr = valueStr[:-1]
                    filename = season + '_players' + '.csv'
                    statFile = open(filename, 'a')
                    statFile.write(valueStr + "\n")
                    statFile.close()

    teamFile.close()
 
def prepopulate_headers():
     (years, seasons) = make_seasons_array()
     for season in seasons:
        filename = season + '_players' + '.csv'
        statFile = open(filename, 'a')
        statFile.write("Team,Player,Height,Weight,Age\n")
        statFile.close()

def main():
    # get_teams()
    prepopulate_headers()
    get_stats()
    # get_games()

main()