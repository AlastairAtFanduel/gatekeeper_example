"""
Fake c3pyo clients :)
"""

class FakeGameDataC3pyo(object):
    def java_call_1(self, x):
        return x

    def java_call_2(self, x):
        return x


class FakeSportDataC3pyo(object):
    def java_call_1(self, x):
        return x

    def java_call_2(self, x):
        return x


clients_nt = namedtuple('clients_nt', ['game_data', 'sport_data'])
clients = clients_nt(FakeGameDataC3pyo(), FakeSportDataC3pyo())
