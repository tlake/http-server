[![Travis](https://travis-ci.org/tlake/http-server.svg)](https://travis-ci.org/tlake/http-server.svg)

# http-server

A simple HTTP server in Python.


## Authors:
- [Tanner Lake](http://github.com/tlake)
- [Scott Schmidt](http://github.com/sjschmidt44)


## Resources Used:

### SO_REUSEADDR


Attempting to start a server on the same port as a recently-terminated server
would generate this error:

```socket.error: [Errno 98] Address already in use```

This is because the previous server left the socket in a `TIME_WAIT` state,
so it couldn't be immediately reused. Solution to this problem was discovered
in the [Python Docs](https://docs.python.org/2/library/socket.html), in the
`socket.SO_REUSEADDR` socket flag.


### Running the Server in the Background


We knew that we needed to somehow run the server in the background for our
tests, otherwise the server would hold onto the prompt and refuse to let any
subsequent tests execute. If `CTRL-C` were sent, the server would terminate
and then the following tests would have no server to which to connect.

Hints from the team of
[Jonathan Stallings](https://github.com/jonathanstallings),
[Jim Grant](https://github.com/MigrantJ), and
[Andrew Wilson](https://github.com/wilson0xb4)
([their work here](https://github.com/wilson0xb4/http-server))
pointed us in the direction of Pytest's
[`yield_fixture`](https://pytest.org/latest/yieldfixture.html) and the
[`multiprocessing`](http://pymotw.com/2/multiprocessing/basics.html) module.


### Running *Multiple* Servers in the Background


Progression to spinning up a gevent server was trivial; extending testing
to a gevent server was not. In retrospect, all of the tests written for
the original server.py work perfectly well for gevent_server.py, once a
couple pointers were properly redirected. The bigger issues, though,
were the yield fixtures.

We used to have a yield fixture for each of the functional test suites,
which would start up their respective servers and keep them going, we
thought, until the end of the yield fixture's scope. Since these server
fixtures were scoped to `module`, we believed they would terminate at
the end of the module. In practice, it seems that a yield fixture doesn't
terminate until the end of the *entire* testing session, regardless
of defined scope.

The solution - the discovery thereof again facilitated by Jonathan Stallings -
is to use just a regular fixture with a process-terminating finalizer.
The scope behaves properly, and autouse also still works.
