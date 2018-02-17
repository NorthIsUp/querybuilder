from enum import Enum


class Condition(str, Enum):
    '''
    The available ways to do boolean combinations.
    '''
    # TODO make enums expandable when using plugins
    # TODO: expand with XOR

    AND = 'AND'
    OR = 'OR'


class Input(str, Enum):
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


class Type(str, Enum):
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


class Operator(str, Enum):
    '''
    Operator supported by default in jQQB
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

Operator.unary_comparisons = frozenset({
    Operator.IS_NULL,
    Operator.IS_NOT_NULL
})

Operator.binary_comparisons = frozenset({
    Operator.EQUAL,
    Operator.NOT_EQUAL,
    Operator.LESS,
    Operator.LESS_OR_EQUAL,
    Operator.GREATER,
    Operator.GREATER_OR_EQUAL,
})

Operator.ternary_comparisons = frozenset({
    Operator.BETWEEN,
    Operator.NOT_BETWEEN,
})

Operator.string_comparisons = frozenset({
    Operator.BEGINS_WITH,
    Operator.NOT_BEGINS_WITH,
    Operator.ENDS_WITH,
    Operator.NOT_ENDS_WITH,
})

Operator.collection_comparisons = frozenset({
    Operator.IN,
    Operator.NOT_IN,
    Operator.IS_EMPTY,
    Operator.IS_NOT_EMPTY,
    Operator.CONTAINS,
    Operator.NOT_CONTAINS,
})
