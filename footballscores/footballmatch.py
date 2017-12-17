import string
from BeautifulSoup import BeautifulSoup
import re
from datetime import datetime, time
import json
from time import sleep


from .base import matchcommon
from .matchdict import MatchDict
from .matchdict import MatchDictKeys as MDKey
from .matchevent import MatchEvent
from .playeraction import PlayerAction

import morphlinks as ML

import web_pdb

class FootballMatch(matchcommon):
    '''Class for getting details of individual football matches.
    Data is pulled from BBC live scores page.
    '''
    scoreslink = ("/data/bbc-morph-football-scores-match-list-data/endDate/"
                  "{end_date}/startDate/{start_date}/{source}/version/2.2.3/"
                  "withPlayerActions/{detailed}")


    detailprefix =   ("http://www.bbc.co.uk/sport/football/live/"
                      "partial/{id}")

    match_format = {"%H": "HomeTeam",
                    "%A": "AwayTeam",
                    "%h": "HomeScore",
                    "%a": "AwayScore",
                    "%v": "Venue",
                    "%T": "DisplayTime",
                    "%S": "Status",
                    "%R": "HomeRedCards",
                    "%r": "AwayRedCards",
                    "%G": "HomeScorers",
                    "%g": "AwayScorers",
                    "%C": "Competition"}

    ACTION_GOAL = "goal"
    ACTION_RED_CARD = "red-card"

    def __init__(self, team, detailed = True, data = None):
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
        self.match = MatchDict()
        self._on_red = self._on_goal = self._on_status_change = None
        self._clearFlags()

        self.hasTeamPage = self._findTeamPage()

        if not self.hasTeamPage:
            self._scanLeagues()

        if self.hasTeamPage:
            self.update()

    def _no_match(default):
        """
        Decorator to provide default values for properties when there is no
        match found.

        e.g.:
            @property
            @_no_match(str())
            def HomeTeam(self):
                ...
        """
        def wrapper(func):

            def wrapped(self):

                if self.match:
                    return func(self)

                else:
                    return default

            return wrapped

        return wrapper


    def _override_none(value):
        """
        Decorator to provide default values for properties when there is no
        current value.

        For example, this decorator can be used to convert a None value for a
        match score (empty before the match starts) to 0.

        e.g.:
            @property
            @_no_match(int())
            @_override_none(0)
            def HomeScore(self):
                ...
        """
        def wrapper(func):

            def wrapped(self):

                if func(self) is None:
                    return value

                else:
                    return func(self)

            return wrapped

        return wrapper

    def _scanLeagues(self):

        return self._getScoresFixtures(source=ML.MORPH_FIXTURES_ALL,
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
        match = payload["matchData"]

        if match:
            return match[0]["tournamentDatesWithEvents"].values()[0][0]["events"][0]
        else:
            return None

    def _setCallbacks(self):
        self.match.add_callback(MDKey.HOME_TEAM, self._checkHomeTeamEvent)
        self.match.add_callback(MDKey.AWAY_TEAM, self._checkAwayTeamEvent)
        self.match.add_callback(MDKey.PROGRESS, self._checkStatus)

    def __getEvents(self, event, event_type):
        events = []

        player_actions = event.get("playerActions", list())

        for acts in player_actions:
            player = acts["name"]["abbreviation"]
            for act in acts["actions"]:
                if act["type"] == event_type:
                    pa = PlayerAction(acts, act)
                    events.append(pa)

        return sorted(events)

    def _lastEvent(self, event_type):
        events = self.__getEvents(self.match.homeTeam, event_type)
        events += self.__getEvents(self.match.awayTeam, event_type)
        # events = sorted(events, key=lambda x: (x[1], x[2]))
        events = sorted(events)

        if events:
            return events[-1]
        else:
            return []


    def _getReds(self, event):
        return self.__getEvents(event, self.ACTION_RED_CARD)

    def _getGoals(self, event):
        return self.__getEvents(event, self.ACTION_GOAL)


    def _checkGoal(self, old, new):
        return (old.scores.score != new.scores.score) and (new.scores.score > 0)

    def _checkRed(self, old, new):

        old_reds = self._getReds(old)
        new_reds = self._getReds(new)

        return old_reds != new_reds


    def _checkHomeTeamEvent(self, event):
        self._checkTeamEvent(event, home=True)

    def _checkAwayTeamEvent(self, event):
        self._checkTeamEvent(event, home=False)

    def _checkTeamEvent(self, event, home=True):

        if home:
            old = self._old.homeTeam
        else:
            old = self._old.awayTeam

        new = MatchDict(event)

        goal = self._checkGoal(old, new)
        red = self._checkRed(old, new)

        if goal:
            if home:
                self._homegoal = True
            else:
                self._awaygoal = True

        if red:
            if home:
                self._homered = True
            else:
                self._awayred = True


    def _checkStatus(self, status):
        self._statuschange = True

    def _clearFlags(self):
        self._homegoal = False
        self._awaygoal = False
        self._homered = False
        self._awayred = False
        self._statuschange = False

    def _fireEvent(self, func, payload):

        try:
            func(payload)
        except TypeError:
            pass

    def _fireEvents(self):

        if self._homegoal:
            func = self.on_goal
            payload = MatchEvent(MatchEvent.TYPE_GOAL, self, True)
            self._fireEvent(func, payload)

        if self._awaygoal:
            func = self.on_goal
            payload = MatchEvent(MatchEvent.TYPE_GOAL, self, False)
            self._fireEvent(func, payload)

        if self._homered:
            func = self.on_goal
            payload = MatchEvent(MatchEvent.TYPE_RED_CARD, self, True)
            self._fireEvent(func, payload)

        if self._awayred:
            func = self.on_goal
            payload = MatchEvent(MatchEvent.TYPE_RED_CARD, self, False)
            self._fireEvent(func, payload)

        if self._statuschange:
            func = self.on_status_change
            payload = MatchEvent(MatchEvent.TYPE_STATUS, self)
            self._fireEvent(func, payload)

    def _formatEvents(self, events, event_type=ACTION_GOAL):

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

            if match:

                if not self.match:
                    self.match = MatchDict(match, add_callbacks=True)
                    self._setCallbacks()
                    self._old = self.match

                else:
                    self._clearFlags()
                    self.match.update(match)
                    self._fireEvents()
                    self._old = self.match

            else:
                self._clearFlags()
                self._old = None
                self.match = None

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


    def __nonzero__(self):

        return bool(self.match)

    def __repr__(self):

        return "<FootballMatch(\'%s\')>" % (self.myteam)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.match.eventKey == other.match.eventKey
            if self.match and other.match:
                return self.match.eventKey == other.match.eventKey
            else:
                return self.myteam == other.myteam
        else:
            return False
    #
    # # Neater functions to return data:
    #

    @property
    def on_goal(self):

        if self._on_goal:
            return self._on_goal

    @on_goal.setter
    def on_goal(self, func):

        if callable(func):
            self._on_goal = func

    @property
    def on_red(self):

        if self._on_red:
            return self._on_red

    @on_red.setter
    def on_red(self, func):

        if callable(func):
            self._on_red = func

    @property
    def on_status_change(self):

        if self._on_status_change:
            return self._on_status_change

    @on_status_change.setter
    def on_status_change(self, func):

        if callable(func):
            self._on_status_change = func

    @property
    @_no_match(str())
    def HomeTeam(self):
        """Returns string of the home team's name

        """
        return self.match.homeTeam.name.full

    @property
    @_no_match(str())
    def AwayTeam(self):
        """Returns string of the away team's name

        """
        return self.match.awayTeam.name.full

    @property
    @_no_match(int())
    @_override_none(0)
    def HomeScore(self):
        """Returns the number of goals scored by the home team

        """
        return self.match.homeTeam.scores.score

    @property
    @_no_match(int())
    @_override_none(0)
    def AwayScore(self):
        """Returns the number of goals scored by the away team

        """
        return self.match.awayTeam.scores.score

    @property
    @_no_match(str())
    def Competition(self):
        """Returns the name of the competition to which the match belongs

        e.g. "Premier League", "FA Cup" etc

        """
        return self.match.tournamentName.full

    @property
    @_no_match(str())
    def Status(self):
        """Returns the status of the match

        e.g. "L", "HT", "FT"

        """
        return self.match.eventProgress.period

    @property
    @_no_match(str())
    def DisplayTime(self):
        me = self.match.minutesElapsed
        et = self.match.minutesIntoAddedTime

        miat = u"+{}".format(et) if et else ""

        if me:
            return u"{}{}".format(me, miat)
        else:
            return None

    @property
    @_no_match(int())
    def ElapsedTime(self):
        return self.match.minutesElapsed

    @property
    @_no_match(int())
    def AddedTime(self):
        return self.match.minutesIntoAddedTime

    @property
    @_no_match(str())
    def Venue(self):
        return self.match.venue.name.full

    @property
    @_no_match(False)
    def isFixture(self):
        return self.match.eventStatus == "pre-event"

    @property
    @_no_match(False)
    def isLive(self):
        return self.match.eventStatus == "mid-event"

    @property
    @_no_match(False)
    def isFinished(self):
        return self.match.eventStatus == "post-event"

    @property
    @_no_match(False)
    def isInAddedTime(self):
        return self.match.minutesIntoAddedTime > 0

    @property
    @_no_match(list())
    def HomeScorers(self):
        """Returns list of goalscorers for home team

        """
        return self._getGoals(self.match.homeTeam)

    @property
    @_no_match(list())
    def AwayScorers(self):
        """Returns list of goalscorers for away team

        """
        return self._getGoals(self.match.awayTeam)

    @property
    @_no_match(str())
    def LastGoal(self):
        return self._lastEvent(self.ACTION_GOAL)

    @property
    @_no_match(list())
    def HomeRedCards(self):
        """Returns list of players sent off for home team

        """
        return self._getReds(self.match.homeTeam)

    @property
    @_no_match(list())
    def AwayRedCards(self):
        """Returns list of players sent off for away team

        """
        return self._getReds(self.match.awayTeam)


    @property
    @_no_match(str())
    def LastRedCard(self):
        return self._lastEvent(self.ACTION_RED_CARD)
      return None


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
