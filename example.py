from footballscores import Match
from time import sleep

match = Match("Everton", detailed=True)

print match.PrintDetail

while match.MatchFound and not match.Status == "FT":
	sleep(60)
	match.Update()
	if match.Goal or match.StatusChange:
		print match.PrintDetail