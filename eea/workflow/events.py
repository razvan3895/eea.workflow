""" Events for eea.workflow
"""
from Products.Archetypes.utils import shasattr
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implements

#Order of events triggering when an object is versioned:
#initial state creation -> object copied -> object cloned -> object versioned

class IInitialStateCreatedEvent(IObjectEvent):
    """ Event triggered when an object is initially created with a default
        workflow state
    """

class InitialStateCreatedEvent(ObjectEvent):
    """ An event object for new versions being created
    """
    implements(IInitialStateCreatedEvent)

INITIAL_ITEM_CREATION = "Initial item creation"
NEW_VERSION = "New version"
COPIED = "Copied"


def handle_workflow_initial_state_created(obj, event):
    """ Handler for the IInitialStateCreatedEvent
    """
    if not shasattr(obj, 'workflow_history'):
        return

    history = obj.workflow_history   #this is a persistent mapping

    for name, wf_entries in history.items():
        wf_entries = list(wf_entries)

        #initial creation entry has no action id
        if wf_entries[-1]['action'] != None:
            return

        wf_entries[-1]['action'] = INITIAL_ITEM_CREATION
        history[name] = tuple(wf_entries)


def handle_object_copied(obj, event):
    """ Handler for object cloned event

    The object cloned event only received the resulting object,
    with no idea to the original. This event receives the original,
    but it is triggered too soon, before the workflow history is changed
    To solve this issue we cache the UID of the original objec in the
    final object.
    """

    if not obj is event.object:
        #the event is being dispatched to sublocations
        return

    original = event.original
    obj._v_original = original


def handle_object_cloned(obj, event):
    """ Handler for object cloned event
    """

    #print "Event: ", id(event)

    if not shasattr(obj, 'workflow_history'):
        return

    if not shasattr(obj, '_v_original'):
        #this is the event triggered for a clone operation
        return

    if not obj.portal_type == obj._v_original.portal_type:
        #the event is being dispatched to sublocations
        return

    old_history = obj._v_original.workflow_history
    history = obj.workflow_history   #this is a persistent mapping

    for name in history:
        history[name] = old_history.get(name, ()) + history.get(name, ())

    for name, wf_entries in history.items():
        wf_entries = list(wf_entries)

        wf_entries[-1]['action'] = COPIED
        wf_entries[-1]['comments'] = "Copied from (uid:%s)" % \
                obj._v_original.UID()
        history[name] = tuple(wf_entries)

    #print "Copied history"


def handle_version_created(obj, event):
    """ Handler for IVersionCreatedEvent
    """

    if not shasattr(obj, 'workflow_history'):
        return

    history = obj.workflow_history   #this is a persistent mapping

    for name, wf_entries in history.items():
        wf_entries = list(wf_entries)

        #before the version event is triggered, the object appears as copied
        if wf_entries[-1]['action'] != COPIED:
            return

        wf_entries[-1]['action'] = NEW_VERSION
        wf_entries[-1]['comments'] = "New version created based on (uid:%s)" \
                % event.original.UID()
        history[name] = tuple(wf_entries)
