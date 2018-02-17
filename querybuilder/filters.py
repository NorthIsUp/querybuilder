from __future__ import absolute_import

# Standard Library
import re
from datetime import (
    date,
    datetime,
    time,
)
from decimal import (
    Context,
    Decimal,
)

# External Libraries
import six
from cached_property import cached_property

# Project Library
from querybuilder.constants import (
    Input,
    Operator,
    Type,
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

        # get the value returned in the filter instance
        filter_operand = filter.func(self)

        # check that the value is within the filter constraints
        if not filter.validate(filter_operand):
            return False, filter_operand

        # get the value set in the rule
        rule_operand = filter.python_value(rule.value)

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

    _validation_functions = frozenset()

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
            type (str or Type):
                Type of the field. Available types are in `Type`
            optgroup (str):
                Group name to group this filter with
            input (str or Input):
                Type of input used. Available inputs are in `Inputs`
            values ([Values]):
                Required for `radio` and `checkbox` inputs. Generally needed for select inputs.
            value_separator (str):
                Used the split and join the value when a text input is used with an operator allowing multiple values (between for example).
            default_value:
                The default value.
            validation ([Validation]):
                Object of options for rule validation. See the `Validation` class.
            operators ([Operator)]):
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
        self.type = Type(type) if type else type
        self.field = field
        self.label = label
        self.description = description
        self.optgroup = optgroup
        self.input = Input(input) if input else input

        self.values = values
        if self.input in (Input.CHECKBOX, Input.RADIO) and not self.values:
            raise ValueError('values are required when using input %s' % self.input)

        self.value_separator = value_separator
        self.default_value = default_value
        self.input_event = input_event
        self.size = size
        self.rows = rows
        self.multiple = multiple
        self.placeholder = placeholder
        self.vertical = vertical
        self.validation = dict(validation or {})  # ensure validation is a dict

        self.operators = [Operator(op) for op in operators]  # cast strings to operator, this also validates
        self.plugin = plugin
        self.plugin_config = plugin_config
        self.data = data
        self.valueSetter = valueSetter
        self.valueGetter = valueGetter

        self.func = None

        self._validation_functions = frozenset(
            getattr(self, func_name)
            for func_name in dir(self)
            if func_name.startswith('validate_') and callable(getattr(self, func_name))
        )

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
        Type.STRING: str,  # TODO validate these converters
        Type.INTEGER: int,  # TODO validate these converters
        Type.DOUBLE: Decimal,  # TODO validate these converters
        Type.DATE: date,  # TODO validate these converters
        Type.TIME: time,  # TODO validate these converters
        Type.DATETIME: datetime,  # TODO validate these converters
        Type.BOOLEAN: lambda x: bool(int(x) if x.isdigit() else (1 if x == 'true' else 0))
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

    def validate(self, value):
        if self._validation_functions:
            return all(
                f(value) is not False  # value must be false, not just falsy
                for f in self._validation_functions
            )

        return True

    ###########################################################################
    # Default handlers for operators
    @Operator.EQUAL.handles
    def equal(self, lop, rop):
        return lop == rop

    @Operator.NOT_EQUAL.handles
    def not_equal(self, lop, rop):
        return not self.equal(lop, rop)

    @Operator.IN.handles
    def _in(self, lop, rop):
        return lop in rop

    @Operator.NOT_IN.handles
    def not_in(self, lop, rop):
        return not self._in(lop, rop)

    @Operator.LESS.handles
    def less(self, lop, rop):
        return lop < rop

    @Operator.LESS_OR_EQUAL.handles
    def less_or_equal(self, lop, rop):
        return self.less(lop, rop) or self.equal(lop, rop)

    @Operator.GREATER.handles
    def greater(self, lop, rop):
        return not self.less_or_equal(lop, rop)

    @Operator.GREATER_OR_EQUAL.handles
    def greater_or_equal(self, lop, rop):
        return self.greater(lop, rop) or self.equal(lop, rop)

    @Operator.BETWEEN.handles
    def between(self, op, minop, maxop):
        '''
        minop <= op <= maxop
        '''
        return self.less_or_equal(minop, op) and self.less_or_equal(op, maxop)

    @Operator.NOT_BETWEEN.handles
    def not_between(self, op, minop, maxop):
        return not self.between(op, minop, maxop)

    @Operator.CONTAINS.handles
    def contains(self, lop, rop):
        return self._in(lop, rop)

    @Operator.IS_NULL.handles
    def is_null(self, op):
        return op is None

    @Operator.IS_NOT_NULL.handles
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
    TYPE = Type.BOOLEAN

    OPERATORS = [
        Operator.EQUAL,
        Operator.NOT_EQUAL,
        Operator.IS_NULL,
        Operator.IS_NOT_NULL,
    ]

    OPTIONS = {
        'input': Input.RADIO,
        'values': ({1: 'Is True'}, {0: 'Is False'}),
    }


