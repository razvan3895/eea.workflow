""" Utils module
"""
from Products.Archetypes.Field import Field, TextField
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.UnicodeSplitter import process_unicode
from eea.workflow.interfaces import IFieldIsRequiredForState, IValueProvider
from zope.component import adapts
from zope.interface import Interface, implements
from logging import getLogger

logger = getLogger('eea.workflow')

class ATFieldValueProvider(object):
    """An IValueProvider implementation for AT Fields"""

    implements(IValueProvider)
    adapts(Interface, Field)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def has_value(self, **kwargs):
        """ Has value
        """
        return bool(self.get_value())  #may trigger false positives

    def get_value(self, **kwargs):
        """ Get value
        """
        accessor = self.field.getAccessor(self.context)
        if not accessor:
            logger.warning("Field %s for %s has no accessor",
                        self.field, self.context)
            return None
        return accessor()

    def value_info(self, **kwargs):
        """ Get value info
        """
        accessor = self.field.getAccessor(self.context)
        if accessor is None:
            logger.warning("Field %s for %s has no accessor",
                        self.field, self.context)

            return {
                'raw_value':None,
                'value':None,
                'has_value':False,
                'msg':"Could not find accessor for this field"
            }

        return {
            'raw_value':accessor(),
            'value':accessor(),
            'has_value':self.has_value(**kwargs),
            'msg':('No value filled in') #needs i18n
        }



class TextFieldValueProvider(ATFieldValueProvider):
    """An IValueProvider implementation for Text Fields"""

    adapts(Interface, TextField)

    def has_value(self, **kwargs):
        """ Returns true if text field has at least 2 words in it
        """
        convert = getToolByName(self.context, 'portal_transforms').convert
        accessor = self.field.getAccessor(self.context)
        if not accessor:
            logger.warning("Field %s for %s has no accessor",
                        self.field, self.context)
            return False
        value = accessor()
        text = convert('html_to_text', value).getData().strip()
        if not isinstance(text, unicode):
            text = unicode(text, 'utf-8', 'ignore')
        words = process_unicode(text)
        return len(list(words)) > 1   #there should be at least 2 words, or
                                #the field is considered empty

    def value_info(self, **kwargs):
        """ Get value info
        """
        accessor = self.field.getAccessor(self.context)
        if accessor is None:
            logger.warning("Field %s for %s has no accessor",
                        self.field, self.context)

            return {
                'raw_value':None,
                'value':None,
                'has_value':False,
                'msg':"Could not find accessor for this field"
            }

        return {
            'raw_value':accessor(),
            'value':accessor(),
            'has_value':self.has_value(**kwargs),
            'msg':('Needs at least two words.') #needs i18n
        }


class ATFieldIsRequiredForState(object):
    """ An IFieldIsRequiredForState implementation for AT Fields """

    implements(IFieldIsRequiredForState)
    adapts(Interface, Field)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    def __call__(self, state, **kwargs):
        if self.field.required:
            return True
        ATTR = 'required_for_' + state
        return getattr(self.field, ATTR, False)

