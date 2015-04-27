# coding: utf8


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
        return "{0}:\n{1}".format(self.name(), self.query())

    def __repr__(self):
        return "<Querier '{0}'>".format(self.name())


class State(object):
    pass


class FundamentalState(State):
    pass


class CompositeState(State):
    pass


class StateNegation(CompositeState):
    pass


class StateDisjunction(CompositeState):
    pass


class StateConjunction(CompositeState):
    pass
