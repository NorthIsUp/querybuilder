# -*- coding: utf-8 -*-

from __future__ import absolute_import


class ToDictMixin(object):

    DICT_KEYS = NotImplementedError

    def to_dict(self):
        return {
            k: v.to_dict() if hasattr(v, 'to_dict') else v
            for k, v in ((k, getattr(self, k, None)) for k in self.DICT_KEYS)
            if v
        }
