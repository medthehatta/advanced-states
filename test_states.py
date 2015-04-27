# coding: utf8

import pytest
from collections import namedtuple
import random

import states


@pytest.yield_fixture()
def basic_queriers():
    QuerierContainer = namedtuple('DataContainer', 'q_true,q_false,q_random')
    yield QuerierContainer(
        q_true=states.Querier(
            name='Always True Querier',
            method=lambda: True,
        ),
        q_false=states.Querier(
            name='Always False Querier',
            method=lambda: False,
        ),
        q_random=states.Querier(
            name='Random Querier',
            method=lambda: random.random(),
        ),
    )


@pytest.yield_fixture()
def basic_states(basic_queriers):
    BasicStatesContainer = namedtuple(
        'BasicStatesContainer',
        's_true,s_high,s_weird_name',
    )
    yield BasicStatesContainer(
        s_true=states.FundamentalState(
            name='Always True State',
            querier=basic_queriers.q_true,
        ),
        s_high=states.FundamentalState(
            name='Sometimes High State',
            querier=basic_queriers.q_random,
            query_evaluator=lambda x: x > 0.5
        ),
        s_weird_name=states.FundamentalState(
            name='A__State Name _ A # ',
            querier=basic_queriers.q_true,
        ),
    )


@pytest.yield_fixture()
def attached_querier():
    AttachedQuerierContainer = namedtuple(
        'AttachedQuerierContainer',
        'obj,q',
    )
    obj = {'v': False}
    yield AttachedQuerierContainer(
        obj=obj,
        q=states.Querier(
            name='Attached Querier',
            method=lambda: obj,
        ),
    )


@pytest.yield_fixture()
def attached_state(attached_querier):
    AttachedStateContainer = namedtuple(
        'AttachedStateContainer',
        'obj,q,s',
    )
    q = attached_querier.q
    yield AttachedStateContainer(
        obj=attached_querier.obj,
        q=q,
        s=states.FundamentalState(
            name='Attached State',
            querier=q,
            query_evaluator=lambda x: x['v'] == 'found',
        ),
    )


def test_basic_queriers(basic_queriers):
    t = basic_queriers.q_true
    assert t.name == 'Always True Querier'
    assert t.query(use_cache=True) == 1


def test_querier_attached_to_object_works_with_cache(attached_querier):
    obj = attached_querier.obj
    q = attached_querier.q

    obj['v'] = False
    assert q.query(use_cache=False) == {'v': False}


def test_querier_attached_to_object_works_with_no_cache(attached_querier):
    obj = attached_querier.obj
    q = attached_querier.q

    obj['v'] = False
    q.query(use_cache=False)
    obj['v'] = True
    assert q.query() == {'v': False}
    assert q.query(use_cache=False) == {'v': True}


def test_querier_attached_to_object_works_with_clear(attached_querier):
    obj = attached_querier.obj
    q = attached_querier.q

    obj['v'] = True
    q.query(use_cache=False)
    obj['v'] = False
    q.clear()
    assert q.query() == {'v': False}


def test_canonical_name(basic_states):
    assert basic_states.s_true.canonical_name == 'always_true_state'
    assert basic_states.s_weird_name.canonical_name == 'a__state_name___a_'


def test_attached_state_sanity(attached_state):
    obj = attached_state.obj
    s = attached_state.s

    obj['v'] = 'found'
    assert s.inspect()

    obj['v'] = 'not found'
    assert not s.inspect(use_cache=0)

    obj['v'] = 'found'
    assert s.inspect(use_cache=0)

    # Checking cache, not real value
    obj['v'] = 'not found'
    assert s.inspect()

    s.clear_caches()
    assert not s.inspect()


def test_attached_state_children(attached_state):
    q = attached_state.q
    s = attached_state.s

    assert s.children == []
    assert s.queriers == [q]
    assert s.all_children == s.children


def test_attached_state_id_exists(attached_state):
    s = attached_state.s
    assert s.generate_unique_id()
    assert states.State.generate_unique_id()
    assert states.FundamentalState.generate_unique_id()
    assert states.CompositeState.generate_unique_id()
    with pytest.raises(AttributeError):
        states.Querier.generate_unique_id()
