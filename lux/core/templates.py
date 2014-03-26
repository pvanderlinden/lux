'''
Template
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Template
   :members:
   :member-order: bysource


Context
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Context
   :members:
   :member-order: bysource


GridTemplate
=============

.. autoclass:: GridTemplate
   :members:
   :member-order: bysource


Row
=============

.. autoclass:: Row
   :members:
   :member-order: bysource

Column
=============

.. autoclass:: Column
   :members:
   :member-order: bysource
'''
from itertools import chain

from .wrappers import Html, AttributeDictionary


__all__ = ['Template', 'Context', 'ColumnTemplate', 'RowTemplate',
           'GridTemplate', 'PageTemplate']


class Template(object):
    '''A factory of :class:`.Html` objects.

    ::

        >>> simple = Template(Context('foo', tag='span'), tag='div')
        >>> html = simple(cn='test', context={'foo': 'bla'})
        >>> html.render()
        <div class='test'><span data-context='foo'>bla</span></div>

    .. attribute:: key

        An optional string which identify this :class:`Template` within
        other templates.

    .. attribute:: children

        List of :class:`Template` objects which are rendered as children
        of this :class:`Template`

    .. attribute:: parameters

        An attribute dictionary containing all key-valued parameters.

        it is initialised by the :meth:`init_parameters` method at the end
        of initialisation.
    '''
    key = None
    tag = None
    classes = None

    def __init__(self, *children, **parameters):
        if 'key' in parameters:
            self.key = parameters.pop('key')
        if not children:
            children = [self.child_template()]
        new_children = []
        for child in children:
            child = self.child_template(child)
            if child:
                new_children.append(child)
        self.children = new_children
        self.init_parameters(**parameters)

    def __repr__(self):
        return '%s(%s)' % (self.key or self.__class__.__name__, self.tag or '')

    def __str__(self):
        return self.__repr__()

    def child_template(self, child=None):
        return child

    def init_parameters(self, tag=None, **parameters):
        '''Called at the and of initialisation.

        It fills the :attr:`parameters` attribute.
        It can be overwritten to customise behaviour.
        '''
        self.tag = tag or self.tag
        self.parameters = AttributeDictionary(parameters)

    def __call__(self, request=None, context=None, children=None, **kwargs):
        '''Create an Html element from this template.'''
        c = []
        if context is None:
            context = {}
        for child in self.children:
            child = child(request, context, **kwargs)
            c.append(self.post_process_child(child, **kwargs))
        if children:
            c.extend(children)
        return self.html(request, context, c, **kwargs)

    def html(self, request, context, children, **kwargs):
        '''Create the :class:`Html` instance.

        This method is invoked at the end of the ``__call__`` method with
        a list of ``children`` elements and a ``context`` dictionary.
        This method shouldn't be accessed directly.

        :param request: a client request, can be ``None``.
        :param context: a dictionary of :class:`Html` or strings to include.
        :param children: list of children elements.
        :param kwargs: additional parameters used when initialising the
            :attr:`Html` for this template.
        :return: an :class:`Html` object.
        '''
        params = self.parameters
        if kwargs:
            params = dict(params)
            params.update(kwargs)
        html = Html(self.tag, *children, **params)
        html.maker = self
        return html.addClass(self.classes)

    def get(self, key):
        '''Retrieve a children :class:`Template` with :attr:`Template.key`
equal to ``key``. The search is done recursively and the first match is
returned. If not available return ``None``.'''
        for child in self.children:
            if child.key == key:
                return child
        for child in self.children:
            elem = child.get(key)
            if elem is not None:
                return elem

    def post_process_child(self, child, **parameters):
        return child


class Context(Template):
    '''A specialised :class:`Template` which uses the :attr:`Template.key`
    to extract content from the ``context`` dictionary passed to the template
    callable method.

    :param key: initialise the :attr:`Template.key` attribute. It must be
        provided.

    Fore example::

        >>> from lux import Context
        >>> template = Context('foo', tag='div')
        >>> template.key
        'foo'
        >>> html = template(context={'foo': 'pippo'})
        >>> html.render()
        <div>pippo</div>
    '''
    def __init__(self, key, *children, **params):
        params['key'] = key
        params['context'] = key
        super(Context, self).__init__(*children, **params)

    def html(self, request, context, children, **kwargs):
        html = super(Context, self).html(request, context, children, **kwargs)
        if context:
            html.append(context.get(self.key))
        return html


class ColumnTemplate(Template):
    '''A column can have one or more :class:`Block`.
    '''
    tag = 'div'
    classes = 'column'

    def __init__(self, *children, **params):
        self.span = params.pop('span', 1)
        super(ColumnTemplate, self).__init__(*children, **params)
        if self.span > 1:
            raise ValueError('Column span "%s" greater than one!' % self.span)


class RowTemplate(Template):
    '''A :class:`.RowTemplate` is a container of :class:`.ColumnTemplate`
    elements.

    :param column: Optional parameter which set the :attr:`column` attribute.

    .. attribute:: column

        It can be either 12 or 24 and it indicates the number of column
        spans available.

        Default: 12
    '''
    tag = 'div'
    columns = 12

    def __init__(self, *children, **params):
        self.columns = params.pop('columns', self.columns)
        self.classes = 'grid%s row' % self.columns
        super(RowTemplate, self).__init__(*children, **params)

    def child_template(self, child=None):
        if not isinstance(child, ColumnTemplate):
            child = ColumnTemplate(child)
        span = int(child.span * self.columns)
        child.classes += ' span%s' % span
        return child


class GridTemplate(Template):
    '''A container of :class:`.RowTemplate` or other templates.

    :parameter fixed: optional boolean flag to indicate if the grid is
        fixed (html class ``grid fixed``) or fluid (html class ``grid fluid``).
        If not specified the grid is considered fluid (it changes width when
        the browser window changes width).

    '''
    tag = 'div'

    def html(self, request, context, children, **kwargs):
        html = super(GridTemplate, self).html(request, context, children,
                                              **kwargs)
        cn = 'grid fixed' if self.parameters.fixed else 'grid fluid'
        return html.addClass(cn)

    def child_template(self, child=None):
        if not isinstance(child, (Row, CmsContext)):
            child = Row(child)
        return child


class PageTemplate(Template):
    '''The main :class:`.Template` of the content management system extension.

    The template renders the inner part of the HTML ``body`` tag.
    A page template is created by including the page components during
    initialisation, for example::

        from lux.extensions.cms.grid import PageTemplate

        head_body_foot = PageTemplate(
            Row()
            GridTemplate(CmsContext('content')),
            GridTemplate(CmsContext('footer', all_pages=True)))
    '''
    tag = 'div'
    classes = 'cms-page'

    def __init__(self, *children, **params):
        params['role'] = 'page'
        super(PageTemplate, self).__init__(*children, **params)

    def html(self, request, context, children, **kwargs):
        html = super(PageTemplate, self).html(request, context, children,
                                              **kwargs)
        if request:
            site_contents = []
            ids = context.get('content_ids')
            if ids:
                contents = yield from request.models.content.filter(id=ids).all()
                for content in contents:
                    for elem in ids.get(content.id, ()):
                        self.apply_content(elem, content)
            doc = request.html_document
            doc.head.scripts.require('cms')
        return html

    def apply_content(self, elem, content):
        elem.data({'id': content.id, 'content_type': content.content_type})
        for name, value in chain((('title', content.title),
                                  ('keywords', content.keywords)),
                                 content.data.items()):
            if isinstance(value, str):
                elem.append(Html('div', value, field=name))
            else:
                elem.data(name, value)
