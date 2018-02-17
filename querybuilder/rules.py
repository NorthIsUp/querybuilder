# -*- coding: utf-8 -*-
from __future__ import absolute_import

# Standard Library
import json
from logging import getLogger

# Project Library
import sys

from querybuilder.constants import (
    Condition,
    Input,
    Operator,
    Type,
)
from querybuilder.core import ToDictMixin
from querybuilder.exceptions import ValidationError

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
    rule_fields = set(['id', 'field', 'input', 'operator', 'type', 'value'])
    group_fields = set(['condition', 'rules'])

    def __init__(self, rule):
        '''
        Args:
            rule: The rule object
            operators: Enum of operators, this allows for adding custom operators
            inputs: Enum of inputs, this allows for adding custom inputs
            types: Enum of types, this allows for adding custom types
        '''
        if not isinstance(rule, dict):
            raise ValidationError('Rule must be a dictionary')

        self.is_group = False
        self.is_empty = False  # note that an empty rule evaluates as true

        try:
            if rule.get('empty'):
                # some rules
                self.is_empty = True
            elif self.group_fields.issubset(rule):
                self.is_group = True
                self.condition = Condition(rule['condition'])
                if not isinstance(rule['rules'], list):
                    raise ValidationError('\'rules\' must be a list')
                self.rules = [Rule(rule) for rule in rule['rules']]
            elif self.rule_fields.issubset(rule):
                self.id = rule['id']
                self.field = rule['field']
                self.input = Input(rule['input'])
                self.operator = Operator(rule['operator'])
                self.type = Type(rule['type'])
                self.value = rule['value']
            else:
                raise ValidationError('Rule did not contain required fields')
        except ValueError as e:
            raise ValidationError(e.message)

    def __repr__(self, value=None):
        parens = '()' if value is None else '({})'.format(value)
        if self.is_group:
            return ('(' + ' {s.condition} '.join(repr(r) for r in self.rules) + ')').format(s=self)
        elif self.is_empty:
            return 'Rule{p}'.format(p=parens)
        else:
            return 'Rule({s.id}{p} {s.operator} {s.value})'.format(s=self, p=parens)

    def dumps(self):
        """
        Converts the rule to a json string.
        :return: string
        """
        return json.dumps(self.to_dict())

    def to_dict(self):
        converted = {}
        if self.is_empty:
            converted['empty'] = True
        elif self.is_group:
            converted['condition'] = self.condition.value
            converted['rules'] = [rule.to_dict() for rule in self.rules]
        else:
            converted['id'] = self.id
            converted['field'] = self.field
            converted['input'] = self.input.value
            converted['operator'] = self.operator.value
            converted['type'] = self.type.value
            converted['value'] = self.value

        return converted

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False

        if not (self.is_empty == other.is_empty and self.is_group == other.is_group):
            return False

        if self.is_empty:
            return True
        elif self.is_group:
            return (
                self.condition == other.condition
                and self.rules == other.rules
            )
        else:
            return (
                self.id == other.id
                and self.field == other.field
                and self.input == other.input
                and self.operator == other.operator
                and self.type == other.type
                and self.value == other.value
            )

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
        Condition.AND: all,
        Condition.OR: any,
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
            sys.stderr.write(log_args[0] % log_args[1:] + '\n') if verbose else logger.debug(*log_args)

            return self.python_conditions[self.condition](
                rule.is_valid(filters, indent=indent + 2, verbose=verbose) for rule in self.rules
            )
        elif self.is_empty:
            return True
        else:
            result, filter_operand = filters.run_filter_for_rule(self)

            log_args = '%s%s == %s', pad, self.__repr__(value=filter_operand), result
            sys.stderr.write(log_args[0] % log_args[1:] + '\n') if verbose else logger.debug(*log_args)

            return result
