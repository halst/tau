from datetime import datetime

import pytest

from tau import MemoryBackend, BinaryBackend, CSVBackend


all = (MemoryBackend, BinaryBackend, CSVBackend)


def backends(*args):
    return pytest.mark.parametrize(('backend',), [(b(),) for b in args])


def teardown_function(function):
    for backend in all:
        backend().clear()


@backends(*all)
def test_backend_signals(backend):
    backend.set('foo', 9)
    assert backend.signals() == ['foo']
    backend.set('bar', 9)
    assert set(backend.signals()) == set(['foo', 'bar'])


@backends(*all)
def test_backend_clear(backend):
    backend.set('eggs', 9)
    backend.set('spam', 9)
    assert set(backend.signals()) == set(['eggs', 'spam'])
    backend.clear()
    assert set(backend.signals()) == set()


@backends(*all)
def test_backend_get(backend):
    backend.set('foo', 8)
    res = backend.get('foo')
    assert res[1] == 8
    assert type(res[0]) == datetime


@backends(MemoryBackend, CSVBackend)
def test_backend_get_compound(backend):
    backend.set('foo', {'this': 1, 'that': [2, 3]})
    res = backend.get('foo')
    assert res[1] == {'this': 1, 'that': [2, 3]}
    assert type(res[0]) == datetime


@backends(*all)
def test_backend_get_start_end(backend):
    backend.set('foo', 1)
    backend.set('foo', 2)
    backend.set('foo', 3)
    one, two, three = backend.get('foo', datetime.min, datetime.now())
    assert (one[1], two[1], three[1] == 1, 2, 3)


@backends(*all)
def test_backend_get_limit(backend):
    for n in range(10):
        backend.set('foo', n)
    res = backend.get('foo', datetime.min, datetime.now())
    assert len(res) == 10
    res = backend.get('foo', datetime.min, datetime.now(), limit=4)
    assert len(res) == 4
