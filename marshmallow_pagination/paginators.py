# -*- coding: utf-8 -*-

import abc
import math

import six
import sqlalchemy as sa

from marshmallow_pagination import pages

class BasePaginator(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, cursor, per_page, count=None):
        self.cursor = cursor
        self.per_page = per_page
        self.count = count or self._count()

    def _count(self):
        return self.cursor.count()

    @abc.abstractproperty
    def page_type(self):
        pass

    @property
    def pages(self):
        return int(math.ceil(self.count / self.per_page))

    @abc.abstractproperty
    def get_page(self):
        pass

class OffsetPaginator(BasePaginator):
    """Paginator based on offsets and limits. Not performant for large result sets.
    """
    page_type = pages.OffsetPage

    def get_page(self, page):
        offset, limit = self.per_page * (page - 1), self.per_page
        return self.page_type(self, page, self._fetch(offset, limit))

    def _fetch(self, offset, limit):
        offset += (self.cursor._offset or 0)
        if self.cursor._limit:
            limit = min(limit, self.cursor._limit - offset)
        return self.cursor.offset(offset).limit(limit).all()

class SeekPaginator(BasePaginator):
    """Paginator using keyset pagination for performance on large result sets.
    See http://use-the-index-luke.com/no-offset for details.
    """
    page_type = pages.SeekPage

    def __init__(self, cursor, per_page, index_column, sort_column=None,
                 sort_direction=None, count=None):
        self.index_column = index_column
        self.sort_column = sort_column
        self.sort_direction = sort_direction
        super(SeekPaginator, self).__init__(cursor, per_page, count=count)

    def get_page(self, last_index=None, sort_index=None):
        limit = self.per_page
        return self.page_type(self, self._fetch(last_index, sort_index, limit))

    def _fetch(self, last_index, sort_index=None, limit=None):
        cursor = self.cursor
        direction = self.sort_direction or sa.asc
        lhs, rhs = (), ()
        if sort_index is not None:
            lhs += (self.sort_column, )
            rhs += (sort_index, )
        if last_index is not None:
            lhs += (self.index_column, )
            rhs += (last_index, )
        if any(rhs):
            filter = lhs > rhs if direction == sa.asc else lhs < rhs
            cursor = cursor.filter(filter)
        return cursor.order_by(
            direction(self.index_column)
        ).limit(
            limit
        ).all()

    def _get_index_values(self, result):
        """Get index values from last result, to be used in seeking to the next
        page. Optionally include sort values, if any.
        """
        ret = {'index': getattr(result, self.index_column.key)}
        if self.sort_column:
            key = self.sort_column.key
            ret[key] = getattr(result, self.sort_column.key)
        return ret
