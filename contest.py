# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Fake Stuff IGNORE

# In this example the managers are instantiated inside the handlers and passed the clients
# This is just to make the implementation simple for now.
# Implementation could be split out much more.

from contest_managers import FakeManager


def foo_handler(request, path_params):
    return 'defaultvalue'


def ContestsHandler(request, path_params, query_params, clients, documenter):
    """
    The contests collection resource provides lists of contests filtered by
    various parameters.  If no fixture_list is specfied then only pinned contests
    over all upcoming fixture_lists will be provided (in this case
    fixture_lists will be be an empty list).

    **Example request**:

    .. sourcecode:: http

        GET /contests?fixture_list=8010
        Host: api.fanduel.com
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json
    """

    contests_manager = FakeManager(clients)

    print("ContestsHandler: FIRST CALL get_contests")
    contests, fixture_lists = contests_manager.get_contests()

    data = {
        'contests': contests,
        'fixture_lists': fixture_lists,
    }
    document = documenter(data)
    return document


def ContestHandler(request, path_params, query_params, clients, documenter):
    contest_manager = FakeManager(clients)

    fixture_list_id = path_params.fixture_list_id
    contest_id = path_params.contest_id
    choice = query_params.foo
    print("ContestHandler: ", fixture_list_id, contest_id, choice)

    if choice:
        print("ContestHandler: FIRST CALL get_contest")
        contest = contest_manager.get_contest()
        print("ContestHandler: SECOND CALL get_contest")
        contest = contest_manager.get_contest()    # To show lru caching
        print("ContestHandler: THIRD CALL call_unexpected_thing")
        contest_manager.call_unexpected_thing()
    else:
        contest = contest_manager.get_contests()

    data = {
        'contest': contest,
    }

    document = documenter(data)
    return document
