========
Overview
========

Domain
------

All API access is over HTTPS from the ``api.fanduel.com`` domain. All data is
sent and received in JSON format, using custom `Media types`_.

Date & time formats
-------------------

All time values are provided as strings in ISO8601_ format:

``YYYY-MM-DDTHH:MM:SSZ``

e.g. ``2013-10-11T17:24:25Z``

All duration values are provided as strings in ISO8601_ duration format:

e.g. ``PT2H33M12S`` - 2 hours, 33 minutes and 12 seconds

.. _ISO8601: http://en.wikipedia.org/wiki/ISO_8601

Parameters
----------

GET requests can include path parameters, e.g.

.. sourcecode:: http

    GET https://api.fanduel.com/users/12345 HTTP/1.1

GET requests can also include optional query string parameters, e.g.

.. sourcecode:: http

    GET https://api.fanduel.com/users/12345/entries?type=live HTTP/1.1

Parameters not in the URL path for destructive or creative methods should be
encoded as JSON, e.g.

.. sourcecode:: http

    POST https://api.fanduel.com/password-resets HTTP/1.1

    {"email": "steelersfan@mailprovider.com"}

General server errors
---------------------

If the API service is unavailable, all requests will return a 503 SERVICE
UNAVAILABLE response with a standard error response body (see
`Error messaging`_).

.. sourcecode:: http

    HTTP/1.1 503 SERVICE UNAVAILABLE
    Content-Type: application/json

    {
        "errors": [
            {
                "summary": "Service unavailable",
                "description": "The FanDuel API service is currently unavailable."
            }
        ]
    }

General client errors
---------------------

There are some common error response codes across the API:

``400 Bad Request`` - Commonly caused by malformed JSON in the request body or
sending unrecognised JSON values.

``401 Unauthorized`` - If a resource or action requires authentication

``403 Forbidden`` - If the requesting application is not permitted to use a
resource.

``404 Not Found`` - If a resource is not found

``405 Method not allowed`` - If the attempted HTTP method is not supported on
this resource

``406 Not Acceptable`` - If the requested media types can not be supported

``415 Unsupported Media Type`` - If the provided request data is not of a
supported media type.

Error messaging
---------------

An error response *may* also include further details of the error(s), with
the following body response format:

.. sourcecode:: json

    {
        "errors": [
            {
                "code": "entry-010",
                "summary": "Salary cap exceeded",
                "description": "The total salaries for your choices exceeds the salary cap for this contest"
            }
        ]
    }

.. object:: errors (array)

    A collection of error objects, each containing the following details:

    .. object:: code (string)

        The internal error code reference, if relevant. These are documented on
        the relevant resource.

    .. object:: summary (string)

        A summary of the error, suitable for display to the user.

    .. object:: description (string)

        A longer description of the error, suitable for display to the user.

    .. object:: attribute (string) - optional

        A key indicating the attribute of the POST request body on which the
        error was raised. This always refers to the primary document in the
        request body.

Redirects
---------

Any request could result in a redirect, so there should be generalised client
code to handle them. Redirect responses will use a ``Location`` header
containing the URI to repeat the request for.

HTTP Verbs
----------

The FanDuel API uses appropriate HTTP verbs for each action

``GET`` - Retrieve the resource

``POST`` - Create resources or perform custom actions

``PUT`` - Replace a resource or collection.

``DELETE`` - Delete a resource.

Authentication
--------------

See main article

Response glossary
-----------------

We use a number of terms in describing response formats that are useful to
understand

response
    The result of making an HTTP request to the API.

response body
    The entire JSON payload delivered as part of a response

resource
    An abstract concept mapping to an object or process in the system that is
    being represented. e.g. a 'roster' is a resource, as are 'players', 'users'
    and 'fixtures'.

representation or document
    The current state of the referenced resource. A single response can include
    a number of documents, and a number of different document formats can
    represent a single resource. e.g. There may be a summary and a full document
    version of a document where the full version provides much more detailed
    information.

Hypermedia and links
--------------------

Documents may contain a ``_url`` property that links to a canonical
representation wherever they appear. Often a separate ``id`` property is also 
included.  The ``_url`` properties should be used rather than
constructing URLs in the client, e.g. from ``id`` attributes.

Some responses may include multiple document types. For example, a request for a
user's live rosters can include details of the fixture lists and players related
to those rosters as summary documents. In this case, unique summary documents
are returned at the root of the document, and the ``_ref`` and ``_members``
attributes are used to specify the relationship, in addition to providing a
``_url`` where the related resource's canonical representation can be found.

One-to-one relationship example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An ``entry`` resource may refer to a related ``contest`` summary with a link to
its canonical representation:

.. sourcecode:: json

    {
        "entries": [
            {
                "id": "987",
                "_url": "https://api.fanduel.com/entries/987",
                "prize": "$9",
                "contest": {
                    "_ref": "contests.id",
                    "_members": ["654"]
                }
            }
        ],
        "contests": [
            {
                "id": "654",
                "_url": "https://api.fanduel.com/contests/3232-654",
                "name": "NFL 50/50 League"
            }
        ]
    }

One-to-many relationship example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``roster`` resource may refer to member ``player`` summaries, each of which
could be shared by a number of rosters:

.. sourcecode:: json

    {
        "rosters": [
            {
                "id": "432",
                "_url": "https://api.fanduel.com/users/12345/rosters/432",
                "score": 43.5,
                "players": {
                    "_ref": "players.id",
                    "_members": ["1357", "2468", "3579"]
                }
            }
        ],
        "players": [
            {
                "id": "1357",
                "_url": "https://api.fanduel.com/players/1357",
                "first_name": "Aaron",
                "last_name": "Rodgers",
                "position": "QB"
            },
            {
                "id": "2468",
                "_url": "https://api.fanduel.com/players/2468",
                "first_name": "Marshawn",
                "last_name": "Lynch",
                "position": "RB"
            }
        ]
    }

e.g. Or if the ``players`` are available at a separate location:

.. sourcecode:: json

    {
        "rosters": [
            {
                "id": "432",
                "_url": "https://api.fanduel.com/users/12345/rosters/432",
                "score": 43.5,
                "players": {
                    "_url": "https://api.fanduel.com/users/12345/rosters/432/players"
                }
            }
        ]
    }

It is also possible that both a ``_url`` and a combination ``_ref`` and
``_members`` attributes may be given for a one-to-many relationship.

Pagination
----------

Collections returning multiple items are paginated using a consistent format.

Query string parameters can be used to specify the items required:

``page`` - The page to request. 1-based. The default value is ``1``.

``page_size`` - The number of items to return per page. Maximum and default
values vary by resource.

In a paged response, the ``Link`` HTTP header is used to indicate related pages,
e.g.

.. sourcecode:: http

    Link: <https://api.fanduel.com/users/1234/entries?type=live&page=2&page_size=50>; rel="next",
        <https://api.fanduel.com/users/1234/entries?type=live&page=10&page_size=50>; rel="last",
        <https://api.fanduel.com/users/1234/entries?type=live&page=1&page_size=50>; rel="first"

The possible values of ``rel`` are ``first``, ``last``, ``prev`` and ``next``.

Where multiple document types are provided in a response, pagination is over the
primary (requested) resource representation, which is specified in a ``_meta``
section:

.. sourcecode:: json

    {
        "_meta": {
            "_primary_document": "entries"
        },
        "entries": [

        ]
    }

Rate limiting
-------------

TODO

Conditional requests
--------------------

TODO. Last-modified, If-None-Match, If-Modified-Since, ETag etc.

Media types
-----------

TODO
