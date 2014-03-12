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

def get_teams():
    
    alphabet = list(string.ascii_uppercase)
    baseUrl = "http://statsheet.com/mcb/teams/browse/name?t="

    for letter in alphabet:
        url = baseUrl + letter
        soup = get_page(url)

        for table in soup.findAll("tbody"):
            for tr in table.findAll("tr"):
                tds = tr.findAll("td")
                if len(tds):
                    outputFile = open('textfiles/teams_statsheet.txt', 'a')
                    line = str(tds[1].text) + "," + str(tds[1].a['href']) + "," + str(tds[2].text)
                    outputFile.write(line + "\n")
                    outputFile.close()

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
            full_url = url + '/team_stats?season=' + season + '&type=all'
            soup = get_page(full_url)
            for table in soup.findAll("table", { "class" : "table-stats" }):
                valueStr = ""
                opponentsVals = ""
                for tr in table.findAll("tr"):
                    tds = tr.findAll("td")

                    # this are the values
                    if len(tds):
                        valueStr += str(tds[1].text) + ","
                        opponentsVals += str(tds[4].text) + ','

                if valueStr != "":
                    valueStr = valueStr[:-1]
                    filename = season + '_teamstats' + '.csv'
                    statFile = open(filename, 'a')
                    statFile.write(name + "," + valueStr + "\n")
                    statFile.close()
                    opFilename = season + '_opponentstats' + '.csv'
                    opponentsVals = opponentsVals[:-1]
                    opFile = open(opFilename, 'a')
                    opFile.write(name + ',' + opponentsVals + "\n")
                    opFile.close()

    teamFile.close()
                

def main():
    # get_teams()
    get_stats()
    # get_games()

main()