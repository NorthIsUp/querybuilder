# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """Tests for `querybuilder` package."""
#
# import pytest
#
#
# from querybuilder import querybuilder
#
#
# @pytest.fixture
# def response():
#     """Sample pytest fixture.
#
#     See more at: http://doc.pytest.org/en/latest/fixture.html
#     """
#     # import requests
#     # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
#
#
# def test_content(response):
#     """Sample pytest test function with the pytest fixture as an argument."""
#     # from bs4 import BeautifulSoup
#     # assert 'GitHub' in BeautifulSoup(response.content).title.string
#
#
# class ApothecaryFilters(Filters):
#
#     def __init__(self, apothecary):
#         self.apothecary = apothecary
#
#     @NumericFilter(
#         label='Comment Toxicity Score',
#         description='A 0-1 value as provided by the perspective API',
#         validation=Validation(min=0, max=1, step=0.01),
#     )
#     def toxicity(self):
#         return self.apothecary._toxicity
#
#     @BooleanFilter(
#         label='Comment is toxic',
#         description='Toxicity as defined by a reasonable threshold',
#     )
#     def is_toxic(self):
#         return self.apothecary.is_toxic
#
#     @BooleanFilter(
#         label='Comment is spam',
#         description='Comment is marked as spam by either a moderator or akismet',
#     )
#     def is_spam(self):
#         return self.apothecary.is_spam
#
#     @BooleanFilter(
#         label='Author is whitelisted',
#         description='The comment author is whitelisted on the forum',
#         input=Inputs.RADIO,
#         values=({1: 'Is Whitelisted'}, {0: 'Is Not Whitelisted'}),
#     )
#     def is_user_whitlisted(self):
#         return self.apothecary.user_is_whitelisted
#
#     @IntegerFilter(
#         label='User moderation count',
#         description='Number of times the comment author has been previously moderated on this forum',
#     )
#     def delete_offense_count(self):
#         '''check if the user has three comments deleted by moderators'''
#         from disqus.aggregators.redis import UserModeratorDeletedCountForum
#         return self.apothecary.offense_count(UserModeratorDeletedCountForum)
#
#     @IntegerFilter(
#         label='User spam count',
#         description='Number of times the comment author has been previously marked as spam on this forum',
#     )
#     def spam_offense_count(self):
#         '''check if the user has three comments marked as by moderators or akismet'''
#         from disqus.aggregators.redis import UserSpamCountForum
#         return self.apothecary.offense_count(UserSpamCountForum)
