import requests
from bs4 import BeautifulSoup

url = "http://www.teamrankings.com/ajax/league/v3/player-stats_controller.php"
dat = {'league': 'ncb', 'stat_id' : '4026', 'split': '', 'rate': 'per-game'}

seasons = [('304','2006-2007'),('305','2007-2008'),('306','2008-2009'),('307','2009-2010'),('308','2010-2011'),('309','2011-2012'),('310','2012-2013'),('311','2013-2014')]

for code, season in seasons:
    d = dat.copy()
    d['season_id'] = code
    r = requests.post(url, data=d)
    soup = BeautifulSoup(r.text)
    rows = soup.findAll('tr')
    valueStr = "Rank,Player,Team,Pos,Efficiency\n"
    for row in rows:
        tds = row.findAll('td')
        if len(tds):
	        valueStr += str(tds[0].text.strip()) + "," + str(tds[1].text.strip()) + "," + str(tds[2].text.strip()) + "," + str(tds[3].text.strip()) + "," + str(tds[4].text.strip()) + "\n"

    filename = season + '_nbaefficiency' + '.csv'
    statFile = open(filename, 'w')
    statFile.write(valueStr)
    statFile.close()