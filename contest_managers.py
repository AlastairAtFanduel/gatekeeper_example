
class FakeManager(object):
    def __init__(self, clients):
        self._clients = clients

    def get_contests(self):
        print("FakeManager.get_contests: calling sport_data_java_call_1")
        contests = self._clients.sport_data.sport_data_java_call_1("aaa")

        print("FakeManager.get_contests: calling sport_data_java_call_1")
        contests = self._clients.sport_data.sport_data_java_call_1("aaa")

        print("FakeManager.get_contests: calling sport_data_java_call_2")
        self._clients.sport_data.sport_data_java_call_2("aaa")

        print("FakeManager.get_contests: calling game_data_java_call_2")
        fixture_lists = self._clients.game_data.game_data_java_call_2("bbb")

        return contests, fixture_lists

    def get_contest(self):
        print("FakeManager.get_contest: calling get_contest")
        contest = self._clients.sport_data.sport_data_java_call_2("aaa")
        return contest

    def call_unexpected_thing(self):
        y = self._clients.game_data.game_data_java_call_1("bbb")
        return y
