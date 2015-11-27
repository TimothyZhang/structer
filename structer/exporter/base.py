# coding=utf-8
__author__ = 'Timothy'

import copy


class BaseExporter(object):
    def __init__(self, project):
        self.project = project
        self.__files = {}

    def save(self, name, data):
        self.__files[name] = data

    def get_files(self):
        return copy.copy(self.__files)

    def export(self):
        pass
