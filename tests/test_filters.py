# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard Library
from datetime import (
    date,
    datetime,
    time,
)

# External Libraries
import pytest

# Project Library
from querybuilder.constants import Operator
from querybuilder.filters import (
    BooleanFilter,
    DateFilter,
    DateTimeFilter,
    DoubleFilter,
    IntegerFilter,
    NumericFilter,
    StringFilter,
    TimeFilter,
)
from tests import fixture


class BaseFilter(object):
    """
    Each filter is run through these tests with the fixtures provided in their own subclasses.

    The fixtures are by operator type (unary, binary, ternary, collection, string).

    If a filter does not handle an operator the test will be marked as skipped.

    Expectation values are calculated based on python's built in comparisons.
    """

    # Dummy fixtures, these need to be overridden when appropriate in subclasses
    unary_comparison_scenario = fixture(None, not None, autoparam=True)
    binary_comparison_scenario = fixture(None, autoparam=True)
    ternary_comparison_scenario = fixture(None, autoparam=True)
    collection_scenario = fixture(None, autoparam=True)
    strings_scenario = fixture(None, autoparam=True)

    @fixture()
    def Filter(self):
        return self.FILTER()

    @fixture(autouse=True)
    def skip_if_not_applicable(self, request):
        # this filter will skip the test if the filter doesn't respond to the operator being tested
        op_name = request.node.originalname[len('test_Operators_'):].upper()
        op = getattr(Operator, op_name)
        if op not in self.FILTER.OPERATORS:
            pytest.skip('{} does not respond to {}'.format(self.FILTER, op))

    ###########################################################################
    # unary comp
    def test_Operators_is_null(self, Filter, unary_comparison_scenario):
        op = unary_comparison_scenario

        expects = (op is None)
        assert Filter.is_null(op) == expects, '({op} is None)'.format(**locals())

    def test_Operators_is_not_null(self, Filter, unary_comparison_scenario):
        op = unary_comparison_scenario

        expects = (op is not None)
        assert Filter.is_not_null(op) == expects, '({op} is not None)'.format(**locals())

    ###########################################################################
    # binary comp
    def test_Operators_equal(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop == rop)
        assert Filter.equal(lop, rop) == expects, '({lop} == {rop})'.format(**locals())

    def test_Operators_not_equal(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop != rop)
        assert Filter.not_equal(lop, rop) == expects, '({lop} != {rop})'.format(**locals())

    def Operator_less(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop < rop)
        assert Filter.less(lop, rop) == expects, '({lop} < {rop})'.format(**locals())

    def test_Operators_less_or_equal(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop <= rop)
        assert Filter.less_or_equal(lop, rop) == expects, '({lop} <= {rop})'.format(**locals())

    def test_Operators_greater(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop > rop)
        assert Filter.greater(lop, rop) == expects, '({lop} > {rop})'.format(**locals())

    def test_Operators_greater_or_equal(self, Filter, binary_comparison_scenario):
        lop, rop = binary_comparison_scenario

        expects = (lop >= rop)
        assert Filter.greater_or_equal(lop, rop) == expects, '({lop} >= {rop})'.format(**locals())

    ###########################################################################
    # ternary comp
    def test_Operators_between(self, Filter, ternary_comparison_scenario):
        op, minop, maxop = ternary_comparison_scenario

        expects = (minop <= op <= maxop)
        assert Filter.between(op, minop, maxop) == expects, '({minop} <= {op} <= {maxop})'.format(**locals())

    def test_Operators_not_between(self, Filter, ternary_comparison_scenario):
        op, minop, maxop = ternary_comparison_scenario

        expects = not (minop <= op <= maxop)
        assert Filter.not_between(op, minop, maxop) == expects, 'not ({minop} <= {op} <= {maxop})'.format(**locals())

    ###########################################################################
    # collections
    def test_Operators_in(self, Filter, collection_scenario):
        lop, rop = collection_scenario

        expects = (lop in rop)
        assert Filter._in(lop, rop) == expects, '({lop} in {rop})'.format(**locals())

    def test_Operators_not_in(self, Filter, collection_scenario):
        lop, rop = collection_scenario

        expects = (lop not in rop)
        assert Filter.not_in(lop, rop) == expects, '({lop} not in {rop})'.format(**locals())

    def test_Operators_contains(self, Filter, collection_scenario):
        lop, rop = collection_scenario

        expects = (lop in rop)
        assert Filter.contains(lop, rop) == expects, '({lop} in {rop})'.format(**locals())

    def test_Operators_not_contains(self, Filter, collection_scenario):
        lop, rop = collection_scenario

        expects = (lop not in rop)
        assert Filter.not_contains(lop, rop) == expects, '({lop} not in {rop})'.format(**locals())

    def test_Operators_is_empty(self, Filter, collection_scenario):
        op = collection_scenario

        expects = (len(op) == 0)
        assert Filter.is_empty(op) == expects, '(len({op}) == 0)'.format(**locals())

    def test_Operators_is_not_empty(self, Filter, collection_scenario):
        op = collection_scenario

        expects = (len(op) >= 0)
        assert Filter.is_not_empty(op) == expects, '(len({op}) >= 0)'.format(**locals())

    ###########################################################################
    # strings
    def test_Operators_ends_with(self, Filter, strings_scenario):
        lop, rop = strings_scenario

        expects = (lop.endswith(rop))
        assert Filter.ends_with(lop, rop) == expects, '({lop}.endswith({rop}))'.format(**locals())

    def test_Operators_not_ends_with(self, Filter, strings_scenario):
        lop, rop = strings_scenario

        expects = (not lop.endswith(rop))
        assert Filter.not_ends_with(lop, rop) == expects, '(not {lop}.endswith({rop}))'.format(**locals())

    def test_Operators_begins_with(self, Filter, strings_scenario):
        lop, rop = strings_scenario

        expects = (lop.startswith(rop))
        assert Filter.begins_with(lop, rop) == expects, '({lop}.startswith({rop}))'.format(**locals())

    def test_Operators_not_begins_with(self, Filter, strings_scenario):
        lop, rop = strings_scenario

        expects = (not lop.startswith(rop))
        assert Filter.not_begins_with(lop, rop) == expects, '(not {lop}.startswith({rop}))'.format(**locals())


