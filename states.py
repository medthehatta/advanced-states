# coding: utf8

from functools import lru_cache
import re
import time


class Querier(object):
    def __init__(self, method, name='Unnamed Querier'):
        self._name = name
        self._method = method
        self.cache = None

    @property
    def name(self):
        return self._name

    def query(self, use_cache=True):
        if not use_cache:
            self.clear()

        if self._cache is not None:
            return self._cache

        result = self._method()
        self._cache = result
        return result

    def clear(self):
        self._cache = None

    def __str__(self):
        return '{0}:\n{1}'.format(self.name, self.query())

    def __repr__(self):
        return '<Querier "{0}">'.format(self.name)


class State(object):
    def __init__(self, *params, **kwargs):
        raise NotImplementedError()

    @staticmethod
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
        return self._name

    @property
    def canonical_name(self):
        if self._canonical_name:
            return self._canonical_name
        else:
            canonical = State.get_canonical_name(self.name)
            self._canonical_name = canonical
            return canonical

    def inspect(self, *params, use_cache=1, **kwargs):
        if not use_cache:
            self.clear_caches()
        return self._inspect(*params, **kwargs)

    def _inspect(self, *params, **kwargs):
        raise NotImplementedError()

    @property
    def children(self):
        raise NotImplementedError()

    @property
    def queriers(self):
        raise NotImplementedError()

    def clear_caches(self):
        for querier in self.queriers:
            querier.clear()

    @staticmethod
    def generate_unique_id():
        return str(time.time())


class FundamentalState(State):
    def __init__(self, name, querier, query_evaluator, canonical_name=None):
        self._name = name
        self.querier = querier
        self.query_evaluator = query_evaluator
        self.canonical_name = canonical_name
        self._id = State.generate_unique_id()

    @property
    @lru_cache()
    def queriers(self):
        return [self.querier]

    @property
    def children(self):
        return []

    def _inspect(self, *params, **kwargs):
        query_result = self.querier.query(*params, **kwargs)
        return self.query_evaluator(query_result)

    def pretend(value=True):
        return value

    @property
    def all_children(self):
        return self.children


class CompositeState(State):
    def __init__(self):
        raise NotImplementedError()

    def _inspect(self, *params, **kwargs):
        raise NotImplementedError()

    @property
    def children(self):
        return self._children

    @property
    @lru_cache()
    def queriers(self):
        all_queriers = (child.queriers for child in self.children)
        return list(set(all_queriers))

    @property
    @lru_cache()
    def all_children(self):
        list(set(child.all_children for child in self.children))


class StateNegation(CompositeState):
    def __init__(self, of, name=None):
        if isinstance(of, list):
            self._children = of
        else:
            self._children = [of]

        if name:
            self._name = name
        else:
            self._name = 'NOT ' + of.name

        self.target = of
        self._id = State.generate_unique_id()

    def _inspect(self, *params, **kwargs):
        return not self.target.inspect(*params, **kwargs)


class StateDisjunction(CompositeState):
    def __init__(self, of, name=None):
        if name:
            self._name = name
        else:
            self._name = StateDisjunction._auto_name(of)

        self._children = of
        self._id = State.generate_unique_id()

    def _inspect(self, *params, **kwargs):
        return any(child.inspect(*params, **kwargs) for child in self.children)

    @staticmethod
    def _auto_name(of):
        return ' or '.join([child.name for child in of])


class StateConjunction(CompositeState):
    def __init__(self, of, name=None):
        if name:
            self._name = name
        else:
            self._name = StateConjunction._auto_name(of)

        self._children = of
        self._id = State.generate_unique_id()

    def _inspect(self, *params, **kwargs):
        return all(child.inspect(*params, **kwargs) for child in self.children)

    @staticmethod
    def _auto_name(of):
        return ' and '.join([child.name for child in of])
