# -*- coding: utf-8 -*-

import abc
import collections

import six

class BasePage(six.with_metaclass(abc.ABCMeta, collections.Sequence)):
    """A page of results.
    """
    def __init__(self, paginator, results):
        self.paginator = paginator
        self.results = results

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return self.results[index]

    @abc.abstractproperty
    def info(self):
        pass

class OffsetPage(BasePage):

    def __init__(self, paginator, page, results):
        self.page = page
        super(OffsetPage, self).__init__(paginator, results)

    @property
    def info(self):
        return {
            'page': self.page,
            'count': self.paginator.count,
            'pages': self.paginator.pages,
            'per_page': self.paginator.per_page,
        }

class SeekPage(BasePage):

    @property
    def last_indexes(self):
        if self.results:
            return self.paginator._get_index_values(self.results[-1])
        return None

    @property
    def info(self):
        return {
            'count': self.paginator.count,
            'pages': self.paginator.pages,
            'per_page': self.paginator.per_page,
            'last_indexes': self.last_indexes,
        }
