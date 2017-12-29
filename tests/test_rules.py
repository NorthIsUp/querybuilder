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
            'format': '/^.{4}-.{4}-.{4}$/'
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


Scenario = namedtuple('Scenario', 'is_valid,rule,item,reason')

_name = 'hello'
_category = 1
_in_stock = True
_not_in_stock = False
_price = 10
_id = 'abcd-1234-de56'

PASS = True
FAIL = False

rule_1 = Rule({
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

rule_2 = Rule({
    "condition": "AND",
    "rules": [
        {
            "condition": "OR",
            "rules": [
              {
                  "id": "name",
                  "field": "name",
                  "type": "string",
                  "input": "text",
                  "operator": "equal",
                  "value": "henry"
              },
              {
                  "id": "id",
                  "field": "id",
                  "type": "string",
                  "input": "text",
                  "operator": "equal",
                  "value": "1111-1111-1111"
              },
              {
                  "id": "category",
                  "field": "category",
                  "type": "integer",
                  "input": "select",
                  "operator": "equal",
                  "value": "4"
              }
              ]
        },
        {
            "id": "in_stock",
            "field": "in_stock",
            "type": "integer",
            "input": "radio",
            "operator": "equal",
            "value": "1"
        }
    ],
    "valid": True
})

scenario = fixture(
    autoparam=True,
    params=(
        # rule1
        Scenario(PASS, rule_1, Item(_name, _category, _in_stock, _price, _id), 'a-ok'),
        Scenario(PASS, rule_1, Item(_name, _category, _in_stock, 10, _id), 'a-ok'),
        Scenario(PASS, rule_1, Item(_name, _category, _in_stock, 10.24, _id), 'a-ok'),
        Scenario(PASS, rule_1, Item(_name, _category, _in_stock, 0, _id), 'a-ok'),
        Scenario(FAIL, rule_1, Item(_name, _category, _in_stock, 10.25, _id), '10.25 is not < 10.25'),
        Scenario(FAIL, rule_1, Item(_name, _category, _in_stock, 10.249, _id), '10.249 is the wrong step'),
        Scenario(FAIL, rule_1, Item(_name, _category, _in_stock, 10.251, _id), '10.251 is the wrong step'),
        Scenario(FAIL, rule_1, Item(_name, _category, _in_stock, -1, _id), 'price of -1 is below min'),

        # rule2
        Scenario(FAIL, rule_2, Item(_name, _category, _not_in_stock, _price, _id), 'meets no conditions'),

        Scenario(PASS, rule_2, Item(_name, _category, _in_stock, _price, '1111-1111-1111'), 'good id'),
        Scenario(FAIL, rule_2, Item(_name, _category, _not_in_stock, _price, '1111-1111-1111'), 'good id, but not in stock'),
        Scenario(FAIL, rule_2, Item(_name, _category, _not_in_stock, _price, '1111-1111-1112'), 'bad id'),
        Scenario(FAIL, rule_2, Item(_name, _category, _not_in_stock, _price, '111111111111'), 'bad id'),

        Scenario(PASS, rule_2, Item(_name, 4, _in_stock, _price, _id), 'category is tools'),
        Scenario(FAIL, rule_2, Item(_name, 4, _not_in_stock, _price, _id), 'category is tools, but not in stock'),
        Scenario(FAIL, rule_2, Item(_name, 5, _in_stock, _price, _id), 'category is not tools'),
        Scenario(PASS, rule_2, Item('henry', _category, _in_stock, _price, _id), 'good name'),
        Scenario(FAIL, rule_2, Item('bob ross', _category, _in_stock, _price, _id), 'bad name'),
    )
)


def test_a_rule(scenario):
    filters = SomeFilters(item=scenario.item)
    assert scenario.is_valid == scenario.rule.is_valid(filters, verbose=True), scenario.reason
