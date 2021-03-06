#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_schematics_flexible
----------------------------------

Tests for `schematics_flexible` module.
"""


import unittest
from collections import namedtuple
try:
    from unittest import mock
except ImportError:
    import mock

from schematics.exceptions import ValidationError as schematicsValidationError
from schematics_flexible import schematics_flexible
schema_tuple = namedtuple('schema', ['code', 'version', 'schema'])


class ImportException(BaseException):

    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(ImportException, self).__init__(*args, **kwargs)


class ValidationException(BaseException):

    def __init__(self, message, *args, **kwargs):
        self.message = message
        super(ValidationException, self).__init__(*args, **kwargs)


def raise_validation_exception(*args, **kwargs):
    raise ValidationException(message="Properties are wrong")


def get_schema_side_effect(code, version='latest'):
    true_validation = mock.Mock()
    true_validation.validate.return_value = True
    false_validation = mock.Mock()
    false_validation.validate.side_effect = raise_validation_exception
    if code == '04':
        return schema_tuple(schema=true_validation, code='04', version='001')
    if code == '06':
        return schema_tuple(schema=false_validation, code='05', version='001')
    if code == '07':
        raise ImportException(message="Can't import schema with code 07")


def get_mock():
    m = mock.Mock()
    m.get_schema = get_schema_side_effect
    m.validation_exception = (ValidationException,)
    m.import_exception = (ImportException,)
    return m


class TestSchematicsFlexible(unittest.TestCase):

    def test_000_validate_by_good_code(self):
        """ Send good code and try validate """
        m = schematics_flexible.Flexible(
            {'code': '04',
             'properties': {"m": "this is text"}},
            store_handler=get_mock())
        self.assertIsNone(m.validate())

    def test_001_validate_with_bad_properties(self):
        """ Send bad code and try validate """
        m = schematics_flexible.Flexible(
            {'code': '06',
             'properties': {"a": "this is test"}},
            store_handler=get_mock())
        try:
            m.validate()
        except schematicsValidationError:
            pass
        else:
            self.assertTrue(False,
                            'Model must raise exception when validate raise')

    def test_002_import_exception(self):
        """ Try import not real schema """
        m = schematics_flexible.Flexible(
            {'code': '07',
             'properties': {"a": "this is test"}},
            store_handler=get_mock())
        try:
            m.validate()
        except schematicsValidationError:
            pass
        else:
            self.assertTrue(False,
                            'Model must raise exception when import raise')
