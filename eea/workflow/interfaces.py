""" Eea.workflow interfaces
"""
from zope.interface import Interface, Attribute
#from zope.schema import List, Dict, TextLine, Object


class IHasMandatoryWorkflowFields(Interface):
    """ Marker interface for objects with fields that are required 
    for workflow transitions 
    """


class IValueProvider(Interface):
    """ Objects of this type provide values

    The use case is this: we want to be able to interrogate various 
    AT fields contained in objects if they have value; we don't want 
    to hardcode the logic that achieves this, so we make it extendible 
    by adaptation. This package also provides a default implementation 
    for a component that adapts AT fields -> IValueProvider
    """

    def has_value(kwargs):
        """ Returns True if the object has a value
        """

    def get_value(kwargs):
        """ Returns the value of this object
        """

    def value_info(kwargs):
        """ Returns a mapping describing the value of the object

        Keys are:
        ``raw_value``: the real value for this object
        ``value``: same thing as get_value()
        ``has_value``: same thing as has_value()
        ``msg``: a descriptive message informing about value requirements
        """


class IFieldIsRequiredForState(Interface):
    ### the naming of this interface should be changed, it's too specific;
    """ Objects of this type provide required for state

    The use case is this: we want to be able to interrogate various
    AT fields contained in objects if they are required for a specific state;
    we don't want to hardcode the logic that achieves this, so we make it
    extendible by adaptation. This package also provides a default
    implementation for a component that adapts AT fields -> IRequiredFor
    """
    def __call__(state):
        """ Is required for state?
        """

class IRequiredFieldsForState(Interface):
    """Should be implemented as a named adapter for objects, with the name
    being the workflow state name

    queryAdapter(context, interface=IRequiredFieldsForState, name='published')
    """

    fields = Attribute("A list of field names that are required for the state")


class IObjectReadiness(Interface):
    """ Returns info on how ready is an object to be moved to 
    a certain workflow state
    """

    checks = Attribute("A mapping of workflow state to lists of checks that "
                                                        "need to be executed")
    depends_on = Attribute("A list of objects whose marked fields "
                                                        "should be considered")

    def get_info_for(state_name):
        """ Returns a mapping containing statistics on object readiness 
        for a certain state
        """

    def is_ready_for(state_name):
        """ Returns a bool that tells is the object is ready to be transitioned 
        to the named state
        """


class IObjectArchived(Interface):
    """ A marker interface for objects that are archived
    """


class IObjectArchivator(Interface):
    """ Execute archival operations on objects
    """

    is_archived = Attribute("Is this object archived?")
    initiator = Attribute("The actor who initiated the archival")
    reason = Attribute("Reason for archival, selected from predefined list")
    custom_message = Attribute("A human-readable text reason for archival")

    # It may be useful to keep this date, as the 
    # object's ExpirationDate can be changed
    archive_date = Attribute("The date when the object was archived")

    def archive(self):
        """ Archives the object """

    def unarchive(self):
        """ Unarchives the object """
