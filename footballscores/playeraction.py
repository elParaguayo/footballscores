ACTION_GOAL = "goal"
ACTION_RED_CARD = "red-card"

actions = {ACTION_GOAL: "GOAL",
           ACTION_RED_CARD: "RED CARD"}


class PlayerAction(object):

    def __init__(self, player, action):
        self._fullname = player["name"]["full"]
        self._abbreviatedname = player["name"]["abbreviation"]
        self._firstname = player["name"]["first"]
        self._lastname = player["name"]["last"]

        self._actiontype = action["type"]
        self._actiondisplaytime = action["displayTime"]
        self._actionowngoal = action["ownGoal"]
        self._actionpenalty = action["penalty"]
        self._actiontime = action["timeElapsed"]
        self._actionaddedtime = action["addedTime"]

    def __lt__(self, other):
        normal = self._actiontime < other._actiontime
        added = (self._actiontime == other._actiontime) and (self._actionaddedtime < other._actionaddedtime)
        return normal or added

    def __eq__(self, other):
        normal = self._actiontime == other._actiontime
        added = self._actionaddedtime == other._actionaddedtime
        return normal and added

    def __repr__(self):
        return "<{}: {} ({})>".format(actions[self._actiontype],
                                      self._abbreviatedname.encode("ascii", "replace"),
                                      self._actiondisplaytime)

    @property
    def FullName(self):
        return self._fullname

    @property
    def FirstName(self):
        return self._firstname

    @property
    def LastName(self):
        return self._lastname

    @property
    def AbbeviatedName(self):
        return self._abbreviatedname

    @property
    def ActionType(self):
        return self._actiontype

    @property
    def DisplayTime(self):
        return self._actiondisplaytime

    @property
    def ElapsedTime(self):
        return self._actiontime

    @property
    def AddedTime(self):
        return self._actionaddedtime

    @property
    def isGoal(self):
        return self._actiontype == ACTION_GOAL

    @property
    def isRedCard(self):
        return self._actiontype == ACTION_RED_CARD   

    @property
    def isPenalty(self):
        return self._actionpenalty

    @property
    def isOwnGoal(self):
        return self._actionowngoal