class TestBooleanFilter(BaseFilter):
    FILTER = BooleanFilter

    unary_comparison_scenario = fixture(
        True,
        False,
        autoparam=True
    )
    binary_comparison_scenario = fixture(
        (True, False),
        (False, True),
        (True, True),
        (False, False),
        autoparam=True
    )


class TestDoubleFilter(BaseFilter):
    FILTER = DoubleFilter

    unary_comparison_scenario = fixture(
        None,
        not None,
        1,
        10.0,
        autoparam=True,
    )
    binary_comparison_scenario = fixture(
        (1.0, 1),
        (2.0, 2),
        (0.0, 0),
        (-3.0, 10),
        (1.0, 2),
        (3.0, 5),
        (1000000000, 100000000000),
        autoparam=True,
    )
    ternary_comparison_scenario = fixture(
        (1, 1.0, 1),
        (3, 1.0, 5),
        (1, 2.0, 3),
        (1, 2.0, 2),
        (2, 2.0, 3),
        (-1, 0, 1),
        autoparam=True,
    )


class TestIntegerFilter(BaseFilter):
    FILTER = IntegerFilter

    unary_comparison_scenario = fixture(
        None,
        not None,
        10,
        autoparam=True,
    )
    binary_comparison_scenario = fixture(
        (1, 1),
        (2, 2),
        (0, 0),
        (-3, 10),
        (1, 2),
        (3, 5),
        autoparam=True,
    )
    ternary_comparison_scenario = fixture(
        (1, 1, 1),
        (3, 1, 5),
        (1, 2, 3),
        (1, 2, 2),
        (2, 2, 3),
        (-1, 0, 1),
        autoparam=True,
    )


