""" IObjectArchived implementation
"""

import logging

from DateTime import DateTime
from Products.Five import BrowserView
import transaction
from Products.Archetypes.interfaces import IBaseObject
from persistent import Persistent
from zope.annotation.factory import factory
from zope.component import adapts, queryAdapter
from zope.interface import implements, alsoProvides, noLongerProvides
from zope.event import notify
from z3c.caching.purge import Purge

from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.CMFPlone.utils import getToolByName
from eea.versions.interfaces import IGetVersions
from eea.workflow.interfaces import IObjectArchived, IObjectArchivator
from Products.CMFPlone.utils import safe_unicode

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
        :param context: object which is going to be unarchived
        :param custom_message: Custom message explaining why the object was
               unarchived
        """
        noLongerProvides(context, IObjectArchived)

        now = DateTime()
        context.setExpirationDate(None)

        wftool = getToolByName(context, 'portal_workflow')
        mtool = getToolByName(context, 'portal_membership')

        state = wftool.getInfoFor(context, 'review_state')
        actor = mtool.getAuthenticatedMember().getId()

        comments = custom_message or (u"Unarchived by %(actor)s on %(date)s" % {
            'actor': actor,
            'date': now.ISO8601(),
        })

        for wfname in context.workflow_history.keys():
            history = context.workflow_history[wfname]
            history += ({
                            'action': 'UnArchive',
                            'review_state': state,
                            'actor': actor,
                            'comments': comments,
                            'time': now,
                        },)
            context.workflow_history[wfname] = history

        context.workflow_history._p_changed = True
        context.reindexObject()
        notify(Purge(context))

    def archive(self, context, initiator=None, reason=None, custom_message=None,
                archive_date=None):
        """Archive the object
        :param context: given object that should be archived
        :param initiator: the user id or name which commissioned the archival
        :param reason: reason id for which the object was archived
        :param custom_message: Custom message explaining why the object was
               archived
        :param archive_date: DateTime object which sets the expiration date of
               the object
        """
        initiator = safe_unicode(initiator)
        reason = safe_unicode(reason)
        custom_message = safe_unicode(custom_message)
        wftool = getToolByName(context, 'portal_workflow')
        has_workflow = wftool.getChainFor(context)
        if not has_workflow:
            # NOP
            return
        date = archive_date and archive_date or DateTime()
        alsoProvides(context, IObjectArchived)
        context.setExpirationDate(date)

        # refactor this setting from here, without these assignments to self
        # the test for is_archived fails
        self.archive_date = date
        self.initiator = initiator
        self.custom_message = custom_message
        self.reason = reason

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
                        'actor': actor,
                        'initiator': initiator,
                        'reason': reason,
                        'date': date.ISO8601()
                    })

        for wfname in context.workflow_history.keys():
            history = context.workflow_history[wfname]
            history += ({
                            'action': 'Archive',
                            'review_state': state,
                            'actor': actor,
                            'comments': comments,
                            'time': date,
                        },)
            context.workflow_history[wfname] = history

        context.workflow_history._p_changed = True
        context.reindexObject()
        notify(Purge(context))


archive_annotation_storage = factory(ObjectArchivedAnnotationStorage,
                                     key="eea.workflow.archive")


# helper functions
def archive_object(context, **kwargs):
    """ Archive given context
    :param context: object
    :param kwargs: options that are passed to the archive method directly
           affecting it's results if they are passed
    """
    storage = queryAdapter(context, IObjectArchivator)
    storage.archive(context, **kwargs)
    return context


def archive_obj_and_children(context, **kwargs):
    """ Archive given context and it's children
    :param context: object
    :param kwargs: options that are passed to the archive method directly
           affecting it's results if they are passed
    """
    catalog = getToolByName(context, 'portal_catalog')
    query = {'path': '/'.join(context.getPhysicalPath())}
    brains = catalog.searchResults(query)

    affected_objects = []
    for brain in brains:
        obj = brain.getObject()
        storage = queryAdapter(obj, IObjectArchivator)
        if not storage:
            continue
        storage.archive(obj, **kwargs)
        affected_objects.append(obj)
    return affected_objects


def archive_previous_versions(context, skip_already_archived=True,
                              same_archive_date=False, also_children=False,
                              **kwargs):
    """ Archive previous versions of given object
    :param object context: object
    :param bool skip_already_archived: boolean indicating whether it should skip
           archiving the previous version that is already archived
    :param bool same_archive_date: boolean indicating whether the object being
           archived should receive the same archiving date as the context
    :param bool also_children: boolean indicating whether the children of the
           versions should also be archived
    :param dict kwargs: options that are passed to the archive method directly
           affecting it's results if they are passed
    :rtype list
    """
    versions_adapter = IGetVersions(context)
    archivator_adapter = queryAdapter(context, IObjectArchivator)
    options = kwargs
    if not options:
        custom_message = getattr(archivator_adapter, 'custom_message', '')
        reason = getattr(archivator_adapter, 'reason',
                         'content_is_outdated')
        initiator = getattr(archivator_adapter, 'initiator', None)
        options = {'custom_message': custom_message,
                   'initiator': initiator,
                   'reason': reason}
    if same_archive_date and getattr(archivator_adapter, 'archive_date'):
        options.update({'archive_date': archivator_adapter.archive_date})
    versions = versions_adapter.versions()
    previous_versions = []
    uid = context.UID()
    for version in versions:
        if version.UID() == uid:
            break
        previous_versions.append(version)
    affected_objects = []
    for obj in previous_versions:
        if skip_already_archived:
            if IObjectArchived.providedBy(obj):
                continue
        if also_children:
            affected_objects.extend(archive_obj_and_children(obj, **options))
        else:
            storage = queryAdapter(obj, IObjectArchivator)
            storage.archive(obj, **options)
            affected_objects.append(obj)
    return affected_objects


class ArchivePreviousVersions(BrowserView):
    """ Archives previous versions of objects that are archived
    """

    def __init__(self, context, request):
        super(ArchivePreviousVersions, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        """ Call method
        """
        log = logging.getLogger("archive-versions")
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat(object_provides="eea.workflow.interfaces.IObjectArchived",
                     show_inactive=True, Language="all")
        also_children = self.request.get('alsoChildren')
        count = 0
        total = len(brains)
        obj_urls = "THE FOLLOWING OBJECTS ARE ARCHIVED:\n"
        log.info("Start Archiving the previous versions of %d archived objects",
                 total)

        affected_objects = set()
        for brain in brains:
            previous_versions = []
            brain_url = brain.getURL()
            try:
                obj = brain.getObject()
            except Exception:
                log.info("Can't retrieve %s", brain_url)
                continue
            if also_children:
                previous_versions.extend(archive_previous_versions(obj,
                                                    also_children=True,
                                                    same_archive_date=True))
            else:
                previous_versions.extend(archive_previous_versions(obj,
                                                    same_archive_date=True))
            for obj in previous_versions:
                obj_url = obj.absolute_url()
                if obj_url not in affected_objects:
                    log.info("Archived %s", obj_url)
                    obj_urls += "%s \n" % obj_url
                    affected_objects.add(obj_url)
            count += 1
            if count % 100 == 0:
                transaction.commit()
                log.info('Subtransaction committed to zodb (%s/%s)', count,
                         total)
        log.info("End Archiving the previous versions of %d archived objects",
                 total)
        return obj_urls
