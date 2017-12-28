from __future__ import absolute_import

# External Libraries
from datetime import date, time, datetime

import six
from cached_property import cached_property

# Project Library
from decimal import Decimal
from querybuilder.constants import (
    Inputs,
    Operators,
    Types,
)
from querybuilder.core import ToDictMixin


class Filters(object):

    def run_filter_for_rule(self, rule):
        '''
        Run the rule using the current instance of a Filters class

        Args:
            rule (Rule): the rule to run. This will be a 'leaf' rule without a condition or further rules to run

        Returns (bool):
            the result of the operator handler when run on the values in the rule.

        '''
        # return a boolean if the one rule is satisfied

        # get the filter for the id specified in the rule
        filter = Filter._filter_registry[rule.id]

        # get the value set in the rule
        rule_operand = filter.python_value(rule.value)

        # get the value returned in the filter instance
        filter_operand = filter.func(self)

        # get the operator we are going to test with
        operator_handler = filter.handler_for_operator(rule.operator)

        if isinstance(rule_operand, (list, tuple)):
            # allow for syntax like def between(self, value, upper, lower)
            return operator_handler(filter, filter_operand, *rule_operand), filter_operand
        else:
            return operator_handler(filter, filter_operand, rule_operand), filter_operand


class FilterMeta(type):
    '''
    Metaclass for the filter

    This does simple registration of operators based on Operator.handles
    '''
    def __new__(metacls, name, bases, attrs):
        cls = super(FilterMeta, metacls).__new__(metacls, name, bases, attrs)

        for name, attr in attrs.items():

            if hasattr(attr, 'operator'):
                # check for for the `operator` attribute that is set in Operator.handles
                cls._operator_handlers[attr.operator] = attr

        return cls


