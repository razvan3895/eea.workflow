""" Test archive functionality
"""
from eea.versions.versions import create_version
from eea.workflow.archive import archive_object, archive_obj_and_children, \
    archive_previous_versions
from eea.workflow.tests.base import TestCase
from eea.workflow.interfaces import IObjectArchived


class TestArchive(TestCase):
    """ TestHistory TestCase class
    """

    def afterSetUp(self):
        """ After Setup
        """
        self.setRoles(('Manager', ))

    def test_archive_object(self):
        """ Test history version
        """
        portal = self.portal
        fid    = portal.invokeFactory("Folder", 'f1')
        folder = portal[fid]
        archive_object(folder)
        assert IObjectArchived.providedBy(folder)

    def test_archive_obj_and_children(self):
        """ Test history version
        """
        portal = self.portal
        fid    = portal.invokeFactory("Folder", 'f1')
        folder = portal[fid]
        docid  = folder.invokeFactory("Document", 'd1')
        doc    = folder[docid]
        archive_obj_and_children(folder)
        assert IObjectArchived.providedBy(folder)
        assert IObjectArchived.providedBy(doc)

    def test_archive_previous_versions(self):
        portal  = self.portal
        fid     = portal.invokeFactory("Folder", 'f1')
        folder  = portal[fid]
        version = create_version(folder)
        archive_previous_versions(version)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(folder)
