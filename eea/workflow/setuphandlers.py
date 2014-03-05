""" Setuphandlers
"""

from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFCore.utils import getToolByName
from eea.workflow.vocab import ATVOCABS
import logging

logger = logging.getLogger('eea.workflow.setuphandlers')


def setupATVocabularies(context):
    """ Installs all AT-based Vocabularies
    """

    if context.readDataFile('eea.workflow.txt') is None:
        return

    replace = bool(context.readDataFile('eeaworkflow_vocabularies.txt'))

    portal = context.getSite()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return

    for vkey in ATVOCABS.keys():
        if hasattr(atvm, vkey):
            if not replace:
                continue
            atvm.manage_delObjects(ids=[vkey])

        logger.info("Adding vocabulary %s", vkey)

        atvm.invokeFactory('SimpleVocabulary', vkey)
        simple = atvm.getVocabularyByName(vkey)
        for (key, val) in ATVOCABS[vkey]:
            simple.addTerm(key, val)

