from routes import ROUTES

contests_router = ROUTES[0]
contest_router = ROUTES[1]

# Show call logging
from routes import ROUTES
import gate_keeper
from werkzeug.datastructures import MultiDict
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request, Response

def build_request_obj(query_strings):
    print(query_strings)
    builder = EnvironBuilder()      # query_string=)
    env = builder.get_environ()
    request = Request(env)
    request.args = MultiDict(query_strings.items())
    return request


###########################################
# CALL graph with querying

ALL_CALLS = []


def capture_all_calls(handler_call, client_calls):
    # This would just be a file or remote service, not stored in memory
    ALL_CALLS.append((handler_call, client_calls))

contest_router.post_handler_hook = capture_all_calls


# GET contest
fixture_list_id = 1
contest_id = 2
request = build_request_obj(query_strings={'foo': False})
for x in range(10):
    ret = contest_router(request, fixture_list_id, contest_id)

request = build_request_obj(query_strings={'foo': True})
for x in range(3):
    ret = contest_router(request, fixture_list_id, contest_id)


import sys
sys.exit()


def yield_call_data():
    for handler_call, client_calls in ALL_CALLS:
        call, args, kwargs, ret, error = handler_call
        clients, request, path_params, query_params = args
        call_name = call.__name__
        query_params

        client_methods = []
        for call, args, kwargs, ret, error in client_calls:
            client_methods.append(call.__name__)

        yield call_name, query_params, client_methods

for handler_name, query_params, client_methods in yield_call_data():
    print(handler_name, query_params, client_methods)

# Could quite easily record the call graph for everything, and query down to
# find what params cause what calls.
# What errors are caused by what calls and parameter sets.
# Could capture everything.