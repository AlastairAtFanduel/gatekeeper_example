"""
EXPERIMENTAL ROUTES

Experiment passing inspectable elements into handlers via routes.

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
from gate_keeper import (
    Route,
    PathHandler,
    QueryHandler,
    MethodGateKeeper,
    StatusCodeGateKeeper
)
from documents import ContestsDocument, ContestDocument

from clients import clients


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

def client_gatekeeper(*allowed_methods):
    if not __debug__:
        return None
    else:
        return MethodGateKeeper(allowed_methods)


def status_code_gatekeeper(*allowed_status_codes):
    if not __debug__:
        return None
    else:
        return StatusCodeGateKeeper(allowed_status_codes)


def my_call_logger(handler_call_info, client_call_infos):
    if __debug__:
        handler, handler_args, handler_kwargs, ret, error = handler_call_info
        clients, request, path_params, query_params = handler_args
        print("my_call_logger: Handler of name={} was called".format(handler.name))
        print(request, ret, error)
        print("my_call_logger: It used the following calls")
        for client_method, c_args, c_kwargs, c_ret, c_error in client_call_infos:
            print("\t -> client call", client_method)


# //////////////////////////////////////////////////////////////


ROUTES = []

# GET CONTESTS
ROUTES.append(
    Route(
        path='/contests',
        name="GET /contests",
        handler=ContestsHandler,
        clients=clients,
        document=ContestsDocument,
        client_methods_gatekeeper=client_gatekeeper(
            clients.sport_data.java_call_1,
            clients.game_data.java_call_2
        ),
        status_codes_gatekeeper=status_code_gatekeeper('422', '402', '201'),
        post_handler_hook=my_call_logger,
        lru_cache=__debug__
    )
)

# GET CONTEST
ROUTES.append(
    Route(
        path='/contests/<numeric_string:fixture_list_id>-<numeric_string:contest_id>',
        name="GET /contest",
        handler=ContestHandler,
        clients=clients,
        document=ContestDocument,
        path_handler=PathHandler('fixture_list_id', 'contest_id'),
        query_handler=QueryHandler({'foo': 'defaultvalue'}),
        client_methods_gatekeeper=client_gatekeeper(
            clients.sport_data.java_call_2
        ),
        status_codes_gatekeeper=status_code_gatekeeper('422', '402', '201'),
        post_handler_hook=my_call_logger,
        lru_cache=__debug__
    )
)


# ToDo:

# Check responses instead of just status codes
# Python2 doesnas have a full qual name for allowed_client_methods, name magic
