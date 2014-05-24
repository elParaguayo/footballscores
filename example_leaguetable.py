from footballscores import LeagueTable

l = LeagueTable()
leagues = l.getLeagues()
myleague = [league for league in leagues 
                   if league["name"] == "Premier League"][0]

print myleague["name"]

for team in l.getLeagueTable(myleague["id"]):
	print "{0:02} - {1:20} - {2:02}".format(team.position, 
		                                team.name, 
		                                team.points)
