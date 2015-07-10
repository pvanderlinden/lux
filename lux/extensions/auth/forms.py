import json

from lux import forms
from lux.extensions import odm
from lux.extensions.rest.forms import PasswordForm
from lux.extensions.rest.policy import validate_policy


class PermissionForm(forms.Form):
    model = 'permission'
    id = forms.HiddenField(required=False)
    name = forms.CharField()
    description = forms.TextField()
    policy = forms.JsonField(text_edit=json.dumps({'mode': 'json'}))

    def clean(self):
        policy = self.cleaned_data['policy']
        self.cleaned_data['policy'] = validate_policy(policy)


PermissionModel = odm.RestModel('permission', PermissionForm,
                                repr_field='name')


class GroupForm(forms.Form):
    model = 'group'
    id = forms.HiddenField(required=False)
    name = forms.CharField()
    permissions = odm.RelationshipField(PermissionModel,
                                        multiple=True,
                                        required=False)

    def clean_name(self, value):
        value = value.lower()
        odm = self.request.app.odm()
        with odm.begin() as session:
            query = session.query(odm.group).filter_by(name=value)
            if query.count():
                raise forms.ValidationError('group %s already available'
                                            % value)
        return value


GroupModel = odm.RestModel('group', GroupForm, repr_field='name')


class UserForm(forms.Form):
    id = forms.HiddenField(required=False)
    username = forms.CharField()
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()
    joined = forms.DateTimeField(readonly=True, required=False)
    groups = odm.RelationshipField(GroupModel,
                                   multiple=True,
                                   required=False)


UserModel = odm.RestModel('user', UserForm,
                          repr_field='username',
                          exclude=('password',),
                          columns=('full_name',))


class CreateUserForm(PasswordForm):
    '''Form for creating a new user form username, email and password
    '''
    model = 'user'
    username = forms.SlugField(required=True,
                               validator=odm.UniqueField(),
                               minlength=6,
                               maxlength=30)
    email = forms.EmailField(required=True,
                             validator=odm.UniqueField())
