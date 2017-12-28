# -*- coding: utf-8 -*-

from __future__ import absolute_import

# Standard Library
from collections import namedtuple

# Project Library
from querybuilder import filters
from querybuilder.rules import Rule
from tests import fixture


Item = namedtuple('Item', 'name,category,in_stock,price,id')


class SomeFilters(filters.Filters):

    def __init__(self, item):
        self.item = item

    @filters.StringFilter(
        id='name',
        label='Name',
        type='string'
    )
    def name(self):
        return self.item.name

    @filters.StringFilter(
        id='id',
        label='Identifier',
        type='string',
        placeholder='____-____-____',
        operators=['equal', 'not_equal'],
        validation={
            'format': r'/ ^.{4} - .{4} - .{4}$/'
        }
    )
    def id(self):
        return self.item.id

    @filters.IntegerFilter(
        id='category',
        label='Category',
        type='integer',
        input='select',
        values={
            1: 'Books',
            2: 'Movies',
            3: 'Music',
            4: 'Tools',
            5: 'Goodies',
            6: 'Clothes'
        },
        operators=['equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
    )
    def category(self):
        return self.item.category

    @filters.BooleanFilter(
        id='in_stock',
        label='In stock',
        type='integer',
        input='radio',
        values={
            1: 'Yes',
            0: 'No'
        },
        operators=['equal']
    )
    def in_stock(self):
        return self.item.in_stock

    @filters.NumericFilter(
        id='price',
        label='Price',
        type='double',
        validation={
            'min': 0,
            'step': 0.01
        }
    )
    def price(self):
        return self.item.price


Scenario = namedtuple('Scenario', 'is_valid,item')
scenario = fixture(
    autoparam=True,
    params=(
        Scenario(True, Item(name='hi', category=1, in_stock=True, price=10, id=10)),
        Scenario(True, Item(name='hi', category=1, in_stock=True, price=10.24, id=10)),
        Scenario(True, Item(name='hi', category=1, in_stock=True, price=10.249, id=10)),  # TODO: should be invalid due to rule validation
        Scenario(False, Item(name='hi', category=1, in_stock=True, price=10.25, id=10)),
        Scenario(True, Item(name='hi', category=1, in_stock=True, price=0, id=10)),
        Scenario(False, Item(name='hi', category=1, in_stock=True, price=10.251, id=10)),  # TODO: should be invalid due to rule validation
        Scenario(False, Item(name='hi', category=1, in_stock=True, price=-10, id=10)),
    )
)

def test_a_rule(scenario):
    rule = Rule({
        "condition": "AND",
        "rules": [
            {
                "id": "price",
                "field": "price",
                "type": "double",
                "input": "number",
                "operator": "less",
                "value": "10.25"
            },
            {
                "condition": "OR",
                "rules": [
                    {
                        "id": "category",
                        "field": "category",
                        "type": "integer",
                        "input": "select",
                        "operator": "equal",
                        "value": "2"
                    },
                    {
                        "id": "category",
                        "field": "category",
                        "type": "integer",
                        "input": "select",
                        "operator": "equal",
                        "value": "1"
                    }
                ]
            }
        ],
        "valid": True
    })
    filters = SomeFilters(item=scenario.item)
    assert scenario.is_valid == rule.is_valid(filters, verbose=1)
