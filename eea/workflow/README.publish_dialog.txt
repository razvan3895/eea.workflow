Publish dialog
==============

The eea.workflow package offers a popup dialog that allows adding comments to
the workflow history, when making a publish action. It does this with the help
of a Javascript file (the publish_dialog.js) that automatically hooks up the
dialog to the publish action from the workflow menu.


Instalation
-----------
To enable it on any content type, the publish_dialog.js file needs to be loaded
for that content type. To achieve this, we use a condition in the
portal_javascripts that enumerates the allowed content types:

expression="python: (not portal.portal_membership.isAnonymousUser()) and object.meta_type in ['Assessment', 'Specification']"

The answers to the questions in the popup are saved in the
context.workflow_history mapping. They are saved as a single string, in
concatenated form, to enable easy display in the Workflow History page.


Pluggability: Context-based questions
-------------------------------------
It is possible to have a different set of questions, for each content type. By
default, the questions are defined in the default_publish_questions.pt
template. By defining a <portal_type>_publish_questions.pt template, it is possible
to have a different set of questions.
