'''\
This extension is required when using :ref:`lux.js <jsapi>` javascript module.
It provides the link between AngularJS and Python.

**Required extensions**: :mod:`lux.extensions.ui`
'''
import lux
from lux import Parameter

from pulsar.apps.wsgi import MediaMixin, Html, route
from pulsar.utils.httpurl import urlparse

from .ui import add_css


class Extension(lux.Extension):

    _config = [
        Parameter('HTML5_NAVIGATION', True, 'Enable Html5 navigation'),
        Parameter('ANGULAR_UI_ROUTER', False, 'Enable Angular ui-router'),
        Parameter('ANGULAR_VIEW_ANIMATE', False,
                  'Enable Animation of ui-router views.'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar'),
        Parameter('NGMODULES', [], 'Angular module to load')
    ]


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Angular Html5 navigation

    When the :setting:`HTML5_NAVIGATION` is ``True``, this router
    does not build the ``$main`` key for the context dictionary, insteady
    it places the

        <div ng-view></div>

    tag and populate the javascript context dictionary with a sitemap
    and the ``html5mode`` flag set to ``True``.
    '''
    in_nav = True
    target = None
    title = None
    api = None
    has_content = True
    angular_view_class = 'angular-view'
    html_body_template = 'home.html'
    '''The template for the body part of the Html5 document
    '''
    ngmodules = None
    '''List of angular modules to include
    '''
    _sitemap = None

    def get(self, request):
        app = request.app
        uirouter = app.config['ANGULAR_UI_ROUTER']
        doc = request.html_document
        doc.body.data({'ng-model': 'page',
                       'ng-controller': 'Page',
                       'page': ''})
        #
        # Add info to jscontext
        jscontext = doc.jscontext
        jscontext['html5mode'] = app.config['HTML5_NAVIGATION']
        navbar = doc.jscontext.get('navbar') or {}
        navbar['collapseWidth'] = app.config['NAVBAR_COLLAPSE_WIDTH']
        jscontext['navbar'] = navbar

        context = {}
        main = self.build_main(request, context, jscontext)
        #
        ngmodules = jscontext['ngModules'] = set(jscontext.get('ngModules', ()))
        ngmodules.update(app.config['NGMODULES'])
        #
        # Using Angular Ui-Router
        if uirouter:
            jscontext.update(self.sitemap(app, ngmodules))
            jscontext['page'] = router_href(app,
                                            request.app_handler.full_route)
        elif self.ngmodules:
            ngmodules.update(self.ngmodules)

        if uirouter:
            main = self.uiview(app, main, jscontext)

        jscontext['ngModules'] = list(jscontext['ngModules'])
        context['html_main'] = main
        return app.html_response(request, self.html_body_template,
                                 context=context)

    def build_main(self, request, context):
        '''Build the context when not using ui-router navigation
        '''
        return {}

    def uiview(self, app, main, jscontext):
        '''Wrap the ``main`` html with angulat ``ui-view`` container.
        Add animation class if specified in :setting:`ANGULAR_VIEW_ANIMATE`.
        '''
        main = Html('div', main, cn='hidden')
        div = Html('div', main, cn=self.angular_view_class)
        animate = app.config['ANGULAR_VIEW_ANIMATE']
        if animate:
            div.addClass(animate)
        div.data('ui-view', 'main')
        return div.render()

    def state_template(self, app):
        '''Template for ui-router state associated with this router.
        '''
        pass

    def get_controller(self, app):
        return 'Html5'

    def angular_page(self, app, page):
        '''Callback for adding additional data to angular page object
        '''
        pass

    def sitemap(self, app, ngmodules):
        '''Build the sitemap used by angular ui-router
        '''
        root = self.root
        if root._sitemap is None:
            ngmodules.add('ui.router')
            sitemap = {'hrefs': [],
                       'pages': {},
                       'uiRouter': True,
                       'ngModules': ngmodules}
            add_to_sitemap(sitemap, app, root)
            root._sitemap = sitemap
        return root._sitemap

    def childname(self, prefix):
        return '%s%s' % (self.name, prefix) if self.name else prefix

    def instance_url(self, request, instance):
        '''Return the url for editing the ``instance``
        '''
        pass

    def wrap_html(self, request, html, span=12):
        '''Default wrapper for html loaded via angular
        '''
        return Html('div',
                    Html('div', html, cn='col-sm-%d' % span),
                    cn='row').render(request)


def router_href(app, route):
    url = '/'.join(_angular_route(route))
    if url:
        url = '/%s' % url if route.is_leaf else '/%s/' % url
    else:
        url = '/'
    site_url = app.config['SITE_URL']
    if site_url:
        p = urlparse(site_url + url)
        return p.path
    else:
        return url


def _angular_route(route):
    for is_dynamic, val in route.breadcrumbs:
        if is_dynamic:
            c = route._converters[val]
            yield '*%s' % val if c.regex == '.*' else ':%s' % val
        else:
            yield val


def add_to_sitemap(sitemap, app, router, parent=None):
    '''Add router and its children to the Html5 sitemap
    '''
    # Router variables
    if not isinstance(router, Router):
        return
    href = router_href(app, router.full_route)
    # Target
    target = router.target
    if not target and router.parent:
        if router.parent.html_body_template != router.html_body_template:
            target = '_self'
    #
    page = {'url': href,
            'name': router.name,
            'target': target,
            'template': router.state_template(app),
            'api': router.get_api_info(app),
            'controller': router.get_controller(app),
            'parent': parent}
    router.angular_page(app, page)
    sitemap['hrefs'].append(href)
    sitemap['pages'][href] = page
    if router.ngmodules:
        sitemap['ngModules'].update(router.ngmodules)
    #
    # Loop over children routes
    for child in router.routes:
        #
        # This is the first child
        if not parent:
            getmany = True
            apiname = router.name
        # In navigation
        if getattr(router, 'in_nav', False):
            add_to_sitemap(sitemap, app, child, href)