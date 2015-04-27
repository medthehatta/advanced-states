# coding: utf8

import pytest
from collections import namedtuple

import states


@pytest.yield_fixture()
def basic_queriers():
    QuerierContainer = namedtuple('DataContainer', 'q_true,q_false,q_random')
    yield QuerierContainer(
        q_true = states.Querier(
            name='Always True Querier',
            method=lambda: True,
        ),
        q_false = states.Querier(
            name='Always False Querier',
            method=lambda: False,
        ),
        q_random = states.Querier(
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
        s_true = states.FundamentalState(
            name='Always True State',
            querier=basic_queriers.q_true,
        ),
        s_high = states.FundamentalState(
            name='Sometimes High State',
            querier=basic_queriers.q_random,
            query_evaluator=lambda x: x > 0.5
        ),
        s_weird_name = states.FundamentalState(
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
    obj = {'value': False}
    yield AttachedQuerierContainer(
        obj = obj,
        q = states.Querier(
            name='Attached Querier',
            method=lambda: obj['value'],
        ),
    )


def test_basic_queriers(basic_queriers):
    t = basic_queriers.q_true
    assert t.name == 'Always True Querier'
    assert t.query(use_cache=True) == 1


def test_querier_attached_to_object(attached_querier):
    obj = attached_querier.obj
    q = attached_querier.q

    obj['value'] = False
    assert q.query(use_cache=False) == False

    obj['value'] = True
    assert q.query() == False
    assert q.query(use_cache=False) == True
     
    obj['value'] = False
    q.clear()
    assert q.query() == False


def test_canonical_name(basic_queriers, basic_states):
    assert basic_states.s_true.canonical_name == 'always_true_state'
    assert basic_states.s_weird_name.canonical_name == 'a__state_name___a_'
