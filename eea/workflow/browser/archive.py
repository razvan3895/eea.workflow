""" Archival views
"""

from Products.CMFPlone.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryAdapter
from plone.protect import PostOnly
from zope.event import notify
from z3c.caching.purge import Purge

from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
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
        val = {'initiator': form.get('workflow_archive_initiator'),
               'custom_message': form.get('workflow_other_reason', '').strip(),
               'reason': form.get('workflow_reasons_radio', 'other'),
        }

        if recurse:
            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'path': '/'.join(self.context.getPhysicalPath())}
            brains = catalog.searchResults(query)

            for brain in brains:
                obj = brain.getObject()
                storage = queryAdapter(obj, IObjectArchivator)
                storage.archive(obj, **val)
                notify(Purge(obj))

        else:
            storage = queryAdapter(self.context, IObjectArchivator)
            storage.archive(self.context, initiator=val['initiator'],
                     custom_message=val['custom_message'], reason=val['reason'])
            notify(Purge(self.context))

        return "OK"


class UnArchiveContent(BrowserView):
    """ UnArchive the context object
    """

    def __call__(self, **kwargs):
        PostOnly(self.request)
        form = self.request.form
        recurse = form.get('workflow_unarchive_recurse', False)
        if recurse:
            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'path': '/'.join(self.context.getPhysicalPath())}
            brains = catalog.searchResults(query)

            for brain in brains:
                obj = brain.getObject()
                if IObjectArchived.providedBy(obj):
                    storage = queryAdapter(obj, IObjectArchivator)
                    storage.unarchive(obj)
                    notify(Purge(obj))
            msg = "Object and contents have been unarchived"
        else:
            storage = queryAdapter(self.context, IObjectArchivator)
            storage.unarchive(self.context)
            msg = "Object has been unarchived"
            notify(Purge(self.context))

        IStatusMessage(self.context.REQUEST).add(msg, 'info')

        return self.request.response.redirect(self.context.absolute_url())


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
