#############################################
# EXAMPLE
############################################

# INSPECTABILTY

from routes import ROUTES

print(dir(ROUTES[0]))


for route in ROUTES:
    print('-'*80)
    #for item in dir(route):   # Unordered
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


#import sys; sys.exit()

# ############################################################################

contests_router = ROUTES[0]
contest_router = ROUTES[1]

# BASIC CALL LOGGING
print(('='*80 + '\n')*3)
print("BASIC CALL LOGGING")

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


# GET contests
request = build_request_obj({})




ret = contests_router(request)

#import sys; sys.exit()


# ############################################################################

# CALL LOGGING WITH PARAMS
print(('='*80 + '\n')*3)
print("CALL LOGGING WITH PARAMS")

# GET contest
fixture_list_id = 1
contest_id = 2
request = build_request_obj(query_strings={'foo': "True"})


ret = contest_router(request, fixture_list_id, contest_id)

# CALL LOGGING WITH PARAMS
print(('='*80 + '\n')*3)
print("CALL LOGGING WITH PARAMS2")

request = build_request_obj(query_strings={'foo': "False"})


ret = contest_router(request, fixture_list_id, contest_id)

import sys; sys.exit()

