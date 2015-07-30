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
from contest import ContestsHandler, ContestHandler, foo_handler
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
# Toys

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


def get_call_logger():
    if not __debug__:
        return None
    else:
        def call_logger(handler_call_info, client_call_infos):
            handler, handler_args, handler_kwargs, ret, error = handler_call_info
            clients, request, path_params, query_params, documenter = handler_args
            print('*'*80 + " CALL LOGGER")
            print("\t Handler of name={} was called with args {}".format(handler.__name__, path_params))
            #print(request, ret, error)
            print("\t Client calls")
            for client_method, c_args, c_kwargs, c_ret, c_error in client_call_infos:
                print("\t\t -> client call " + client_method.__name__)
        return call_logger


# //////////////////////////////////////////////////////////////


ROUTES = []

# GET CONTESTS
ROUTES.append(
    Route(
        path='/contests',
        name='/contests',
        verb='GET',
        handler=ContestsHandler,
        clients=clients,
        document=ContestsDocument(),
        status_codes_gatekeeper=status_code_gatekeeper('422', '402', '201'),
        client_methods_gatekeeper=client_gatekeeper(
            clients.sport_data.sport_data_java_call_1,
            clients.game_data.game_data_java_call_2
        ),
        post_handler_hook=get_call_logger(),
        client_lru_cache=__debug__
    )
)


# GET CONTEST
ROUTES.append(
    Route(
        path='/contests/<numeric_string:fixture_list_id>-<numeric_string:contest_id>',
        name='/contest',
        verb='GET',
        handler=ContestHandler,
        clients=clients,
        document=ContestDocument(),
        path_handler=PathHandler('fixture_list_id', 'contest_id'),
        query_handler=QueryHandler({'foo': foo_handler}),
        status_codes_gatekeeper=status_code_gatekeeper('422', '402', '201'),
        client_methods_gatekeeper=client_gatekeeper(
            clients.sport_data.sport_data_java_call_2
        ),
        post_handler_hook=get_call_logger(),
        client_lru_cache=__debug__
    )
)
