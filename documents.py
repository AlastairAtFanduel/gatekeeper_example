
import json


class ContestsDocument(object):
    """
    .. sourcecode:: json

        "_meta": {
            "_primary_document": "contests",
            "count": self.contest_count,
            "entry_fees": [
                0, 1, 2, 5, 10, 25, 50, 109, 270, 535, 1000, 1065, 5300,
                10600, 50000
            ]
        },
        "contests": [OpenContestSubDocument],
        "contest_types": [ContestTypeSubDocument],
        "contest_sub_types": [ContestSubTypeSubDocument],
        "fixture_lists": [FixtureListSubDocument],
        "users": [UserSubDocument]
    """
    def __call__(self, data):
        return json.dumps(data)


class ContestDocument(object):
    """
    .. sourcecode:: json

        "_meta": {
            "_primary_document": "contests"
        },
        "contests": [self._transform_contest(), ],
        "fixture_lists": [self._transform_fixture_list(), ],
        "fixtures": [
            self._transform_fixture(f) for f in self.fixtures
        ],
        "teams": [
            self._transform_team(t) for t in self.teams
        ],
        "users": []
    """
    def __call__(self, data):
        return json.dumps(data)
