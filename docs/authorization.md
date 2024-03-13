# Authentication and Authorization

Every view in Flow Forge is protected in production settings by default.

In order to access the views one of 3 conditions need to be met:

- DEBUG = True in the projects settings.py 
- User is a superuser (this can be overridden to False if required using the decorator)
- User is part of a Group that has the ```Django_Flow_Forge | flow | Can access admin``` permission which can be assigned via the Django Admin or programatically (please search via the web if this process is unfamiliar).

If you end up writing custom views with your Flows then you can wrap your own views with a handy decorator:

```from django_flow_forge.authorization import user_has_permission```

If someone requires a Class mixin this can be imported from:

```from django_flow_forge.authorization import FlowForgePermissionMixin```