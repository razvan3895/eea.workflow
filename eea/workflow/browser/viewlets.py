""" Viewlets
"""

from plone.app.layout.viewlets.common import ViewletBase
from eea.workflow.interfaces import IObjectArchivator
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary


class ArchiveViewlet(ViewletBase):
    """ Viewlet that appears only when the object is archived
    """

    def update(self):
        """ Update viewlet
        """
        info = IObjectArchivator(self.context)

        rv = NamedVocabulary('eea.workflow.reasons')
        vocab = rv.getVocabularyDict(self.context)

        archive_info = dict(initiator=info.initiator,
                            archive_date=info.archive_date,
                            reason=vocab.get(info.reason, "Other"),
                            custom_message=info.custom_message)

        self.info = archive_info
