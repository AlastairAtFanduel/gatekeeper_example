# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Fake Stuff IGNORE

# In this example the managers are instantiated inside the handlers and passed the clients
# This is just to make the implementation simple for now.
# Implementation could be split out much more.


def FakeManager(object):
    def __init__(self, clients):
        self._clients = clients()

    def get_contests(self):
        contests = self._clients.sport_data.java_call_1("aaa")
        fixture_lists = self._clients.game_data.java_call_2("bbb")
        return contests, fixture_lists

    def get_contest(self):
        contest = self._clients.sport_data.java_call_2("aaa")
        return contest

    def call_unexpected_thing(self):
        y = self._clients.game_data.java_call_1("bbb")
        return y


def ContestsHandler(request, path_params, query_params, clients):
    contests_manager = FakeManager(clients)

    contests, fixture_lists = contests_manager.get_contests()

    data = {
        'contests': contests,
        'fixture_lists': fixture_lists,
    }
    return data


def ContestHandler(request, path_params, query_params, clients):
    contest_manager = FakeManager(clients)

    fixture_list_id = path_params.fixture_list_id
    contest_id = path_params.contest_id
    foo = query_params.foo
    print("ContestHandler", fixture_list_id, contest_id, foo)

    contest = contest_manager.get_contest()

    # contest_manager.call_unexpected_thing

    data = {
        'contest': contest,
    }
    return data


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
