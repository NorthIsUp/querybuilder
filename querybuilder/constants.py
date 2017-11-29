from enum import Enum


class Conditions(str, Enum):
    '''
    The available ways to do boolean combinations.
    '''
    # TODO make enums expandable when using plugins
    # TODO: expand with XOR

    AND = 'AND'
    OR = 'OR'


class Inputs(str, Enum):
    '''
    The types of input widgets available to the jQQB library.
    '''
    # TODO make enums expandable when using plugins

    TEXT = 'text'
    NUMBER = 'number'
    TEXTAREA = 'textarea'
    RADIO = 'radio'
    CHECKBOX = 'checkbox'
    SELECT = 'select'


class Types(str, Enum):
    '''
    The types that a filter value can be
    '''
    # TODO make enums expandable when using plugins

    STRING = 'string'
    INTEGER = 'integer'
    DOUBLE = 'double'
    DATE = 'date'
    TIME = 'time'
    DATETIME = 'datetime'
    BOOLEAN = 'boolean'


class Operators(str, Enum):
    '''
    Operators supported by default in jQQB
    '''
    # TODO make enums expandable when using plugins

    # unary comparison
    IS_NULL = 'is_null'
    IS_NOT_NULL = 'is_not_null'

    # binary comparison
    EQUAL = 'equal'
    NOT_EQUAL = 'not_equal'
    LESS = 'less'
    LESS_OR_EQUAL = 'less_or_equal'
    GREATER = 'greater'
    GREATER_OR_EQUAL = 'greater_or_equal'

    # ternary comparison
    BETWEEN = 'between'
    NOT_BETWEEN = 'not_between'

    # strings
    BEGINS_WITH = 'begins_with'
    NOT_BEGINS_WITH = 'not_begins_with'
    ENDS_WITH = 'ends_with'
    NOT_ENDS_WITH = 'not_ends_with'

    # collections
    IN = 'in'
    NOT_IN = 'not_in'
    IS_EMPTY = 'is_empty'
    IS_NOT_EMPTY = 'is_not_empty'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'

    def handles(self, f):
        '''
        Decorator to mark a function as a handler for an operator
        '''
        f.operator = self
        return f

Operators.unary_comparisons = frozenset({
    Operators.IS_NULL,
    Operators.IS_NOT_NULL
})

Operators.binary_comparisons = frozenset({
    Operators.EQUAL,
    Operators.NOT_EQUAL,
    Operators.LESS,
    Operators.LESS_OR_EQUAL,
    Operators.GREATER,
    Operators.GREATER_OR_EQUAL,
})

Operators.ternary_comparisons = frozenset({
    Operators.BETWEEN,
    Operators.NOT_BETWEEN,
})

Operators.string_comparisons = frozenset({
    Operators.BEGINS_WITH,
    Operators.NOT_BEGINS_WITH,
    Operators.ENDS_WITH,
    Operators.NOT_ENDS_WITH,
})

Operators.collection_comparisons = frozenset({
    Operators.IN,
    Operators.NOT_IN,
    Operators.IS_EMPTY,
    Operators.IS_NOT_EMPTY,
    Operators.CONTAINS,
    Operators.NOT_CONTAINS,
})
