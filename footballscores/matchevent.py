class MatchEvent(object):

    TYPE_GOAL = "GOAL"
    TYPE_RED_CARD = "RED"
    TYPE_STATUS = "STATUS"

    def __init__(self, event_type, match, home=None):
        self.eventType = event_type
        self.home = home
        self.match = match

    def is_red(self):
        return self.eventType == self.TYPE_RED_CARD

    def is_goal(self):
        return self.eventType == self.TYPE_GOAL
