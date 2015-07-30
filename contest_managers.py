
class FakeManager(object):
    def __init__(self, clients):
        self._clients = clients()

    def get_contests(self):
        contests = self._clients.sport_data.java_call_1("aaa")
        fixture_lists = self._clients.game_data.java_call_2("bbb")
        return contests, fixture_lists

    def get_contest(self):
        print("CALLED get_contest")
        contest = self._clients.sport_data.java_call_2("aaa")
        return contest

    def call_unexpected_thing(self):
        y = self._clients.game_data.java_call_1("bbb")
        return y
