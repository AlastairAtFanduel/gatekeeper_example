from collections import namedtuple

# //////////////////////////////////////////////////////////
# Toys and placeholders


def basic_thing_handler(*args):
    return namedtuple('client', args)

PathHandler = basic_thing_handler
QueryHandler = basic_thing_handler


def AllowedStatus(*allowed_status):
    def allowed_status(response):
        return response.status in allowed_status
    return allowed_status

# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


class GateKeeper(object):
    """
    To handler will get passed
        request,
        path_paramters,   # id etc.
        query_model,
        clients,

    This gatekeeper exists to:
        * To pass a inspectable query_handler into the handler
        * Make explicit the client methods that are called
        * Make explicit the client status codes that can be returned
        * Gatekeeper records the client calls used by every request, 
            the result of each call and the overall status code
        * Within a single request lru_cache all client calls.  
            Call sport_data.foo(1) twice it only gets called once.  
            The second call just returns what the first call did.

        Make each handler is inspectable:
            Can tell the query parameters it accepts
            The underlying methods it may call
            The status_codes it may return
            The doc string of the handler

        cache: if this is true protect the clients with a lru_cache to save anyreuse
        validator: if a function is passed here it will be called every time an 
            unallowed client method or status code is returned.  Could just 
            add logging or expolde or do nothing.
        recoder: If given this function is called after each request:
            the request, the return response/exception/other
            the client calls used, args and returns/exceptions
    """

    def __init__(
        name,
        handler,
        path_handler=None,
        query_handler=None,
        clients=None,
        allowed_methods=None,
        response_checker=None,
        lru_cache=True,
        invalid=None,
        post_handler_hook=None
    ):
        self.handler = handler
        self.path_handler = path_handler
        self.query_handler = query_handler

        # ToDo wrap clients
        self.clients = clients
        self.allowed_methods = allowed_methods
        self.cache = cache

        #
        self.allowed_responses = allowed_responses
        self.invalid = validator
        self.recorder = recorder

    def __call__(self, request, *path_params):
        if self.path_handler:
            path_params = self.path_handler(*path_params)
        else:
            path_params = None

        if self.query_handler:
            query_params = 12 #Todo
        else:
            query_params = None


        self.handler(request)

    def __doc__(self):
        pass

    def path_params(self):
        pass

    def query_params(self):
        pass

    def last_call