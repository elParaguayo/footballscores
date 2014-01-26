from footballscores import FootballMatch
from time import sleep

match = FootballMatch("Chelsea", detailed=True)

print match.PrintDetail

while match.MatchFound and not match.Status == "FT":
	sleep(60)
	match.Update()
	if match.Goal or match.StatusChange:
		print match.PrintDetail