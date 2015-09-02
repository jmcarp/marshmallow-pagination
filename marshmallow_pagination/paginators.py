# -*- coding: utf-8 -*-

import abc
import math

import six
import sqlalchemy as sa

from marshmallow_sqlalchemy.convert import ModelConverter

from marshmallow_pagination import pages

converter = ModelConverter()
def convert_value(row, attr):
    field = converter._get_field_class_for_property(attr.property)
    value = getattr(row, attr.key)
    return field()._serialize(value, None, None)

class BasePaginator(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, cursor, per_page, count=None):
        self.cursor = cursor
        self.count = count or self._count()
        self.per_page = per_page or self.count

    def _count(self):
        return self.cursor.count()

    @abc.abstractproperty
    def page_type(self):
        pass

    @property
    def pages(self):
        if self.per_page:
            return int(math.ceil(self.count / self.per_page))
        return 0

    @abc.abstractproperty
    def get_page(self):
        pass

class OffsetPaginator(BasePaginator):
    """Paginator based on offsets and limits. Not performant for large result sets.
    """
    page_type = pages.OffsetPage

    def get_page(self, page, eager=True):
        offset, limit = self.per_page * (page - 1), self.per_page
        return self.page_type(self, page, self._fetch(offset, limit, eager=eager))

    def _fetch(self, offset, limit, eager=True):
        offset += (self.cursor._offset or 0)
        if self.cursor._limit:
            limit = min(limit, self.cursor._limit - offset)
        query = self.cursor.offset(offset).limit(limit)
        return query.all() if eager else query

class SeekPaginator(BasePaginator):
    """Paginator using keyset pagination for performance on large result sets.
    See http://use-the-index-luke.com/no-offset for details.
    """
    page_type = pages.SeekPage

    def __init__(self, cursor, per_page, index_column, sort_column=None, count=None):
        self.index_column = index_column
        self.sort_column = sort_column
        super(SeekPaginator, self).__init__(cursor, per_page, count=count)

    def get_page(self, last_index=None, sort_index=None, eager=True):
        limit = self.per_page
        return self.page_type(self, self._fetch(last_index, sort_index, limit, eager=eager))

    def _fetch(self, last_index, sort_index=None, limit=None, eager=True):
        cursor = self.cursor
        direction = self.sort_column[1] if self.sort_column else sa.asc
        lhs, rhs = (), ()
        if sort_index is not None:
            lhs += (self.sort_column, )
            rhs += (sort_index, )
        if last_index is not None:
            lhs += (self.index_column, )
            rhs += (last_index, )
        lhs = sa.tuple_(*lhs)
        rhs = sa.tuple_(*rhs)
        if rhs.clauses:
            filter = lhs > rhs if direction == sa.asc else lhs < rhs
            cursor = cursor.filter(filter)
        query = cursor.order_by(direction(self.index_column)).limit(limit)
        return query.all() if eager else query

    def _get_index_values(self, result):
        """Get index values from last result, to be used in seeking to the next
        page. Optionally include sort values, if any.
        """
        ret = {'last_index': convert_value(result, self.index_column)}
        if self.sort_column:
            key = 'last_{0}'.format(self.sort_column[0].key)
            ret[key] = convert_value(result, self.sort_column[0])
        return ret
