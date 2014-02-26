""" eea.workflow content rules interfaces
"""
from zope import schema
from zope.interface import Interface


class IArchiveUnarchiveAction(Interface):
    """ Archive/Unarchive settings schema
    """
    action = schema.Choice(title=u"Workflow Action",
                           description=u"The state which the object will "
                                       u"transition to.",
                           values=['archived', 'unarchived'],
                           required=True)
