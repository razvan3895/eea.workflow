""" eea.workflow actions
"""
import logging
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements, Interface

from OFS.SimpleItem import SimpleItem
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.app.contentrules.browser.formhelper import AddForm as PloneAddForm
from plone.app.contentrules.browser.formhelper import EditForm as PloneEditForm
from Products.CMFPlone.utils import getToolByName

from eea.workflow.rules.interfaces import IArchiveUnarchiveAction
from eea.workflow.interfaces import IObjectArchivator
from eea.versions.interfaces import IGetVersions

logger = logging.getLogger("eea.workflow.actions")


class ArchiveUnarchiveAction(SimpleItem):
    """ Action settings
    """
    implements(IArchiveUnarchiveAction, IRuleElementData)

    element = 'eea.workflow.rules.actions.archive_unarchive_objects'
    action = None
    applyRecursively = False
    affectPreviousVersion = False

    @property
    def summary(self):
        apply_recursively = getattr(self, "applyRecursively")
        affect_previous_version = getattr(self, "affectPreviousVersion")
        msg_template = "%s will be: %s" % ("%s", self.action)
        msg = msg_template % ("Object")
        if apply_recursively:
            msg = msg_template % ("Object and it's children")
        if affect_previous_version:
            msg = msg_template % ("Previous object revision")
        if affect_previous_version and apply_recursively:
            msg = msg_template % ("Previous object version and it's children")
        if self.action:
            return msg
        else:
            return "Not configured"


class ArchiveUnarchiveExecutor(object):
    """ Archive Unarchive Action executor
    """
    implements(IExecutable)
    adapts(Interface, IArchiveUnarchiveAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        action = self.element.action
        obj = self.event.object
        orig_obj_url = obj.absolute_url(1)
        versions = IGetVersions(obj).versions()
        adapter = None
        val = dict()
        rec_action = ''
        import pdb; pdb.set_trace()

        if action == "archived":
            rec_action = 'archive'
            message = 'New version %s was published' % orig_obj_url
        else:
            rec_action = 'unarchive'
            message = ('Unarchived by content rule because latest version %s '
                       'was unpublished') % orig_obj_url

        if self.element.affectPreviousVersion and self.element.applyRecursively:
            if len(versions) < 2:
                # no action to be taken
                return True
            else:
                obj = versions[-2]
        elif self.element.affectPreviousVersion:
            if len(versions) < 2:
                # no action to be taken
                return True
            else:
                obj = versions[-2]
        else:
            pass

        val = dict(initiator='contentRules', reason='Other',
                   custom_message=message)

        if self.element.applyRecursively:
            self.recursive_action(obj, rec_action, val)
        else:
            adapter = IObjectArchivator(obj)
            if action == "archived":
                adapter.archive(obj, **val)
            else:
                adapter.unarchive(obj, **val)

        logger.info("Object %s state is %s", obj.absolute_url(), action)
        return True

    def recursive_action(self, orig_obj, action, val):
        """
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'path': '/'.join(orig_obj.getPhysicalPath())}
        brains = catalog.searchResults(query)
        for brain in brains:
            obj = brain.getObject()
            storage = IObjectArchivator(obj)
            logger.info("Object %s state is %s", obj.absolute_url(), action)
            getattr(storage, action)(obj, **val)


class AddForm(PloneAddForm):
    """ Action add form
    """
    form_fields = form.FormFields(IArchiveUnarchiveAction)
    label = u"Archive/Unarchive action"
    description = u"An archive/unarchive action."
    form_name = u"Archive/Unarchive content"

    def create(self, data):
        """ Add Action Create method
        """
        action = ArchiveUnarchiveAction()
        form.applyChanges(action, self.form_fields, data)
        return action


class EditForm(PloneEditForm):
    """ Action edit form
    """
    form_fields = form.FormFields(IArchiveUnarchiveAction)
    label = u"Edit Archive/Unarchive action"
    description = u""
    form_name = u"Archive/Unarchive action"
