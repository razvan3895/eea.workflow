============
EEA Workflow
============
Enhancements for the default Plone/CMF workflow system.

Contents
========

.. contents::

Main features
=============

- Progress monitoring, a system that visually display a progress bar
  in the publishing process of a document according with the workflow
  state in which the document is.

Install
=======

- Add eea.workflow to your eggs section in your buildout and re-run buildout. You
  can download a sample buildout from
  https://github.com/eea/eea.workflow/tree/master/buildouts/plone4
- Install eea.workflow within Site Setup > Add-ons

Getting started
===============

Progress monitoring
-------------------

1. Go to *ZMI > portal_workflows > Contents Tab* and select your workflow
2. Click on *Progress Bar Tab* and update *% done* for each state


Source code
===========

- Latest source code (Plone 4 compatible):
  https://github.com/eea/eea.workflow
- Plone 2 and 3 compatible:
  https://github.com/eea/eea.workflow/tree/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Workflow (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