class Filter(six.with_metaclass(FilterMeta, ToDictMixin)):
    '''
    Corresponds to the Filter jQQB object.

    Filters define the possible contents for a rule. This includes
        - the human readable name
        - help information
        - what is the data type we are working with
        - what are the validation criteria (also see the Validation class)
        - if there are default values
        - if the input is limited to a set of choices
        - etc.

    For detailed information see the project website.

        http://querybuilder.js.org/#filters

    '''

    # top level registry of all the filters that exist by id
    _filter_registry = {}

    # per-filter class map of operator -> function
    _operator_handlers = {}

    DICT_KEYS = ('id', 'type', 'field', 'label', 'description', 'optgroup', 'input', 'values', 'value_separator', 'default_value', 'input_event', 'size', 'rows', 'multiple', 'placeholder', 'vertical', 'validation', 'operators', 'plugin', 'plugin_config', 'data', 'valueSetter', 'valueGetter')

    TO_PYTHON = None

    def __init__(
        self,
        id=None,
        field=None,
        label=None,
        description=None,
        type=None,
        optgroup=None,
        input=None,
        values=(),
        value_separator=None,
        default_value=None,
        input_event=None,
        size=None,
        rows=None,
        multiple=None,
        placeholder=None,
        vertical=None,
        validation=None,
        operators=(),
        plugin=None,
        plugin_config=None,
        data=None,
        valueSetter=None,
        valueGetter=None,
    ):
        '''

        Args:
            id (str):
                Unique identifier of the filter.
                By default this is the name of the function it is decorating.
            field (str): ??? understand this better
                Field used by the filter, multiple filters can use the same field.
            label (str):
                Label used to display the filter. It can be simple string or a map for localization.
            description (str):
                Detailed description for display as help text.
            type (str or Types):
                Type of the field. Available types are in `Types`
            optgroup (str):
                Group name to group this filter with
            input (str or Inputs):
                Type of input used. Available inputs are in `Inputs`
            values ([Values]):
                Required for `radio` and `checkbox` inputs. Generally needed for select inputs.
            value_separator (str):
                Used the split and join the value when a text input is used with an operator allowing multiple values (between for example).
            default_value:
                The default value.
            validation ([Validation]):
                Object of options for rule validation. See the `Validation` class.
            operators ([Operators)]):
                Array of operators types to use for this filter. If empty the filter will use all applicable operators.
            data (dict):
                Additional data not used by QueryBuilder but that will be added to the output rules object. Use this to store any functional data you need.

        Args with only front end uses:
            input_event:
                Space separated list of DOM events which the builder should listen to detect value changes.
            plugin:
                Name of a jQuery plugin to apply on the input.
            plugin_config:
                Object of parameters to pass to the plugin.
            valueSetter:
                Function used to set the input(s) value. If provided the default function is not run. It takes 2 parameters: rule, value
            valueGetter:
                Function used to get the input(s) value. If provided the default function is not run. It takes 1 parameter: rule

            Only for text and textarea inputs:
                size: horizontal size of the input.
                rows: vertical size of the input.
                placeholder: placeholder to display inside the input.

            Only for select inputs:
                multiple: accept multiple values.

            Only for radio and checkbox inputs:
                vertical: display inputs vertically on not horizontally.

        '''
        self.id = id
        self.type = Types(type) if type else type
        self.field = field
        self.label = label
        self.description = description
        self.optgroup = optgroup
        self.input = Inputs(input) if input else input

        self.values = values
        if self.input in (Inputs.CHECKBOX, Inputs.RADIO) and not self.values:
            raise ValueError('values are required when using input %s' % self.input)

        self.value_separator = value_separator
        self.default_value = default_value
        self.input_event = input_event
        self.size = size
        self.rows = rows
        self.multiple = multiple
        self.placeholder = placeholder
        self.vertical = vertical
        self.validation = validation

        self.operators = [Operators(op) for op in operators]  # cast strings to operator, this also validates
        self.plugin = plugin
        self.plugin_config = plugin_config
        self.data = data
        self.valueSetter = valueSetter
        self.valueGetter = valueGetter

        self.func = None

    def __call__(self, func):
        self.func = func

        # set the id, label, etc
        self.id = self.id or func.__name__

        Filter._filter_registry[self.id] = self

        return cached_property(func)

    @classmethod
    def all_filters(cls):
        '''returns all the available filters in the registry'''
        return [
            filter.to_dict()
            for filter
            in cls._filter_registry.values()
        ]

    @classmethod
    def handler_for_operator(cls, operator):
        return cls._operator_handlers.get(operator) or Filter._operator_handlers[operator]

    # how to convert a rule's type to a python type
    _python_types = {
        Types.STRING: str,  # TODO validate these converters
        Types.INTEGER: int,  # TODO validate these converters
        Types.DOUBLE: Decimal,  # TODO validate these converters
        Types.DATE: date,  # TODO validate these converters
        Types.TIME: time,  # TODO validate these converters
        Types.DATETIME: datetime,  # TODO validate these converters
        Types.BOOLEAN: lambda x: bool(int(x) if x.isdigit() else (1 if x == 'true' else 0))
    }

    def python_value(self, filter_value):
        '''Convert the json representation of a value to python'''
        if filter_value is None:
            # when value is None it is intentional and shouldn't be mapped
            return None
        else:
            # lookup the converter in the python_types dict
            return self._python_types[self.type](filter_value)

    @classmethod
    def filter_value(cls, python_value):
        '''Convert the python representation of a value to one which is filter and json compatible'''
        return python_value

    ###########################################################################
    # Default handlers for operators
    @Operators.EQUAL.handles
    def equal(self, lop, rop):
        return lop == rop

    @Operators.NOT_EQUAL.handles
    def not_equal(self, lop, rop):
        return not self.equal(lop, rop)

    @Operators.IN.handles
    def _in(self, lop, rop):
        return lop in rop

    @Operators.NOT_IN.handles
    def not_in(self, lop, rop):
        return not self._in(lop, rop)

    @Operators.LESS.handles
    def less(self, lop, rop):
        return lop < rop

    @Operators.LESS_OR_EQUAL.handles
    def less_or_equal(self, lop, rop):
        return self.less(lop, rop) or self.equal(lop, rop)

    @Operators.GREATER.handles
    def greater(self, lop, rop):
        return not self.less_or_equal(lop, rop)

    @Operators.GREATER_OR_EQUAL.handles
    def greater_or_equal(self, lop, rop):
        return self.greater(lop, rop) or self.equal(lop, rop)

    @Operators.BETWEEN.handles
    def between(self, op, minop, maxop):
        '''
        minop <= op <= maxop
        '''
        return self.less_or_equal(minop, op) and self.less_or_equal(op, maxop)

    @Operators.NOT_BETWEEN.handles
    def not_between(self, op, minop, maxop):
        return not self.between(op, minop, maxop)

    @Operators.CONTAINS.handles
    def contains(self, lop, rop):
        return self._in(lop, rop)

    @Operators.IS_NULL.handles
    def is_null(self, op):
        return op is None

    @Operators.IS_NOT_NULL.handles
    def is_not_null(self, op):
        return not self.is_null(op)


