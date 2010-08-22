A subclass of ModelAdmin that provides hooks for setting field-level permissions based on object or request properties.

Installation
============

As it is available on the Python Package Index, you can install django-fieldlevel-permissions using your favorite package manager::

    pip install django-fieldlevel-permissions
    
    easy_install django-fieldlevel-permissions

You can also install directly from the git master branch using the pip package manager::

    pip install git+http://github.com/cpharmston/django-fieldlevel-permissions.git#egg=fieldlevel

Or you can download django-fieldlevel-permissions and install locally::

    setup.py install

Usage
=====
In your admin classes, inherit from ``fieldlevel.admin.FieldLevelAdmin`` rather than ``django.contrib.admin.ModelAdmin``. This provides you with two overridable methods, ``can_change_field`` and ``can_change_inline``, each of which have access to the request and the object being edited, and should return a boolean indicating whether or not the user should see the field in the admin.

It is important to note that any potentially hidden fields must be ``blank=True``, have a default set, or must have handling code in a `custom save method <http://docs.djangoproject.com/en/dev/topics/db/models/#overriding-predefined-model-methods>`_.
 
In the following example, we will demonstrate this by modifying these Models and ModelAdmin to achieve a few tasks:

1. Only superusers will be able to modify the post and comment dates
2. Only users with appropriate permissions will be able to approve comments
3. The "approved" field will not appear in the comment add view
4. Only users with appropriate permissions will be able to edit blog post meta tags.

::

    # models.py
    
    from django.contrib.auth.models import User
    
    class BlogPost(models.Model):
        title = models.CharField(max_length=128)
        text = models.TextField()
        post_date = models.DateField(blank=True)
        author = models.ForeignKey(User)
        
        class Meta:
            permissions = (
                ("can_edit_meta", "Can edit meta tags"),
            )

    
    class Comment(models.Model):
        blogpost = models.ForeignKey(BlogPost)
        author = models.ForeignKey(User)
        text = models.TextField()
        comment_date = models.DateField(blank=True)
        approved = models.BooleanField(default=False)
        
        class Meta:
            permissions = (
                ("can_approve_comments", "Can approve comments"),
            )
    
    # admin.py
    
    from django.contrib import admin
    from metatags.admin import MetaTagInline
    from models import BlogPost, Comment
    
    class BlogPostAdmin(admin.ModelAdmin):
        inlines = [
            MetaTagInline,
        ]
    
    admin.site.register(BlogPost, BlogPostAdmin)
    admin.site.register(Comment)

First, we will set the stage by changing the Admin classes to inherit from FieldLevelAdmin, rather than admin.ModelAdmin::

    from fieldlevel.admin import FieldLevelAdmin
    
    class BlogPostAdmin(FieldLevelAdmin):
        ...
    
    class CommentAdmin(FieldLevelAdmin):
        ...
    
    admin.site.register(BlogPost, BlogPostAdmin)
    admin.site.register(Comment, CommentAdmin)

Next, we'll tackle the first task, only allowing superusers to modify the post and comment dates. We will do this by overriding the can_change_field method for each respective admin class::

    class BlogPostAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
            
            if field_name == "post_date":
                if not request.user.is_superuser:
                    return False
            
            return True
    
    class CommentAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
        
            if field_name == "comment_date":
                if not request.user.is_superuser:
                    return False
            
            return True

Next, we'll extend our custom can_change_field method on CommentAdmin to allow users with appropriate permissions to approve comments::

    class CommentAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
            
            if field_name == "comment_date":
                if not request.user.is_superuser:
                    return False
            
            if field_name == 'approved':
                if not request.user.has_perm('blog.can_approve_comments'):
                    return False
            
            return True

Now, we'll prevent the 'approved' field on the Comment model from appearing in the add view::

    class CommentAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
            
            if field_name == "comment_date":
                if not request.user.is_superuser:
                    return False
            
            if field_name == 'approved':
                if not request.user.has_perm('blog.can_approve_comments'):
                    return False
                if obj is None:
                    return False
            
            return True

Finally, we'll only allow users with appropriate permissions to edit blog post meta tags::

    class BlogPostAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
            
            if field_name == "post_date":
                if not request.user.is_superuser:
                    return False
            
            return True
        
        def can_change_inline(self, request, obj, inline_name):
            
            if inline_name == 'MetaTagInline':
                if not request.user.has_perm('blog.can_edit_meta'):
                    return False
            
            return True

That's it! Our final admin.py::

    from django.contrib import admin
    from metatags.admin import MetaTagInline
    from models import BlogPost, Comment
    
    class CommentAdmin(FieldLevelAdmin):
        
        def can_change_field(self, request, obj, field_name):
            
            if field_name == "comment_date":
                if not request.user.is_superuser:
                    return False
            
            if field_name == 'approved':
                if not request.user.has_perm('blog.can_approve_comments'):
                    return False
                if obj is None:
                    return False
            
            return True
    
    class BlogPostAdmin(FieldLevelAdmin):
        inlines = [
            MetaTagInline,
        ]

        def can_change_field(self, request, obj, field_name):
            
            if field_name == "post_date":
                if not request.user.is_superuser:
                    return False
            
            return True
        
        def can_change_inline(self, request, obj, inline_name):
            
            if inline_name == 'MetaTagInline':
                if not request.user.has_perm('blog.can_edit_meta'):
                    return False
            
            return True
    
    admin.site.register(BlogPost, BlogPostAdmin)
    admin.site.register(Comment, CommentAdmin)