from collections import namedtuple

# //////////////////////////////////////////////////////////
# Toys and placeholders


def basic_thing_handler(*args):
    return namedtuple('client', args)

PathHandler = basic_thing_handler
QueryHandler = basic_thing_handler


class AllowedStatus(object):
    def (*allowed_status):
        pass
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
        response_checker=None,
        post_handler_hook=None,
        clients=None,
        allowed_methods=None,
        disallowed_client_method=None,
        lru_cache=True,
    ):
        self.handler = handler
        self.path_handler = path_handler
        self.query_handler = query_handler

        self.clients = clients
        self.allowed_methods = allowed_methods
        self.invalid = validator
        
        self.lru_cache = lru_cache
        self.allowed_responses = allowed_responses
        


        self.recorder = recorder

    def __call__(self, request, *path_params):
        if self.path_handler:
            path_params = self.path_handler(*path_params)
        else:
            path_params = None

        if self.query_handler:
            query_params = 12 #Todo werkzeug magic
        else:
            query_params = None

        with self as clients:
            ret = self.handler(request, path_params, query_params, clients)


    def __enter__(self):
        return ClientRecorder(clients)

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __doc__(self):
        pass

    def path_params(self):
        pass

    def query_params(self):
        pass

    def last_call(self):
        pass



def log_call(stack):
    def wrap(func):
        def inner(*args, **args):
            ret = None
            try:
                ret = func(*args, **kwargs)
            except Exception as e:
                pass
            stack.append(func, args, kwargs, ret, e)
    return wrap



class ClientRecorder(object):
    def __init__(self, clients, allowed_methods):
        self.clients = clients
        self.calls = []
        self.logger = log_call(self.calls)
        self.allowed_methods = allowed_methods

    def __getattr__(self, attr):
        return self.logger(getattr(self.clients, attr))
