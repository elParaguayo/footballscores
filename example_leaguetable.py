from footballscores import LeagueTable

l = LeagueTable()
leagues = l.getLeagues()
myleague = [league for league in leagues 
                   if league["name"] == "Premier League"][0]

print myleague["name"]

for pos, team in enumerate(l.getLeagueTable(myleague["id"])):
	print "{0:02} - {1:20} - {2:02}".format(pos + 1, 
		                                    team["team"], 
		                                    team["points"])