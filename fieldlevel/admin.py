from copy import deepcopy
import re

from django.contrib import admin


class FieldLevelAdmin(admin.ModelAdmin):
    """
    A subclass of ModelAdmin that provides hooks for setting field-level 
    permissions based on object or request properties. Intended to be used as an 
    abstract base class replacement for ModelAdmin, with can_view_inline() and 
    can_view_field() customized to each use.
    """
    
    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets for the add form, modified to only display 
        fields inside fieldsets that the user has permission to view or change.
        """
        
        # Get fieldsets from the ModeAdmin object
        if self.declared_fieldsets:
            fieldsets = self.declared_fieldsets
        else:
            form = self.get_form(request, obj)
            fieldsets = form.base_fields.keys() + \
                list(self.get_readonly_fields(request, obj))
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj=obj)
        fieldsets = deepcopy(fieldsets)
        
        # Delete all fields in fieldsets that the request does not have
        # permission to view
        for fieldset in fieldsets:
            fieldset[1]['fields'] = [field for field in fieldset[1]['fields'] \
                if self.can_view_field(request, obj, field)]
        
        # Delete empty fieldsets
        for fieldset in fieldsets:
            if not fieldset[1]['fields']:
                fieldsets.remove(fieldset)
        
        return fieldsets
    
    def get_form(self, request, obj=None):
        """
        Returns a Form class (used by add_view and change_view) modified to only 
        include fields and inlines that the user has permissions to view.
        """
        form = super(PageAdmin, self).get_form(request, obj)
        
        # Remove the fields that the user does not have permission to view.
        for field_name, field in form.base_fields.items():
            if not self.can_view_field(request, obj, field_name):
                del form.base_fields[field_name]
        
        # Because inlines live outside of the normal flow of fields (i.e. are
        # not represented in self.base_fields), they need to be handled
        # separately.
        self.inline_instances = []
        for inline_class in self.inlines:
            if(self.can_view_inline(request, obj, inline_class.__name__)):
                inline_instance = inline_class(self.model, self)
                self.inline_instances.append(inline_instance)
        
        return form
    
    def can_view_inline(self, request, obj, inline_name):
        """
        Returns boolean indicating whether the user has necessary permissions to
        view the passed inline.
        """
        return True
    
    def can_view_field(self, request, obj, field_name):
        """
        Returns boolean indicating whether the user has necessary permissions to
        view the passed field.
        """
        return True