from lux.extensions import admin
from lux.forms import Layout, Fieldset, Submit

from .views import PageCRUD, TemplateCRUD, PageForm, TemplateForm


#    CLASSES FOR ADMIN
class CmsAdmin(admin.CRUDAdmin):
    '''Admin views for the cms
    '''
    section = 'cms'


@admin.register(PageCRUD)
class PageAdmin(CmsAdmin):
    '''Admin views for html pages
    '''
    icon = 'fa fa-sitemap'
    form = Layout(PageCRUD._model.form,
                  Fieldset(all=True),
                  Submit('Add new page'))
    updateform = Layout(PageForm,
                        Fieldset(all=True),
                        Submit('Update page'))


@admin.register(TemplateCRUD)
class TemplateAdmin(CmsAdmin):
    icon = 'fa fa-file-code-o'
    form = Layout(TemplateCRUD._model.form,
                  Fieldset(all=True),
                  Submit('Add new template'))
    updateform = Layout(TemplateForm,
                        Fieldset(all=True),
                        Submit('Update template'))
