import string
from BeautifulSoup import BeautifulSoup
import re
from datetime import datetime, time
import json
from time import sleep


from .base import matchcommon
from .matchdict import MatchDict
from .matchdict import MatchDictKeys as MDKey

import morphlinks as ML

import web_pdb

class FootballMatch(matchcommon):
    '''Class for getting details of individual football matches.
    Data is pulled from BBC live scores page.
    '''
    # self.accordionlink = "http://polling.bbc.co.uk/sport/shared/football/accordion/partial/collated"
    scoreslink = "/data/bbc-morph-football-scores-match-list-data/endDate/{end_date}/startDate/{start_date}/{source}/version/2.2.3/withPlayerActions/{detailed}"


    detailprefix =   ("http://www.bbc.co.uk/sport/football/live/"
                      "partial/{id}")

    match_format = {"%H": "HomeTeam",
                    "%A": "AwayTeam",
                    "%h": "HomeScore",
                    "%a": "AwayScore"}

    def __init__(self, team, detailed = False, data = None):
        '''Creates an instance of the Match object.
        Must be created by passing the name of one team.

        data - User can also send data to the class e.g. if multiple instances
        of class are being run thereby saving http requests. Otherwise class
        can handle request on its own.

        detailed - Do we want additional data (e.g. goal scorers, bookings)?
        '''
        super(FootballMatch, self).__init__()
        self.detailed = detailed
        self.myteam = team
        self.match = None

        self.hasTeamPage = self._findTeamPage()

        if not self.hasTeamPage:
            self._scanLeagues()

        if self.hasTeamPage:
            self.update()


        # # Set the relevant urls
        # self.detailedmatchpage = None
        # self.scorelink = None
        #
        # # Boolean to notify user if there is a valid match
        # self.matchfound = False
        #
        # # Which team am I following?
        # self.myteam = team
        #
        # self.__resetMatch()
        #
        # # Let's try and load some data
        # data = self.__loadData(data)
        #
        # # If our team is found or we have data
        # if data:
        #
        #     # Update the class properties
        #     self.__update(data)
        #     # No notifications for now
        #     self.goal = False
        #     self.statuschange = False
        #     self.newmatch = False

    def _scanLeagues(self):

        return self.getScoresFixtures(source=ML.MORPH_FIXTURES_ALL,
                                      detailed=False)

    def _findTeamPage(self):
        teams = self.getTeams()

        if teams:
            myteam = [x for x in teams if self.myteam.lower() in x["name"].lower()]
            if myteam:
                tm = myteam[0]["url"]
                try:
                    self.myteampage = "team/{}".format(tm.split("/")[4])
                    return True
                except:
                    self.myteampage = None
                    return False

        return False

    def _getScoresFixtures(self, start_date=None, end_date=None,
                          source=None, detailed=None):
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")

        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        if source is None and self.hasTeamPage:
            source = self.myteampage

        if detailed is None:
            detailed = self.detailed

        pl = self.scoreslink.format(start_date=start_date,
                                    end_date=end_date,
                                    source=source,
                                    detailed=str(detailed).lower())

        return self.sendRequest(pl)


    def __findMatch(self, payload):
        match = payload["matchData"][0]["tournamentDatesWithEvents"].values()[0][0]["events"][0]
        return match

    def _setCallbacks(self):
        self.match.add_callback(MDKey.HOME_TEAM, self._checkHomeTeamEvent)
        self.match.add_callback(MDKey.AWAY_TEAM, self._checkAwayTeamEvent)
        self.match.add_callback(MDKey.EVENT_STATUS, self._checkStatus)

    def _checkHomeTeamEvent(self, event):
        self._checkTeamEvent(event, home=True)

    def _checkAwayTeamEvent(self, event):
        self._checkTeamEvent(event, home=False)

    def _checkTeamEvent(self, event, home=True):
        pass

    def _checkStatus(self, status):
        pass

    def formatMatch(self, fmt):

        for key in self.match_format:
            try:
                fmt = fmt.replace(key, getattr(self, self.match_format[key]))
            except TypeError:
                fmt = fmt.replace(key, str(getattr(self, self.match_format[key])))

        return fmt

    def update(self):

        data = self._getScoresFixtures()

        if data:

            match = json.loads(data[0]["payload"])
            match = self.__findMatch(match)

            if self.match is None:
                self.match = MatchDict(match)
                self._setCallbacks()
                self._old = self.match

            else:
                self.match.update(match)
                self._old = self.match

            return True

        return False

    # def __getUKTime(self):
    #     #api.geonames.org/timezoneJSON?formatted=true&lat=51.51&lng=0.13&username=demo&style=full
    #     rawbbctime = self.getPage("http://api.geonames.org/timezoneJSON"
    #                            "?formatted=true&lat=51.51&lng=0.13&"
    #                            "username=elParaguayo&style=full")
    #
    #     bbctime = json.loads(rawbbctime).get("time") if rawbbctime else None
    #
    #     if bbctime:
    #         servertime = datetime.strptime(bbctime,
    #                                        "%Y-%m-%d %H:%M")
    #         return servertime
    #
    #     else:
    #
    #         return None
    #
    # def __resetMatch(self):
    #     '''Clear all variables'''
    #     self.hometeam = None
    #     self.awayteam = None
    #     self.homescore = None
    #     self.awayscore = None
    #     self.scorelink = None
    #     self.homescorers = None
    #     self.awayscorers = None
    #     self.homeyellowcards = []
    #     self.awayyellowcards = []
    #     self.homeredcards = []
    #     self.awayredcards = []
    #     self.competition = None
    #     self.matchtime = None
    #     self.status = None
    #     self.goal = False
    #     self.statuschange = False
    #     self.newmatch = False
    #     self.homebadge = None
    #     self.awaybadge = None
    #     self.matchid = None
    #     self.matchlink = None
    #     self.rawincidents = []
    #     self.booking = False
    #     self.redcard = False
    #     self.leagueid = None
    #
    #
    # def __findMatch(self):
    #     leaguepage = self.getPage(self.livescoreslink.format(comp=""))
    #     data = None
    #     teamfound = False
    #
    #     if leaguepage:
    #
    #         # Start with the default page so we can get list of active leagues
    #         raw =  BeautifulSoup(leaguepage)
    #
    #         # Find the list of active leagues
    #         selection = raw.find("div", {"class":
    #                                      "drop-down-filter live-scores-fixtures"})
    #
    #
    #         # Loop throught the active leagues
    #         for option in selection.findAll("option"):
    #
    #             # Build the link for that competition
    #             league = option.get("value")[12:]
    #
    #             if league:
    #                 scorelink = self.livescoreslink.format(comp=league)
    #
    #                 scorepage = self.getPage(scorelink)
    #
    #                 if scorepage:
    #                     # Prepare to process page
    #                     optionhtml = BeautifulSoup(scorepage)
    #
    #                     # We just want the live games...
    #                     live = optionhtml.find("div", {"id": "matches-wrapper"})
    #
    #                     # Let's look for our team
    #                     if live.find(text=self.myteam):
    #                         teamfound = True
    #                         self.scorelink = scorelink
    #                         self.competition = option.text.split("(")[0].strip()
    #                         self.leagueid = league
    #                         data = live
    #                         break
    #
    #     self.matchfound = teamfound
    #
    #     return data
    #
    # def __getScores(self, data, update = False):
    #
    #     for match in data.findAll("tr", {"id": re.compile(r'^match-row')}):
    #         if match.find(text=self.myteam):
    #
    #             self.hometeam = match.find("span", {"class": "team-home"}).text ## ENCODE
    #
    #             self.awayteam = match.find("span", {"class": "team-away"}).text
    #
    #             linkrow = match.find("td", {"class": "match-link"})
    #             try:
    #                 link = linkrow.find("a").get("href")
    #                 self.matchlink = "http://www.bbc.co.uk%s" % (link)
    #             except AttributeError:
    #                 self.matchlink = None
    #
    #             if match.get("class") == "fixture":
    #                 status = "Fixture"
    #                 matchtime = match.find("span",
    #                                  {"class":
    #                                  "elapsed-time"}).text.strip()[:5]
    #
    #             elif match.get("class") == "report":
    #                 status = "FT"
    #                 matchtime = None
    #
    #             elif ("%s" %
    #                  (match.find("span",
    #                  {"class": "elapsed-time"}).text.strip()) == "Half Time"):
    #                 status = "HT"
    #                 matchtime = None
    #
    #             else:
    #                 status = "L"
    #                 matchtime = match.find("span",
    #                                  {"class": "elapsed-time"}).text.strip()
    #
    #             matchid = match.get("id")[10:]
    #
    #             score = match.find("span",
    #                              {"class": "score"}).text.strip().split(" - ")
    #
    #             try:
    #                 homescore = int(score[0].strip())
    #                 awayscore = int(score[1].strip())
    #
    #             except:
    #                 homescore = 0
    #                 awayscore = 0
    #
    #             self.statuschange = False
    #             self.newmatch = False
    #             self.goal=False
    #
    #             if update:
    #
    #                 if not status == self.status:
    #                     self.statuschange = True
    #
    #                 if not matchid == self.matchid:
    #                     self.newmatch = True
    #
    #                 if not (homescore == self.homescore and
    #                         awayscore == self.awayscore):
    #                     # Gooooooooooooaaaaaaaaaaaaaaaaallllllllllllllllll!
    #                     self.goal = True
    #
    #             self.status = status if status else None ## ENCODE
    #             self.matchtime = matchtime if matchtime else None ## ENCODE
    #             self.matchid = matchid if matchid else None ## ENCODE
    #             self.homescore = homescore
    #             self.awayscore = awayscore
    #
    #
    # def __update(self, data = None):
    #
    #     self.__getScores(data)
    #
    #     if self.detailed:
    #         self.__getDetails()
    #
    # def __loadData(self, data = None):
    #
    #     self.matchfound = False
    #
    #     if data:
    #         if data.find(text=self.myteam):
    #             self.matchfound = True
    #         else:
    #             data = None
    #
    #     if not data and self.scorelink:
    #         scorepage = self.getPage(self.scorelink)
    #         if scorepage:
    #             scorehtml = BeautifulSoup(scorepage)
    #             data = scorehtml.find("div", {"id": "matches-wrapper"})
    #             if data.find(text=self.myteam):
    #                 self.matchfound = True
    #             else:
    #                 data = None
    #         else:
    #             data = None
    #
    #     if not data:
    #         data = self.__findMatch()
    #
    #     if not data:
    #         self.__resetMatch()
    #
    #     return data
    #
    # def Update(self, data = None):
    #
    #     data = self.__loadData(data)
    #
    #     if data:
    #         self.__getScores(data, update = True)
    #
    #     if self.detailed:
    #         self.__getDetails()
    #
    # def __getDetails(self):
    #
    #     if self.matchid:
    #         # Prepare bautiful soup to scrape match page
    #
    #
    #             # Let's get the home and away team detail sections
    #         try:
    #             bs =  BeautifulSoup(self.getPage(self.detailprefix.format(
    #                                          id=self.matchid)))
    #             incidents = bs.find("table",
    #                                {"class": "incidents-table"}).findAll("tr")
    #         except:
    #             incidents = None
    #
    #         # Get incidents
    #         # This populates variables with details of scorers and bookings
    #         # Incidents are stored in a list of tuples: format is:
    #         # [(Player Name, [times of incidents])]
    #         hsc = []
    #         asc = []
    #         hyc = []
    #         ayc = []
    #         hrc = []
    #         arc = []
    #
    #         if incidents:
    #
    #             self.__goalscorers = []
    #             self.__yellowcards = []
    #             self.__redcards = []
    #
    #             for incident in incidents:
    #                 i = incident.find("td",
    #                                  {"class":
    #                                  re.compile(r"\bincident-type \b")})
    #                 if i:
    #                     h = incident.find("td",
    #                                      {"class":
    #                                      "incident-player-home"}).text.strip()
    #
    #                     a = incident.find("td",
    #                                      {"class":
    #                                      "incident-player-away"}).text.strip()
    #
    #                     t = incident.find("td",
    #                                      {"class":
    #                                      "incident-time"}).text.strip()
    #
    #                     if "goal" in i.get("class"):
    #                         if h:
    #                             hsc = self.__addIncident(hsc, h, t) ## ENCODE
    #                             self.__goalscorers.append((self.hometeam, h, t))
    #                             self.__addRawIncident("home", "goal", h, t)
    #                         else:
    #                             asc = self.__addIncident(asc, a, t)
    #                             self.__goalscorers.append((self.awayteam, a, t))
    #                             self.__addRawIncident("away", "goal", a, t)
    #
    #                     elif "yellow-card" in i.get("class"):
    #                         if h:
    #                             hyc = self.__addIncident(hyc, h, t)
    #                             self.__yellowcards.append((self.hometeam, h, t))
    #                             self.__addRawIncident("home", "yellow", h, t)
    #                         else:
    #                             ayc = self.__addIncident(ayc, a, t)
    #                             self.__yellowcards.append((self.awayteam, a, t))
    #                             self.__addRawIncident("away", "yellow", a, t)
    #
    #                     elif "red-card" in i.get("class"):
    #                         if h:
    #                             hrc = self.__addIncident(hrc, h, t)
    #                             self.__redcards.append((self.hometeam, h, t))
    #                             self.__addRawIncident("home", "red", h, t)
    #                         else:
    #                             arc = self.__addIncident(arc, a, t)
    #                             self.__redcards.append((self.awayteam, a, t))
    #                             self.__addRawIncident("away", "red", a, t)
    #
    #         self.booking = not (self.homeyellowcards == hyc and
    #                             self.awayyellowcards == ayc)
    #
    #         self.redcard = not (self.homeredcards == hrc and
    #                            self.awayredcards == arc)
    #
    #         self.homescorers = hsc
    #         self.awayscorers = asc
    #         self.homeyellowcards = hyc
    #         self.awayyellowcards = ayc
    #         self.homeredcards = hrc
    #         self.awayredcards = arc
    #
    # def __addIncident(self, incidentlist, player, incidenttime):
    #     '''method to add incident to list variable'''
    #     found = False
    #     for incident in incidentlist:
    #         if incident[0] == player:
    #             incident[1].append(incidenttime)
    #             found = True
    #             break
    #
    #     if not found:
    #         incidentlist.append((player, [incidenttime]))
    #
    #     return incidentlist
    #
    # def __addRawIncident(self, team, incidenttype, player, incidenttime):
    #
    #     incident = (team, incidenttype, player, incidenttime)
    #
    #     if not incident in self.rawincidents:
    #         self.rawincidents.append(incident)
    #
    # def formatIncidents(self, incidentlist, newline = False):
    #     '''Incidents are in the following format:
    #     List:
    #       [Tuple:
    #         (Player name, [list of times of incidents])]
    #
    #     This function converts the list into a string.
    #     '''
    #     temp = []
    #     incidentjoin = "\n" if newline else ", "
    #
    #     for incident in incidentlist:
    #         temp.append("%s (%s)" % (incident[0],
    #                                  ", ".join(incident[1])))
    #
    #     return incidentjoin.join(temp)
    #
    # def getTeamBadges(self):
    #     found = False
    #
    #     if self.matchlink:
    #         badgepage = self.getPage(self.matchlink)
    #         if badgepage:
    #             linkpage = BeautifulSoup(badgepage)
    #             badges = linkpage.findAll("div", {"class": "team-badge"})
    #             if badges:
    #                 self.homebadge = badges[0].find("img").get("src")
    #                 self.awaybadge = badges[1].find("img").get("src")
    #                 found = True
    #
    #     return found
    #
    #
    # def __nonzero__(self):
    #
    #     return self.matchfound
    #
    # def __repr__(self):
    #
    #     return "FootballMatch(\'%s\', detailed=%s)" % (self.myteam,
    #                                                       self.detailed)
    #
    # def __eq__(self, other):
    #     if isinstance(other, self.__class__):
    #         if not self.matchid is None:
    #             return self.matchid == other.matchid
    #         else:
    #             return self.myteam == other.myteam
    #     else:
    #         return False
    #
    # # Neater functions to return data:
    #

    @property
    def on_goal(self):

        if self._on_goal:
            self._on_goal(self)

    @on_goal.setter
    def on_goal(self, func):

        if callable(func):
            self.on_goal = func

    @property
    def on_red(self):

        if self._on_red:
            self._on_red(self)

    @on_red.setter
    def on_red(self, func):

        if callable(func):
            self._on_red = func

    @property
    def on_status_change(self):

        if self._on_status_change:
            self._on_status_change(self)

    @on_status_change.setter
    def on_status_change(self, func):

        if callable(func):
            self._on_status_change = func

    @property
    def HomeTeam(self):
        """Returns string of the home team's name

        """
        return self.match.homeTeam.name.full

    @property
    def AwayTeam(self):
        """Returns string of the away team's name

        """
        return self.match.awayTeam.name.full

    @property
    def HomeScore(self):
        """Returns the number of goals scored by the home team

        """
        return self.match.homeTeam.scores.score

    @property
    def AwayScore(self):
        """Returns the number of goals scored by the away team

        """
        return self.match.awayTeam.scores.score
    #
    # @property
    # def Competition(self):
    #     """Returns the name of the competition to which the match belongs
    #
    #     e.g. "Premier League", "FA Cup" etc
    #
    #     """
    #     return self.competition
    #
    @property
    def Status(self):
        """Returns the status of the match

        e.g. "L", "HT", "FT"

        """
        return self.match.eventProgress.status
    #
    # @property
    # def Goal(self):
    #     """Boolean. Returns True if score has changed since last update
    #
    #     """
    #     return self.goal
    #
    # @property
    # def StatusChanged(self):
    #     """Boolean. Returns True if status has changed since last update
    #
    #     e.g. Match started, half-time started etc
    #
    #     """
    #     return self.statuschange
    #
    # @property
    # def NewMatch(self):
    #     """Boolean. Returns True if the match found since last update
    #
    #     """
    #     return self.newmatch
    #
    # @property
    # def MatchFound(self):
    #     """Boolean. Returns True if a match is found in JSON feed
    #
    #     """
    #     return self.matchfound
    #
    # @property
    # def HomeBadge(self):
    #     """Returns link to image for home team's badge
    #
    #     """
    #     return self.homebadge
    #
    # @property
    # def AwayBadge(self):
    #     """Returns link to image for away team's badge
    #
    #     """
    #     return self.awaybadge
    #
    # @property
    # def HomeScorers(self):
    #     """Returns list of goalscorers for home team
    #
    #     """
    #     return self.homescorers
    #
    # @property
    # def AwayScorers(self):
    #     """Returns list of goalscorers for away team
    #
    #     """
    #     return self.awayscorers
    #
    # @property
    # def HomeYellowCards(self):
    #     """Returns list of players receiving yellow cards for home team
    #
    #     """
    #     return self.homeyellowcards
    #
    # @property
    # def AwayYellowCards(self):
    #     """Returns list of players receiving yellow cards for away team
    #
    #     """
    #     return self.awayyellowcards
    #
    # @property
    # def HomeRedCards(self):
    #     """Returns list of players sent off for home team
    #
    #     """
    #     return self.homeredcards
    #
    # @property
    # def AwayRedCards(self):
    #     """Returns list of players sent off for away team
    #
    #     """
    #     return self.awayredcards
    #
    # @property
    # def LastGoalScorer(self):
    #     if self.detailed:
    #         if self.__goalscorers:
    #             return self.__goalscorers[-1]
    #         else:
    #             return None
    #     else:
    #         return None
    #
    # @property
    # def LastYellowCard(self):
    #     if self.detailed:
    #         if self.__yellowcards:
    #             return self.__yellowcards[-1]
    #         else:
    #             return None
    #     else:
    #         return None
    #
    # @property
    # def LastRedCard(self):
    #     if self.detailed:
    #         if self.__redcards:
    #             return self.__redcards[-1]
    #         else:
    #             return None
    #     else:
    #         return None
    #
    # @property
    # def MatchDate(self):
    #     """Returns date of match i.e. today's date
    #
    #     """
    #     d = datetime.now()
    #     datestring = "%s %d %s" % (
    #                                     d.strftime("%A"),
    #                                     d.day,
    #                                     d.strftime("%B %Y")
    #                                   )
    #     return datestring
    #
    # @property
    # def MatchTime(self):
    #     """If detailed info available, returns match time in minutes.
    #
    #     If not, returns Status.
    #
    #     """
    #     if self.status=="L" and self.matchtime is not None:
    #         return self.matchtime
    #     else:
    #         return self.Status
    #
    # def abbreviate(self, cut):
    #     """Returns short formatted summary of match but team names are
    #     truncated according to the cut parameter.
    #
    #     e.g. abbreviate(3):
    #       "Ars 1-1 Che (L)"
    #
    #     Should handle accented characters.
    #
    #     """
    #     return u"%s %s-%s %s (%s)" % (
    #                                   self.hometeam[:cut],
    #                                   self.homescore,
    #                                   self.awayscore,
    #                                   self.awayteam[:cut],
    #                                   self.Status
    #                                   )
    #
    def __unicode__(self):
        """Returns short formatted summary of match.

        e.g. "Arsenal 1-1 Chelsea (L)"

        Should handle accented characters.

        """
        if self.match:

            return u"%s %s-%s %s (%s)" % (
                                          self.HomeTeam,
                                          self.HomeScore,
                                          self.AwayScore,
                                          self.AwayTeam,
                                          self.Status
                                          )

        else:

            return u"%s are not playing today." % (self.myteam)

    def __str__(self):
        """Returns short formatted summary of match.

        e.g. "Arsenal 1-1 Chelsea (L)"

        """
        return unicode(self).encode('utf-8')
    #
    # @property
    # def PrintDetail(self):
    #     """Returns detailed summary of match (if available).
    #
    #     e.g. "(L) Arsenal 1-1 Chelsea (Arsenal: Wilshere 10',
    #           Chelsea: Lampard 48')"
    #     """
    #     if self.detailed:
    #         hscore = False
    #         scorerstring = ""
    #
    #         if self.homescorers or self.awayscorers:
    #             scorerstring = " ("
    #             if self.homescorers:
    #                 hscore = True
    #                 scorerstring += "%s: %s" % (self.hometeam,
    #                                             self.formatIncidents(self.homescorers))
    #
    #
    #             if self.awayscorers:
    #                 if hscore:
    #                     scorerstring += " - "
    #                 scorerstring += "%s: %s" % (self.awayteam,
    #                                             self.formatIncidents(self.awayscorers))
    #
    #             scorerstring += ")"
    #
    #         return "(%s) %s %s-%s %s%s" % (
    #                                         self.MatchTime,
    #                                         self.hometeam,
    #                                         self.homescore,
    #                                         self.awayscore,
    #                                         self.awayteam,
    #                                         scorerstring
    #                                         )
    #     else:
    #         return self.__str__()
    #
    # @property
    # def TimeToKickOff(self):
    #     '''Returns a timedelta object for the time until the match kicks off.
    #
    #     Returns None if unable to parse match time or if match in progress.
    #
    #     Should be unaffected by timezones as it gets current time from bbc
    #     server which *should* be the same timezone as matches shown.
    #     '''
    #     if self.status == "Fixture":
    #         try:
    #             koh = int(self.matchtime[:2])
    #             kom = int(self.matchtime[3:5])
    #             kickoff = datetime.combine(
    #                         datetime.now().date(),
    #                         time(koh, kom, 0))
    #             timetokickoff = kickoff - self.__getUKTime()
    #         except Exception, e:
    #             timetokickoff = None
    #         finally:
    #             pass
    #     else:
    #         timetokickoff = None
    #
    #     return timetokickoff
    #
    # @property
    # def matchdict(self):
    #     return {"hometeam": self.hometeam,
    #             "awayteam": self.awayteam,
    #             "status": self.status,
    #             "matchtime": self.MatchTime,
    #             "homescore": self.homescore,
    #             "awayscore": self.awayscore,
    #             "homescorers": self.homescorers,
    #             "awayscorers": self.awayscorers,
    #             "homeyellow": self.homeyellowcards,
    #             "awayyellow": self.awayyellowcards,
    #             "homered": self.homeredcards,
    #             "awayred": self.awayredcards,
    #             "incidentlist": self.rawincidents}
