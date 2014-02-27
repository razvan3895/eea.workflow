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
from eea.workflow.rules.interfaces import IArchiveUnarchiveAction
from eea.workflow.interfaces import IObjectArchivator

logger = logging.getLogger("eea.workflow.actions")


class ArchiveUnarchiveAction(SimpleItem):
    """ Action settings
    """
    implements(IArchiveUnarchiveAction, IRuleElementData)

    element = 'eea.workflow.rules.actions.archive_unarchive_objects'
    action = None

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

        adapter = IObjectArchivator(obj)
        if action == "archived":
            adapter.archive(obj, **dict(initiator='contentRules',
                            reason='other', custom_message='new version '
                                                           'published'))
        else:
            adapter.unarchive(obj, **dict(initiator='contentRules',
                            reason='other', custom_message='Unarchived by'
                                                           ' content rule'))
        logger.info("Object %s state is %s", obj.absolute_url(),
                    action)
        return True


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
