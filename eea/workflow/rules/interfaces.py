""" eea.workflow content rules interfaces
"""
from zope import schema
from zope.interface import Interface
from eea.workflow.config import EEAMessageFactory as _


class IArchiveUnarchiveAction(Interface):
    """ Archive/Unarchive settings schema
    """
    action = schema.Choice(title=u"Workflow Action",
                           description=u"The state which the object will "
                                       u"transition to.",
                           values=['archived', 'unarchived'],
                           required=True)

    applyRecursively = schema.Bool(
        title=_('Set action recursively'),
        description=_("Apply action to children"))

    affectPreviousVersion = schema.Bool(
        title=_('Only affect the previous object version'),
        description=_("Apply action only to the previous version"
                      " instead of current object"))
