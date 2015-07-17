"""
EXPERIMENTAL ROUTES WITH GATEKEEPER

What is a gatekeeper?

It is a handler wrapper that provides:

    inspection:
        For each handler can import and see:
            path_parameters it can take
            query_paramaters it can take
            docstring
            client_methods that are allowed to be used
            status codes that can be returned
        (Mostly for doc generation)

    enforcement:
        Can detect disallow/log/do_nothing for unexpected client calls, return values etc.
            E.G. In development never allow an unexpected client call.
                 In production log if one takes place.

    call graphs:
        Can inspect and see possible call graphs.
        Can use the post_handler_hook to generate actual call graphs for different inputs.

    lru_caching:
        For the duration of a request any external client method
            that is called twice will only be called once and the result reused.

    debug mode support:
        For each request capture:
             the external client methods called, args return values etc.
             the request
             the exception traceback.
        .last_call also stores this information for the last call.
            So any pdb can access the external/c3pyo call log for the current request.

"""

from contest import ContestsHandler, ContestHandler
from gate_keeper import GateKeeper, PathHandler, QueryHandler

from clients import clients


class Route(object):
    # Bypassing some of werkzeug for this demo.
    pass

# ROUTES

routes = []

# GET CONTESTS
get_contests_handler = GateKeeper(
    name="GET_contests",
    handler=ContestsHandler,
    clients=clients,
    allowed_client_methods=[
        clients.sport_data.java_call_1,
        clients.game_data.java_call_2
    ],
    allowed_status_codes=('422', '402', '201')
)

routes.append(
    Route(
        '/contests',
        name='contests',
        endpoint=get_contests_handler
    )
)

# GET CONTEST
get_contest_handler = GateKeeper(
    name="GET_contest",
    handler=ContestHandler,
    clients=clients,
    path_handler=PathHandler('fixture_list_id', 'contest_id'),
    query_handler=QueryHandler({'foo': 'defaultvalue'}),
    allowed_client_methods=[
        clients.sport_data.java_call_2
    ],
    allowed_status_codes=('422', '402', '201')
)

routes.append(
    Route(
        '/contests/<numeric_string:fixture_list_id>-<numeric_string:contest_id>',
        name='contest',
        endpoint=get_contest_handler
    )
)

# ToDo:

# ToDo GateKeeper could return a route.  Some duplication. path params etc.
# GateKeeper could do with a bit of seperation.
# allowed_status_codes maybe make more powerfollow check sub error codes etc.
# Check responses instead of just status codes
# Python2 doesnas have a full qual name for allowed_client_methods, name magic