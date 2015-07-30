========
Contests
========

.. _get-contests:

.. http:get:: /contests

    The contests collection resource provides lists of contests filtered by
    various parameters.  If no fixture_list is specfied then only pinned contests
    over all upcoming fixture_lists will be provided (in this case 
    fixture_lists will be be an empty list).

    **Authentication required**: No

    **Example request**:

    .. sourcecode:: http

        GET /contests?fixture_list=8010
        Host: api.fanduel.com
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

    .. sourcecode:: json

        {
            "_meta": {
                "_primary_document": "contests",
                "count": 287,
                "entry_fees": [0, 1, 2, 5, 10, 25, 50, 109, 270, 535, 1000, 10000]
            },
            "contests": [
                <Open contest document>,
                <Open contest document>
            ],
            "contest_types": [
                <Contest type document>,
                <Contest type document>
            ],
            "contest_sub_types": [
                <Contest sub type document>,
                <Contest sub type document>
            ],
            "fixture_lists": [
                <Fixture list summary document>,
                <Fixture list summary document>
            ],
            "users": [
                <User summary document>,
                <User summary document>
            ]
        }

    :query string fixture_list: The id of the fixture list to return contests for.  
    :query string contest_types: The types of contests to return.
        Takes a comma-separated list of contest types.
        Valid contest types are ``H2H``, ``LEAGUE``, ``TOURNAMENT``,
        ``FIFTY_FIFTY`` and ``MULTIPLIER``.
    :query include_restricted: Include restricted contests.
        Acceptable values true and false. Default value is false.
    :query string include_unpinned: Include contests which are unpinned.
        include_unpinned=true return pinned and unpinned contests
        include_unpinned=false return pinned contests
        Default value is 'true'.
        This query string is ignored if there is no fixture_list query.
    :query string status: The status of contests to return. Only ``open`` is permitted (the default).

    **Example query combinations**:

        Note: All queries below,

            * include pinned contests.
            * exclude restricted contests.  Adding ``include_restricted=true`` would include them.

        * fixture_list_id::

            GET /contests?fixture_list=8010

        * fixture_list_id + contest_types::

            GET /contests?fixture_list=8010&contest_types=FIFTY_FIFTY,MULTIPLIER

        * fixture_list_id + pinned only::

            GET /contests?fixture_list=8010&include_unpinned=false

        * Only pinned contests from all upcoming fixture_lists::

            GET /contests

            N.B. fixture_lists will be an empty list in this case.

    :statuscode 200: No error
    :statuscode 422: Unprocessable entity - query parameters invalid

    **Documents**:

.. _get-contest:

.. http:get:: /contests/(str:id)

    The individual contest resource provides detailed information about the
    contest, rules, associated fixtures and prize structures.

    **Authentication required**: No

    Responds with information about a contest, including sport, name, salary
    cap, size, entry count, entry fee, total prize amount, prize breakdown,
    fixtures, rules, start time.

    **Example request**:

    .. sourcecode:: http

        GET /contests/343434-2914582 HTTP/1.1
        Host: api.fanduel.com
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

    .. sourcecode:: json

        {
            "_meta": {
                "_primary_document": "contests"
            },
            "contests": [
                < Full contest document >
            ],
            "fixture_lists": [
                < Fixture list summary document >
            ],
            "fixtures": [
                < Fixture document >,
                < Fixture document >
            ],
            "teams": [
                < Team document >,
                < Team document >
            ],
            "users": [
                < User document >,
                < User document >
            ]
        }

    :param string id: Contest ID

    :statuscode 200: No error
    :statuscode 404: Contest not found

    **Documents**:

