# coding: utf8

from functools import lru_cache
import re


class Querier(object):
    def __init__(self, method, name='Unnamed Querier'):
        self.name = name
        self.method = method
        self.cache = None

    @property
    def name(self):
        return self.name

    def query(self, use_cache=True):
        if not use_cache:
            self.clear()

        if self.cache is not None:
            return self.cache

        result = self.method()
        self.cache = result
        return result

    def clear(self):
        self.cache = None

    def __str__(self):
        return '{0}:\n{1}'.format(self.name, self.query())

    def __repr__(self):
        return '<Querier "{0}">'.format(self.name)


class State(object):
    def __init__(self, *params, **kwargs):
        raise NotImplementedError('Override me')

    @classmethod
    def get_canonical_name(name):
        return re.sub(
            r'\ +',
            '_',
            re.sub(
                r'[^\w\ ]+',
                '',
                name.lower()
            ),
        )

    @property
    def name(self):
        return self.name

    @lru_cache
    def canonical_name(self):
        return State.get_canonical_name(self.name)

    def inspect(self, *params, use_cache=1, **kwargs):
        if not use_cache:
            self.clear_caches()
        return self._inspect(*params, **kwargs)

    def _inspect(self, *params, **kwargs):
        raise NotImplementedError('Override me')

    @property
    def children(self):
        raise NotImplementedError('Override me')

    @property
    def queriers(self):
        raise NotImplementedError('Override me')

    def clear_caches(self):
        for querier in self.queriers:
            querier.clear()


class FundamentalState(State):
    def __init__(self, name, querier, query_evaluator, canonical_name=None):
        self.name = name
        self.querier = querier
        self.query_evaluator = query_evaluator
        self.canonical_name = canonical_name

    @property
    @lru_cache
    def queriers(self):
        return [self.querier]

    @property
    @lru_cache
    def children(self):
        return []

    def _inspect(self, *params, **kwargs):
        query_result = self.querier.query(*params, **kwargs)
        return self.query_evaluator(query_result)


class CompositeState(State):
    pass


class StateNegation(CompositeState):
    pass


class StateDisjunction(CompositeState):
    pass


class StateConjunction(CompositeState):
    pass
