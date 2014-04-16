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
        portal = self.portal
        fid = portal.invokeFactory("Folder", 'f1')
        self.folder = portal[fid]
        docid = self.folder.invokeFactory("Document", 'd1')
        self.doc = self.folder[docid]

    def test_archive_object(self):
        """ Test history version
        """
        archive_object(self.folder)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_obj_and_children(self):
        """ Test history version
        """
        archive_obj_and_children(self.folder)
        assert IObjectArchived.providedBy(self.folder)
        assert IObjectArchived.providedBy(self.doc)

    def test_archive_previous_versions(self):
        """ Test the archival of the previous versions
            for the given object
        """
        version = create_version(self.folder)
        archive_previous_versions(version)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_previous_versions_without_children(self):
        """ Test the archival of the previous versions
            for the given object even when calling the method
            that should archive also the children
        """
        fid = self.portal.invokeFactory("Folder", 'f2')
        self.folder = self.portal[fid]
        version = create_version(self.folder)
        archive_previous_versions(version, also_children=True)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)

    def test_archive_previous_versions_with_children(self):
        """ Test the archival of the previous versions
            for the given object and their children
        """
        version = create_version(self.folder)
        archive_previous_versions(version, also_children=True)
        assert not IObjectArchived.providedBy(version)
        assert IObjectArchived.providedBy(self.folder)
        assert IObjectArchived.providedBy(self.doc)

    def test_archive_previous_versions_with_children_return(self):
        """ Test the return value for archival of the previous versions
            for the given object and their children
        """
        version = create_version(self.folder)
        objects = archive_previous_versions(version, also_children=True)
        expected_output = [self.folder, self.doc]
        assert objects == expected_output
