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

logger = logging.getLogger("eea.workflow.actions")


class ArchiveUnarchiveAction(SimpleItem):
    """ Action settings
    """
    implements(IArchiveUnarchiveAction, IRuleElementData)

    element = 'eea.workflow.rules.actions.archive_unarchive_objects'
    action = None

    @property
    def summary(self):
        if self.action:
            return "Object will be: %s" % self.action
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
