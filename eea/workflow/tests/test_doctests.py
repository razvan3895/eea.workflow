""" Doctests
"""
import doctest
import unittest
from eea.workflow.tests.base import FunctionalTestCase as EEATestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite


OPTIONFLAGS = (
        doctest.REPORT_ONLY_FIRST_FAILURE |
        doctest.ELLIPSIS |
        doctest.NORMALIZE_WHITESPACE
)

def test_suite():
    """ Tests
    """
    return unittest.TestSuite((
            FunctionalDocFileSuite('README.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.workflow',
                  test_class=EEATestCase),
            FunctionalDocFileSuite('tests/archive.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.workflow',
                  test_class=EEATestCase),
            FunctionalDocFileSuite('tests/archive-rule.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.workflow',
                  test_class=EEATestCase),
              ))
