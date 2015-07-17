#############################################
# EXAMPLE
############################################

#
#
#

# get_contests_handler(Request())
# get_contests_handler(Request())

from routes import ROUTES

for route in ROUTES:
    print(route.name)
    print(route.path)
    print(route.endpoint.handler.__doc__)
    print(route.endpoint.path_handler)
    print(route.endpoint.query_handler)
    print(route.endpoint.allowed_status_codes)
    print(route.endpoint.allowed_methods)


# Show call graph
from routes import get_contests_handler, get_contest_handler
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
request = build_request_obj(query_strings={'foo': '71871613876'})
ret = get_contest_handler(request, fixture_list_id, contest_id)



# Show unexpected status code


# Show lru caching


# Show debug mode