class StringFilter(TypedFilter):
    TYPE = Type.STRING

    OPERATORS = (
        Operator.unary_comparisons
        | Operator.binary_comparisons
        | Operator.ternary_comparisons
        | Operator.collection_comparisons
        | Operator.string_comparisons
    )

    @cached_property
    def validation_format(self):
        fmt = self.validation.get('format')
        if fmt is not None:
            if fmt.startswith('/') and fmt.endswith('/'):
                fmt = fmt[1:-1]
            return re.compile(fmt)

    def validate_format(self, value):
        if self.validation_format is not None:
            return bool(self.validation_format.match(value))

    ###########################################################################
    # Default handlers for operators
    @Operator.NOT_CONTAINS.handles
    def not_contains(self, lop, rop):
        return not self.contains(lop, rop)

    @Operator.BEGINS_WITH.handles
    def begins_with(self, lop, rop):
        return lop.startswith(rop)

    @Operator.NOT_BEGINS_WITH.handles
    def not_begins_with(self, lop, rop):
        return not lop.startswith(rop)

    @Operator.ENDS_WITH.handles
    def ends_with(self, lop, rop):
        return lop.endswith(rop)

    @Operator.NOT_ENDS_WITH.handles
    def not_ends_with(self, lop, rop):
        return not lop.endswith(rop)

    @Operator.IS_EMPTY.handles
    def is_empty(self, op):
        return len(op) == 0

    @Operator.IS_NOT_EMPTY.handles
    def is_not_empty(self, op):
        return not self.is_empty(op)


class IntegerFilter(TypedFilter):
    TYPE = Type.INTEGER

    OPERATORS = (
        Operator.unary_comparisons
        | Operator.binary_comparisons
        | Operator.ternary_comparisons
    )

    def validate_min(self, value):
        min = self.validation.get('min')
        if min is not None:
            return value >= Decimal(str(min))

    def validate_max(self, value):
        max = self.validation.get('max')
        if max is not None:
            return value <= Decimal(str(max))

    def validate_step(self, value, _divmod=Context().divmod):
        step = self.validation.get('step')
        if step is not None:
            _, remainder = _divmod(Decimal(str(value)), Decimal(str(step)))
            return remainder == 0


class DoubleFilter(IntegerFilter):
    # this isn't a thing in python, but whatever
    TYPE = Type.DOUBLE


# alias Numeric to Double, these are the same concept in python
NumericFilter = DoubleFilter


class DateFilter(TypedFilter):
    TYPE = Type.DATE

    OPERATORS = (
        Operator.unary_comparisons
        | Operator.binary_comparisons
        | Operator.ternary_comparisons
    )

    # TODO add default validator


class TimeFilter(TypedFilter):
    TYPE = Type.TIME

    OPERATORS = (
        Operator.unary_comparisons
        | Operator.binary_comparisons
        | Operator.ternary_comparisons
    )
    # TODO add default validator


class DateTimeFilter(TypedFilter):
    TYPE = Type.DATETIME

    OPERATORS = (
        Operator.unary_comparisons
        | Operator.binary_comparisons
        | Operator.ternary_comparisons
    )

    # TODO add default validator


__all__ = [_.__name__ for _ in globals().values() if isinstance(_, (Filter, Filters))]
