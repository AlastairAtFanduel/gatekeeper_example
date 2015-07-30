from collections import namedtuple
from lru_cache import lru_cache
import inspect

from qualname import qualname

from clients import clients_nt

from werkzeug.routing import Rule

call_info_nt = namedtuple('call_info_nt', ['call', 'args', 'kwargs', 'ret', 'error'])


class Route(object):
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
        path,
        name,
        verb,
        handler,
        clients,               # To allow easy client call detection
        document,              # erm
        path_handler=None,                  # Needs to be inspectable
        query_handler=None,                 # Needs to be inspectable
        status_codes_gatekeeper=None,       # Needs to be inspectable
        client_methods_gatekeeper=None,     # Needs to be inspectable
        client_lru_cache=False,                # While we are here.
        pre_handler_hook=None,              # Not sure why yet.
        post_handler_hook=None,             # Support graphing calls etc.
    ):
        self.path = path
        self.name = name
        self.verb = verb
        self.handler = handler
        self.raw_clients = clients
        self.document = document

        self.path_handler = path_handler
        self.query_handler = query_handler

        self.client_methods_gatekeeper = client_methods_gatekeeper
        self.status_codes_gatekeeper = status_codes_gatekeeper
        self.client_lru_cache = client_lru_cache
        self.pre_handler_hook = pre_handler_hook
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

    def __call__(self, request, *path_params):
        # Not used at all
        if self.pre_handler_hook:
            args = (request) + path_params
            call_info = call_info_nt(self.handler, args, None, None, None)
            self.pre_handler_hook(call_info)

        # set params
        if self.path_handler:
            path_params = self.path_handler(request, path_params)
        else:
            path_params = None

        if self.query_handler:
            query_params = self.query_handler(request, path_params)
        else:
            query_params = None

        # Maybe wrap clients
        client_call_infos = []
        if self.client_methods_gatekeeper or self.client_lru_cache:
            clients = wrap_clients(
                self.raw_clients, client_call_infos, self.client_methods_gatekeeper, self.client_lru_cache
            )
        else:
            clients = self.raw_clients

        import pdb; pdb.set_trace()

        # Service the request.
        error = None
        ret = None
        args = (clients, request, path_params, query_params)
        try:
            ret = self.handler(*args)
        except Exception as error:
            call_info = call_info_nt(self.handler, args, None, ret, error)
        else:
            call_info = call_info_nt(self.handler, args, None, ret, error)
            if self.status_codes_gatekeeper:
                self.status_codes_gatekeeper(ret.status, call_info)

        finally:
            if self.post_handler_hook:
                self.post_handler_hook(call_info, client_call_infos)

        if error:        # Probably rework this flow, probably messes up chaining
            raise error
        return ret

    def to_werkzeug(self):
        """
        Create a werkzeug Rule object.

        :returns: werkzeug.routing.Rule.
        """
        return Rule(self.path, endpoint=self.name)

    def invoke_handler(self, request, **values):
        """
        Calls the routes endpoint and returns the response.

        :param request:
        :param values: dict -- kwargs of request endpoint values.
        :returns: werkzeug.wrappers.Response.
        """
        return self(request, **values)

    def __dir__(self):
        # Only here to make demo simple
        return [
            'path',
            'name',
            'verb',
            'path_params',
            'query_params',
            'allowed_client_methods',
            'allowed_status_codes',
            'documents_doc',
            'handler_doc'
        ]

    # inspector stuff
    @property
    def path_params(self):
        return self.path_handler.params if self.path_handler else []

    @property
    def query_params(self):
        return self.query_handler.params if self.query_handler else []

    @property
    def allowed_client_methods(self):
        method_names = []
        if self.client_methods_gatekeeper:
            methods = self.client_methods_gatekeeper.allowed
            for method in methods:
                method_names.append(qualname(method))
        return method_names

    @property
    def allowed_status_codes(self):
        return self.status_codes_gatekeeper.allowed

    @property
    def documents_doc(self):
        return self.document.__doc__

    @property
    def handler_doc(self):
        return self.handler.__doc__


def wrap_clients(clients, call_store, client_methods_gatekeeper, client_lru_cache):
    # Save the client calls.
    assert isinstance(call_store, list)

    class ClientProxy(object):
        def __init__(self, client):
            self.client = client
            self.method_proxies = {}
            for name, method in inspect.getmembers(client, inspect.ismethod):
                if not name.startswith('_'):
                    if client_lru_cache:
                        new_method = lru_cache()(method)
                    if client_methods_gatekeeper:
                        new_method = client_meth_wrapper(new_method)
                    self.method_proxies[method.__name__] = new_method

        def __getattr__(self, thing):
            if thing in self.method_proxies:
                return self.method_proxies[thing]
            return getattr(self.method_proxies, thing)

    def client_meth_wrapper(func):
        def inner(self, *args, **kwargs):
            call_info = call_info_nt(func, args, kwargs, None, None)
            client_methods_gatekeeper(call_info)

            ret = None
            error = None
            try:
                ret = func(self, *args, **kwargs)
            except Exception as error:
                pass
            finally:
                call_info = call_info_nt(func, args, kwargs, ret, error)
                call_store.append(call_info)
            if error:     # Probably rework this flow, probably messes up chaining
                raise error
            return ret
        return inner

    client_proxies = []
    for client in clients:
        client_proxies.append(ClientProxy(client))
    return clients_nt(*client_proxies)


# ////////////////////////////////////////////////////////////////
# Toys and Fakery


class PathHandler(object):
    def __init__(self, *path_params):
        self.path_params = path_params

    @property
    def params(self):
        return self.path_params

    def __call__(self, request, path_param_values):
        return namedtuple('path_handler', self.path_params)(path_param_values)


class QueryHandler(object):

    def __init__(self, query_params):
        self.query_params = query_params

    @property
    def params(self):
        return list(self.query_params)

    def __call__(self, request, path_params):
        keys = self.query_params.keys()
        values = []
        for key in keys:
            query_handler = self.query_params.get(key)
            if query_handler:
                value = query_handler(request, path_params)
                values.append(value)

        return namedtuple('query_handler', keys)(values)


class StatusCodeGateKeeper(object):
    def __init__(self, allowed):
        self.allowed = allowed

    def __call__(self, status_code):
        if status_code not in self.allowed:
            print("Illegal status code", status_code)


class MethodGateKeeper(object):
    def __init__(self, allowed):
        self.allowed = allowed

    def __call__(self, client_call_info):
        call, args, kwargs, ret, error = client_call_info
        if call not in self.allowed:
            print("enforcer: Illegal call to ", client_call_info.call.__name__)