class TypedFilter(Filter):
    TYPE = NotImplemented
    OPERATORS = NotImplemented
    OPTIONS = NotImplemented

    def __init__(self, *args, **kwargs):
        kwargs.update(type=self.TYPE)
        assert self.TYPE is not NotImplemented, 'TYPE must be declared in the subclass'

        if self.OPERATORS is not NotImplemented:
            kwargs.setdefault('operators', tuple(self.OPERATORS))

        if self.OPTIONS is not NotImplemented:
            for k, v in self.OPTIONS.items():
                kwargs.setdefault(k, v)

        super(TypedFilter, self).__init__(*args, **kwargs)


class BooleanFilter(TypedFilter):
    TYPE = Types.BOOLEAN

    OPERATORS = [
        Operators.EQUAL,
        Operators.NOT_EQUAL,
        Operators.IS_NULL,
        Operators.IS_NOT_NULL,
    ]

    OPTIONS = {
        'input': Inputs.RADIO,
        'values': ({1: 'Is True'}, {0: 'Is False'}),
    }


class StringFilter(TypedFilter):
    TYPE = Types.STRING

    OPERATORS = (
        Operators.unary_comparisons
        | Operators.binary_comparisons
        | Operators.ternary_comparisons
        | Operators.collection_comparisons
        | Operators.string_comparisons
    )

    @Operators.NOT_CONTAINS.handles
    def not_contains(self, lop, rop):
        return not self.contains(lop, rop)

    @Operators.BEGINS_WITH.handles
    def begins_with(self, lop, rop):
        return lop.startswith(rop)

    @Operators.NOT_BEGINS_WITH.handles
    def not_begins_with(self, lop, rop):
        return not lop.startswith(rop)

    @Operators.ENDS_WITH.handles
    def ends_with(self, lop, rop):
        return lop.endswith(rop)

    @Operators.NOT_ENDS_WITH.handles
    def not_ends_with(self, lop, rop):
        return not lop.endswith(rop)

    @Operators.IS_EMPTY.handles
    def is_empty(self, op):
        return len(op) == 0

    @Operators.IS_NOT_EMPTY.handles
    def is_not_empty(self, op):
        return not self.is_empty(op)


class IntegerFilter(TypedFilter):
    TYPE = Types.INTEGER

    OPERATORS = (
        Operators.unary_comparisons
        | Operators.binary_comparisons
        | Operators.ternary_comparisons
    )


class DoubleFilter(IntegerFilter):
    # this isn't a thing in python, but whatever
    TYPE = Types.DOUBLE


# alias Numeric to Double, these are the same concept in python
NumericFilter = DoubleFilter


class DateFilter(TypedFilter):
    TYPE = Types.DATE

    OPERATORS = (
        Operators.unary_comparisons
        | Operators.binary_comparisons
        | Operators.ternary_comparisons
    )

    # TODO add default validator


class TimeFilter(TypedFilter):
    TYPE = Types.TIME

    OPERATORS = (
        Operators.unary_comparisons
        | Operators.binary_comparisons
        | Operators.ternary_comparisons
    )
    # TODO add default validator


class DateTimeFilter(TypedFilter):
    TYPE = Types.DATETIME

    OPERATORS = (
        Operators.unary_comparisons
        | Operators.binary_comparisons
        | Operators.ternary_comparisons
    )

    # TODO add default validator


__all__ = [_.__name__ for _ in globals().values() if isinstance(_, (Filter, Filters))]
