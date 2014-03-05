""" IObjectArchived implementation
"""

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.utils import getToolByName
from eea.versions.interfaces import IGetVersions
from eea.workflow.interfaces import IObjectArchived, IObjectArchivator
from persistent import Persistent
from zope.annotation.factory import factory
from zope.component import adapts, queryAdapter
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.event import notify
from z3c.caching.purge import Purge


class ObjectArchivedAnnotationStorage(Persistent):
    """ The IObjectArchived information stored as annotation
    """
    implements(IObjectArchivator)
    adapts(IBaseObject)

    @property
    def is_archived(self):
        """Is this object archived?"""
        return bool(getattr(self, 'archive_date', False))

    def unarchive(self, context, custom_message=None):
        """ Unarchive the object
        """
        noLongerProvides(context, IObjectArchived)

        now = DateTime()
        context.setExpirationDate(None)

        wftool = getToolByName(context, 'portal_workflow')
        mtool = getToolByName(context, 'portal_membership')

        state = wftool.getInfoFor(context, 'review_state')
        actor = mtool.getAuthenticatedMember().getId()

        comments = custom_message or (u"Unarchived by %(actor)s on %(date)s" % {
                        'actor':actor,
                        'date':now.ISO8601(),
                    })

        for wfname in context.workflow_history.keys():
            history = context.workflow_history[wfname]
            history += ({
                'action':'UnArchive',
                'review_state':state,
                'actor':actor,
                'comments':comments,
                'time':now,
                },)
            context.workflow_history[wfname] = history

        context.workflow_history._p_changed = True
        context.reindexObject()
        notify(Purge(context))

    def archive(self, context, initiator=None, reason=None, custom_message=None):
        """Archive the object"""

        wftool = getToolByName(context, 'portal_workflow')
        has_workflow = wftool.getChainFor(context)
        if not has_workflow:
            # NOP
            return
        now = DateTime()
        alsoProvides(context, IObjectArchived)
        context.setExpirationDate(now)

        self.archive_date   = now
        self.initiator      = initiator
        self.custom_message = custom_message
        self.reason         = reason

        state = wftool.getInfoFor(context, 'review_state')
        mtool = getToolByName(context, 'portal_membership')
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
        notify(Purge(context))


archive_annotation_storage = factory(ObjectArchivedAnnotationStorage, key="eea.workflow.archive")

# helper functions
def archive_object(context, **kwargs):
    """ Archive given context
    """
    storage = queryAdapter(context, IObjectArchivator)
    storage.archive(context, **kwargs)


def archive_obj_and_children(context, **kwargs):
    """ Archive given context and it's children
    """
    catalog = getToolByName(context, 'portal_catalog')
    query = {'path': '/'.join(context.getPhysicalPath())}
    brains = catalog.searchResults(query)

    for brain in brains:
        obj = brain.getObject()
        storage = queryAdapter(obj, IObjectArchivator)
        storage.archive(obj, **kwargs)


def archive_previous_versions(context, also_children=False, **kwargs):
    """ Archive previous versions of given object
    """
    adapter = IGetVersions(context)
    versions = adapter.versions()
    previous_versions = []
    uid = context.UID()
    for version in versions:
        if version.UID() == uid:
            break
        previous_versions.append(version)
    for obj in previous_versions:
        if also_children:
            archive_obj_and_children(obj, **kwargs)
        storage = queryAdapter(obj, IObjectArchivator)
        storage.archive(obj, **kwargs)
