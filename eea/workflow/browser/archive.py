""" Archival views
"""

from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryAdapter, getMultiAdapter
from plone.protect import PostOnly

from Products.CMFPlone.utils import getToolByName
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from eea.workflow.archive import archive_object, archive_obj_and_children, \
    archive_previous_versions
from eea.workflow.interfaces import IObjectArchivator, IObjectArchived


class Reasons(BrowserView):
    """ Returns a dict of reasons
    """

    def __call__(self):
        rv = NamedVocabulary('eea.workflow.reasons')
        reasons = rv.getVocabularyDict(self.context)
        return reasons


class ArchiveContent(BrowserView):
    """ Archive the context object
    """

    def __call__(self, **kwargs):
        PostOnly(self.request)
        form = self.request.form
        recurse = form.get('workflow_archive_recurse', False)
        prev_versions = form.get('workflow_archive_previous_versions', False)
        val = {'initiator': form.get('workflow_archive_initiator', ''),
               'custom_message': form.get('workflow_other_reason', '').strip(),
               'reason': form.get('workflow_reasons_radio', 'other'),
        }

        context = self.context
        ploneview = getMultiAdapter((context, self.request), name='plone')
        if ploneview.isDefaultPageInFolder():
            context = self.context.getParentNode()

        if recurse and not prev_versions:
            archive_obj_and_children(context, **val)
        elif recurse and prev_versions:
            archive_obj_and_children(context, **val)
            archive_previous_versions(context, also_children=True, **val)
        elif prev_versions and not recurse:
            archive_object(context, **val)
            archive_previous_versions(context, **val)
        else:
            archive_object(context, **val)

        return "OK"


class UnArchiveContent(BrowserView):
    """ UnArchive the context object
    """

    def __call__(self, **kwargs):
        PostOnly(self.request)
        form = self.request.form
        recurse = form.get('workflow_unarchive_recurse', False)

        context = self.context
        ploneview = getMultiAdapter((context, self.request), name='plone')
        if ploneview.isDefaultPageInFolder():
            context = self.context.getParentNode()

        if recurse:
            catalog = getToolByName(context, 'portal_catalog')
            query = {'path': '/'.join(context.getPhysicalPath())}
            brains = catalog.searchResults(query)

            for brain in brains:
                obj = brain.getObject()
                if IObjectArchived.providedBy(obj):
                    storage = queryAdapter(obj, IObjectArchivator)
                    storage.unarchive(obj)
            msg = "Object and contents have been unarchived"
        else:
            storage = queryAdapter(context, IObjectArchivator)
            storage.unarchive(context)
            msg = "Object has been unarchived"

        IStatusMessage(context.REQUEST).add(msg, 'info')

        return self.request.response.redirect(context.absolute_url())


class ArchiveStatus(BrowserView):
    """ Show the same info as the archive status viewlet
    """

    @property
    def info(self):
        """ Info used in view
        """
        info = IObjectArchivator(self.context)

        rv = NamedVocabulary('eea.workflow.reasons')
        vocab = rv.getVocabularyDict(self.context)

        archive_info = dict(initiator=info.initiator,
                            archive_date=info.archive_date,
                            reason=vocab.get(info.reason, "Other"),
                            custom_message=info.custom_message)

        return archive_info
