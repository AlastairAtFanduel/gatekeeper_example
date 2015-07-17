from collections import namedtuple
import functools
import inspect

call_info_nt = namedtuple('call_info_nt', ['call', 'args', 'kwargs', 'ret', 'error'])


class GateKeeper(object):
    """
    Puts everything that is good to know in one place.

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


        lru_cache: if this is true protect the clients with lru_cache to save anyreuse
        validator: if a function is passed here it will be called every time an
            unallowed client method or status code is returned.  Could just
            add logging or expolde or do nothing.
        recoder: If given this function is called after each request:
            the request, the return response/exception/other
            the client calls used, args and returns/exceptions

    To handler will get passed
        clients,
        request,
        path_param_model,
        query_model,

    """

    def __init__(
        self,
        name,
        handler,
        clients=None,           # To allow easy client call detection
        path_handler=None,             # Needs to be inspectable
        query_handler=None,            # Needs to be inspectable
        allowed_status_codes=None,     # Needs to be inspectable
        allowed_methods=None,          # Needs to be inspectable
        disallowed_status_code_hook=None,   # To support debuging/enforcement.
        disallowed_method_hook=None,        # To support debuging/enforcement.
        lru_cache=True,                # While we are here.
        post_handler_hook=None,             # Support graphing calls etc.
    ):
        self.handler = handler
        self.clients = clients

        self.path_handler = path_handler
        self.query_handler = query_handler

        self.allowed_status_codes = allowed_status_codes
        self.allowed_methods = allowed_methods
        self.disallowed_status_code_hook = disallowed_status_code_hook
        self.disallowed_method_hook = disallowed_method_hook
        self.lru_cache = lru_cache
        self.post_handler_hook = post_handler_hook

    def make_params_model(self, path_params):
        if self.path_handler:
            path_params = self.path_handler(*path_params)
        else:
            path_params = None
        return path_params

    def make_query_model(self, request):
        if self.query_handler:
            # ToDo
            import pdb
            pdb.set_trace()
            query_params = self.query_handler(request.args)
        else:
            query_params = None
        return query_params

    def get_clients(self, call_array):
        if self.allowed_methods:
            clients = clients_wrapper(
                self.clients,
                call_array,
                self.allowed_methods,
                self.disallowed_method_hook,
                self.lru_cache,
            )
        else:
            clients = self.clients
        return clients

    def __call__(self, request, *path_params):
        path_params = self.path_handler(path_params)
        query_params = self.make_query_model(request)

        client_call_infos = []
        clients = self.get_clients(client_call_infos)

        error = None
        ret = None
        args = (clients, request, path_params, query_params)
        try:
            ret = self.handler(*args)
        except Exception as error:
            call_info = call_info_nt(self.handler, args, None, ret, error)
        else:
            call_info = call_info_nt(self.handler, args, None, ret, error)
            if ret.status not in self.allowed_status:
                if self.disallowed_status_code_hook:
                    self.disallowed_status_code_hook(call_info)
        finally:
            if self.post_handler_hook:
                self.post_handler_hook(call_info, client_call_infos)

        if error:        # Probably rework this flow, probably messes up chaining
            raise error
        return ret

    # Is this possible
    # def __doc__(self):
    #    return self.handler.__doc__
    #
    # def last_call(self):
    #    pass


def clients_wrapper(clients, call_store, allowed_methods, disallowed_method_handler):
    # Save the client calls.
    assert isinstance(call_store, list)

    def client_meth_wrapper(func):
        def inner(*args, **kwargs):
            if func not in allowed_methods:
                if disallowed_method_handler:
                    call_info = call_info_nt(func, args, kwargs, None, None)
                    disallowed_method_handler(call_info)

            ret = None
            error = None
            try:
                ret = func(*args, **kwargs)
            except Exception as error:
                pass
            finally:
                call_info = call_info_nt(func, args, kwargs, ret, error)
                call_store.append(call_info)
            if error:     # Probably rework this flow, probably messes up chaining
                raise error
            return ret
        return inner

    for client in clients:
        for method in inspect.getmembers(client, inspect.ismethod):
            if not method.__name__.startwith('_'):
                lru_cached_method = functools.lru_cache(method)
                new_method = client_meth_wrapper(lru_cached_method)
                client.__setattr__(client, method.__name__, new_method)


# ////////////////////////////////////////////////////////////////
# Toys and Fakery


def basic_thing_handler(*args):
    return namedtuple('client', args)

PathHandler = basic_thing_handler
QueryHandler = basic_thing_handler


def enforcer(traceback, method, method_name, params):
    """Placeholder This really needs a defined interface"""
    print("An unallowed method was called happened")
    print(traceback)
    raise AssertionError("Bad Coder!")


def my_call_logger(handler_call_info, client_call_infos):
    # Print and PDB
    print("Logging the last call")
    handler, handler_args, handler_kwargs, ret, error = handler_call_info
    clients, request, path_params, query_params = handler_args
    print("Handler of name={} was called with".format(handler.name))
    print(request, ret, error)
    print("It used the following calls")

    for client_method, client_args, client_kwargs, client_ret, client_error in client_call_infos:
        print(client_method, client_args, client_kwargs, client_ret, client_error)
    import pdb
    pdb.set_trace()
# //////////////////////////////////////////////////////////////


GateKeeper = functools.partial(
    GateKeeper,
    disallowed_method_hook=enforcer,
    post_handler_hook=my_call_logger
)


# allowed_methods and disallowed_method_hook could be merged
# allowed_status_codes and disallowed_method_hook