class TestNumericFilter(BaseFilter):
    FILTER = NumericFilter

    unary_comparison_scenario = fixture(
        None,
        not None,
        10,
        autoparam=True,
    )
    binary_comparison_scenario = fixture(
        (1, 1),
        (2, 2),
        (0, 0),
        (-3, 10),
        (1, 2),
        (3, 5),
        autoparam=True,
    )
    ternary_comparison_scenario = fixture(
        (1, 1, 1),
        (3, 1, 5),
        (1, 2, 3),
        (1, 2, 2),
        (2, 2, 3),
        (-1, 0, 1),
        autoparam=True,
    )


class TestStringFilter(BaseFilter):
    FILTER = StringFilter

    unary_comparison_scenario = fixture(
        None,
        not None,
        'hi',
        '',
        autoparam=True
    )
    binary_comparison_scenario = fixture(
        ('a', 'b'),
        ('', ''),
        ('b', 'a'),
        ('a', 'a'),
        autoparam=True
    )
    ternary_comparison_scenario = fixture(
        ('a', 'h', 'z'),
        ('a', 'hiho', 'z'),
        ('a', 'b', 'c'),
        ('a', 'c', 'b'),
        ('b', 'a', 'c'),
        autoparam=True
    )
    collection_scenario = fixture(
        ('a', 'abcd'),
        ('abcd', 'a'),
        autoparam=True
    )
    strings_scenario = fixture(
        ('hello', 'hell'),
        ('hello', 'stuff'),
        autoparam=True
    )


class TestTimeFilter(BaseFilter):
    FILTER = TimeFilter

    t0 = time(0)
    t1 = time(1)
    t2 = time(2)
    t3 = time(3)
    tmax = time.max
    tmin = time.min
    tnow = time()

    unary_comparison_scenario = fixture(
        None,
        not None,
        t1,
        t2,
        t3,
        autoparam=True
    )
    binary_comparison_scenario = fixture(
        (t0, t1),
        (t1, t0),
        (t0, t0),
        (tmax, tmin),
        autoparam=True
    )
    ternary_comparison_scenario = fixture(
        (t0, t2, tnow),
        (t0, t2, tnow),
        (t0, t1, t3),
        (t0, t3, t1),
        (t1, t0, t3),
        (t0, tmin, tmax),
        autoparam=True
    )


class TestDateFilter(BaseFilter):
    FILTER = DateFilter

    t0 = date(2017, 11, 1)
    t1 = date(2017, 11, 2)
    t2 = date(2017, 11, 3)
    t3 = date(2017, 11, 4)
    tnow = date.max
    tmax = date.max
    tmin = date.min

    unary_comparison_scenario = fixture(
        None,
        not None,
        t1,
        t2,
        t3,
        autoparam=True
    )
    binary_comparison_scenario = fixture(
        (t0, t1),
        (t1, t0),
        (t0, t0),
        (tmax, tmin),
        autoparam=True
    )
    ternary_comparison_scenario = fixture(
        (t0, t2, tnow),
        (t0, t2, tnow),
        (t0, t1, t3),
        (t0, t3, t1),
        (t1, t0, t3),
        (t0, tmin, tmax),
        autoparam=True
    )


class TestDateTimeFilter(BaseFilter):
    FILTER = DateTimeFilter

    t0 = datetime(2017, 11, 1)
    t1 = datetime(2017, 11, 2)
    t2 = datetime(2017, 11, 3)
    t3 = datetime(2017, 11, 4)
    tnow = datetime.max
    tmax = datetime.max
    tmin = datetime.min

    unary_comparison_scenario = fixture(
        None,
        not None,
        t1,
        t2,
        t3,
        autoparam=True
    )
    binary_comparison_scenario = fixture(
        (t0, t1),
        (t1, t0),
        (t0, t0),
        (tmax, tmin),
        autoparam=True
    )
    ternary_comparison_scenario = fixture(
        (t0, t2, tnow),
        (t0, t2, tnow),
        (t0, t1, t3),
        (t0, t3, t1),
        (t1, t0, t3),
        (t0, tmin, tmax),
        autoparam=True
    )
