# -*- coding: utf-8 -*-
from __future__ import (
    absolute_import,
    print_function,
)

# Standard Library
import json
from logging import getLogger

# Project Library
from querybuilder.constants import (
    Conditions,
    Inputs,
    Operators,
    Types,
)
from querybuilder.core import ToDictMixin

logger = getLogger(__name__)

__all__ = ()


class Validation(ToDictMixin):
    '''
    Represents the Validation object for jQQB

    This allows you to specify validation requirements for the front end including
        - min and max values for numbers
        - regular expressions for strings
        - error messages
        - is empty an acceptable input

    '''
    DICT_KEYS = ('format', 'min', 'max', 'step', 'messages', 'allow_empty_value', 'callback')

    def __init__(
        self,
        format=None,
        min=None,
        max=None,
        step=None,
        messages=(),
        allow_empty_value=None,
        callback=None,
    ):
        self.format = format
        self.min = min
        self.max = max
        self.step = step
        self.messages = messages
        self.allow_empty_value = allow_empty_value
        self.callback = callback

    def validate(self, value):
        '''Run the validation criteria against a value'''
        if self.min is not None:
            assert value >= self.min, self.messages
        if self.max is not None:
            assert value <= self.max, self.messages
        if self.step is not None:
            # TODO validate that numeric is evenly divisible by step
            pass
        if self.format is not None:
            # assert re.match(self.format, value)
            # TODO run validation on regular expressions
            pass


class Rule(object):
    def __init__(self, rule):
        '''
        Args:
            rule: The rule object
            operators: Enum of operators, this allows for adding custom operators
            inputs: Enum of inputs, this allows for adding custom inputs
            types: Enum of types, this allows for adding custom types
        '''

        self.is_group = False
        self.is_empty = False  # note that an empty rule evaluates as true

        if rule.get('empty'):
            # some rules
            self.is_empty = True
        elif 'condition' and 'rules' in rule:
            self.is_group = True
            self.condition = Conditions(rule['condition'])
            self.rules = [Rule(rule) for rule in rule['rules']]
        else:
            self.id = rule['id']
            self.field = rule['field']
            self.input = Inputs(rule['input'])
            self.operator = Operators(rule['operator'])
            self.type = Types(rule['type'])
            self.value = rule['value']

    def __repr__(self, value=None):
        parens = '()' if value is None else '({})'.format(value)
        if self.is_group:
            return ('(' + ' {s.condition} '.join(repr(r) for r in self.rules) + ')').format(s=self)
        elif self.is_empty:
            return 'Rule{p}'.format(p=parens)
        else:
            return 'Rule({s.id}{p} {s.operator} {s.value})'.format(s=self, p=parens)

    @classmethod
    def loads(cls, string, ensure_list=False):
        '''Returns rule objects from json, supports both a single rule or list of rules'''
        rule = json.loads(string)

        if isinstance(rule, (list, tuple)):
            return [cls(rule) for rule in rule]
        else:
            result = cls(rule)
            return [result] if ensure_list else result

    # how to convert a rule's condition to a python type
    python_conditions = {
        Conditions.AND: all,
        Conditions.OR: any,
    }

    def is_valid(self, filters, indent=0, verbose=False):
        '''
        Traverse all the rules and return the result as lazily as possible

        Args:
            filters: An instance of a sublclass of Filters
            indent: information to pretty print log results
            verbose: printing the rule output is often useful, this is a quick way to enable logging for just this function
        '''
        pad = ' ' * indent
        if self.is_group:
            # recurse and call is_valid for each rule in the list

            log_args = '%s%s', pad, self.python_conditions[self.condition].__name__
            print(log_args[0] % log_args[1:]) if verbose else logger.debug(*log_args)

            return self.python_conditions[self.condition](
                rule.is_valid(filters, indent=indent + 2, verbose=verbose) for rule in self.rules
            )
        elif self.is_empty:
            return True
        else:
            result, filter_operand = filters.run_filter_for_rule(self)

            log_args = '%s%s == %s', pad, self.__repr__(value=filter_operand), result
            print(log_args[0] % log_args[1:]) if verbose else logger.debug(*log_args)

            return result
