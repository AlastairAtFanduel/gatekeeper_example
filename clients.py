"""
Fake c3pyo clients :)
"""

from collections import namedtuple


class FakeGameDataC3pyo(object):
    def java_call_1(self, x):
        print("RAW call FakeGameDataC3pyo.java_call_1")
        return x

    def java_call_2(self, x):
        print("RAW call FakeGameDataC3pyo.java_call_2")
        return x


class FakeSportDataC3pyo(object):
    def java_call_1(self, x):
        print("RAW call FakeSportDataC3pyo.java_call_1")
        return x

    def java_call_2(self, x):
        print("RAW call FakeSportDataC3pyo.java_call_2")
        return x


clients_nt = namedtuple('clients_nt', ['game_data', 'sport_data'])
clients = clients_nt(FakeGameDataC3pyo(), FakeSportDataC3pyo())
