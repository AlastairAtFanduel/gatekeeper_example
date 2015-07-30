#############################################
# EXAMPLE
############################################

# INSPECTABILTY

from routes import ROUTES

print(dir(ROUTES[0]))


for route in ROUTES:
    print('-'*80)
    #for item in dir(route):
    #    print('{}={}'.format(item, getattr(route, item)))

    print("path={}".format(route.path))
    print("name={}".format(route.name))
    print("verb={}".format(route.verb))
    print("path_params={}".format(route.path_params))
    print("query_params={}".format(route.query_params))
    print("allowed_client_methods={}".format(route.allowed_client_methods))
    print("allowed_status_codes={}".format(route.allowed_status_codes))
    print("documents_doc={}".format(route.documents_doc))
    print("handler_doc={}".format(route.handler_doc))


import sys; sys.exit()

# ############################################################################

# CALL LOGGING


# Show call logging
from routes import get_contests_handler, get_contest_handler
import gate_keeper
from werkzeug.datastructures import MultiDict
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def build_request_obj(query_strings=None):
    builder = EnvironBuilder(query_strings)      # query_string=)
    env = builder.get_environ()
    request = Request(env)
    #request.args = MultiDict()
    return request


# GET contests
request = build_request_obj()
ret = get_contests_handler(request)


# GET contest
fixture_list_id = 1
contest_id = 2
request = build_request_obj(query_strings={'foo': False})
ret = get_contest_handler(request, fixture_list_id, contest_id)


###########################################
# CALL graph with querying

ALL_CALLS = []


def capture_all_calls(handler_call, client_calls):
    # This would just be a file or remote service, not stored in memory
    ALL_CALLS.append(handler_call, client_calls)

get_contest_handler.post_handler_hook = capture_all_calls


# GET contest
fixture_list_id = 1
contest_id = 2
request = build_request_obj(query_strings={'foo': False})
for x in range(10):
    ret = get_contest_handler(request, fixture_list_id, contest_id)

request = build_request_obj(query_strings={'foo': True})
for x in range(3):
    ret = get_contest_handler(request, fixture_list_id, contest_id)


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
