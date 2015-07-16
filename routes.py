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
from functools import partial

from contest import ContestsHandler, ContestHandler
from gate_keeper import GateKeeper, AllowedStatus, PathHandler, QueryHandler

from clients import clients


# ////////////////////////////////////////////////////////////////
# Toys and Fakery

class Route(object):
    # Bypassing werkzeug for this demo.
    pass


def enforcer(*args, **kwargs):
    """This really needs a defined interface"""
    print("Something unallowed happened")
    print("AAAAA", args, kwargs)
    raise AssertionError("Bad Coder!")


def my_call_logger(gatekeeper, request, response, exception, client_calls):
    # Print and PDB
    print("Logging the last call")
    print("Handler of name={} was called with".format(gatekeeper.name))
    print(request, response, exception)
    print("It used the following calls")
    for call_num, client_call, params, ret, error in client_calls:
        print(client_call.__name__, params, ret, error)
    import pdb; pdb.set_trace()


my_gatekeeper = partial(
    GateKeeper,
    lru_cache=True,
    disallowed_client_method=enforcer,
    post_handler_hook=my_call_logger
)
# //////////////////////////////////////////////////////////////


# ROUTES

routes = []


# GET CONTESTS
get_contests_handler = my_gatekeeper(
    name="GET_contests",
    handler=ContestsHandler,
    response_checker=AllowedStatus('422', '402', '201'),
    clients=clients,
    allowed_client_methods=[
        clients.sport_data.java_call_1,
        clients.game_data.java_call_2
    ]
)

routes.append(
    Route(
        '/contests',
        name='contests',
        endpoint=get_contests_handler
    )
)

# GET CONTEST
get_contest_handler = my_gatekeeper(
    name="GET_contest",
    handler=ContestHandler,
    path_handler=PathHandler('fixture_list_id', 'contest_id'),
    query_handler=QueryHandler('foo'),
    response_checker=AllowedStatus('422', '402', '201'),
    clients=clients,
    allowed_client_methods=[
        clients.sport_data.java_call_2
    ]
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