'''
Extension for an Admin Web inteface.

In order to use the Admin interface, the :setting:`ADMIN_URL`
needs to be specified.
'''
import lux
from lux import Parameter, RedirectRouter

from .admin import Admin, AdminModel, CRUDAdmin, adminMap, register, is_admin
from .sidebar import add_css


__all__ = ['Admin', 'AdminModel', 'CRUDAdmin', 'register',
           'adminMap', 'add_css']


class Extension(lux.Extension):
    '''Admin site for database data
    '''
    _config = [
        Parameter('ADMIN_URL', 'admin',
                  'Admin site url', True),
        Parameter('ADMIN_SECTIONS', {},
                  'Admin sections information')]

    def middleware(self, app):
        admin = app.config['ADMIN_URL']
        if admin:
            app.require('lux.extensions.rest')
            self.admin = admin = Admin(admin)
            middleware = []
            all = app.module_iterator('admin', is_admin, '__admins__')
            for AdminRouterCls in all:
                if not AdminRouterCls._model:
                    continue
                route = AdminRouterCls()
                admin.add_child(route)
                path = route.path()
                if not path.endswith('/'):
                    middleware.append(RedirectRouter('%s/' % path, path))
            middleware.append(admin)
            return middleware
