""" IObjectArchived implementation
"""

from DateTime import DateTime
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import getToolByName
from eea.workflow.interfaces import IObjectArchived, IObjectArchivator
from persistent import Persistent
from zope.annotation.factory import factory
from zope.component import adapts
from zope.interface import implements, alsoProvides


class ObjectArchivedAnnotationStorage(Persistent):
    """ The IObjectArchived information stored as annotation
    """
    implements (IObjectArchivator)
    adapts(IBaseObject)

    @property
    def is_archived(self):
        """Is this object archived?"""
        return bool(getattr(self, 'archive_date', False))

    def archive(self, context, initiator=None, reason=None, custom_message=None):
        """Archive the object"""

        now = DateTime()
        alsoProvides(context, IObjectArchived)
        context.setExpirationDate(now)

        self.archive_date   = now
        self.initiator      = initiator
        self.custom_message = custom_message
        self.reason         = reason

        wftool = getToolByName(context, 'portal_workflow')
        mtool = getToolByName(context, 'portal_membership')

        state = wftool.getInfoFor(context, 'review_state')
        actor = mtool.getAuthenticatedMember().getId()

        rv = NamedVocabulary('eea.workflow.reasons')
        vocab = rv.getVocabularyDict(context)
        reason = vocab.get(reason, "Other")

        if custom_message:
            reason += u" (%s)" % custom_message

        comments = (u"Archived by %(actor)s on %(date)s by request "
                    u"from %(initiator)s with reason: %(reason)s" % {
                        'actor':actor,
                        'initiator':initiator,
                        'reason':reason,
                        'date':now.ISO8601(),
                    })

        for wfname in context.workflow_history.keys():
            history = context.workflow_history[wfname]
            history += ({
                'action':'Archive',
                'review_state':state,
                'actor':actor,
                'comments':comments,
                'time':now,
                },)
            context.workflow_history[wfname] = history

        context.workflow_history._p_changed = True
        context.reindexObject()


archive_annotation_storage = factory(ObjectArchivedAnnotationStorage, key="eea.workflow.archive")
