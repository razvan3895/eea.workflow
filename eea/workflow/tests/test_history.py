""" Test history
"""
from eea.versions.versions import create_version
from eea.workflow.events import COPIED
from eea.workflow.events import INITIAL_ITEM_CREATION
from eea.workflow.events import NEW_VERSION
from eea.workflow.tests.base import TestCase


class TestHistory(TestCase):
    """ TestHistory TestCase class
    """

    def afterSetUp(self):
        """ After Setup
        """
        self.setRoles(('Manager', ))

    def test_history_a_creation(self):
        """ Test history creation
        """
        fid = self.portal.invokeFactory("Folder", 'f1')
        folder = self.portal[fid]
        history = folder.workflow_history['simple_publication_workflow']

        assert len(history) == 1
        assert history[0]['action'] == INITIAL_ITEM_CREATION

    def test_history_copy(self):
        """ Test history copy
        """
        portal = self.portal
        fid = portal.invokeFactory("Folder", 'f1')
        folder = portal[fid]

        wftool = portal.portal_workflow
        wftool.doActionFor(folder, 'publish')
        clipb = portal.manage_copyObjects(ids=fid)
        res = portal.manage_pasteObjects(clipb)
        new_id = res[0]['new_id']
        foldercopy = portal[new_id]

        history = foldercopy.workflow_history['simple_publication_workflow']

        assert len(history) == 3
        assert history[0]['action'] == INITIAL_ITEM_CREATION
        assert history[1]['action'] == 'publish'
        assert history[2]['action'] == COPIED
        assert history[2]['review_state'] == history[0]['review_state']

    def test_history_version(self):
        """ Test history version
        """
        portal = self.portal
        fid = portal.invokeFactory("Folder", 'f1')
        folder = portal[fid]
        wftool = portal.portal_workflow
        wftool.doActionFor(folder, 'publish')

        version = create_version(folder)
        history = version.workflow_history['simple_publication_workflow']

        assert len(history) == 3
        assert history[0]['action'] == INITIAL_ITEM_CREATION
        assert history[1]['action'] == 'publish'
        assert history[2]['action'] == NEW_VERSION
        assert history[2]['review_state'] == history[0]['review_state']


def test_suite():
    """ Test Suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHistory))
    return suite

