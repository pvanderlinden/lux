import os
import stat
from datetime import datetime, date
from collections import Mapping

from dateutil.parser import parse as parse_date

from pulsar import HttpException, Http404
from pulsar.utils.slugify import slugify
from pulsar.utils.structures import AttributeDictionary, mapping_iterator
from pulsar.utils.pep import to_string

from lux.utils import iso8601, absolute_uri

from ..cache import Cacheable, cached
from .urlwrappers import (URLWrapper, Processor, MultiValue, Tag, Author,
                          Category)


class SkipBuild(Http404):
    pass


class BuildError(Http404):
    pass


class Unsupported(HttpException):
    status = 415


no_draft_field = ('date', 'category')


READERS = {}


CONTENT_EXTENSIONS = {'text/html': 'html',
                      'text/plain': 'txt',
                      'text/css': 'css',
                      'application/json': 'json',
                      'application/javascript': 'js',
                      'application/xml': 'xml'}

HEAD_META = ('title', 'description', 'author', 'keywords')

METADATA_PROCESSORS = dict(((p.name, p) for p in (
    Processor('name'),
    Processor('slug'),
    Processor('title'),
    # Description, if not head_description available it will also be used as
    # description in head meta.
    Processor('description'),
    # An optional image url which can be used to identify the page
    Processor('image'),
    Processor('date', lambda x, cfg: parse_date(x)),
    Processor('status'),
    Processor('priority', lambda x, cfg: int(x)),
    Processor('order', lambda x, cfg: int(x)),
    MultiValue('keywords', Tag),
    MultiValue('category', Category),
    MultiValue('author', Author),
    MultiValue('require_css'),
    MultiValue('require_js'),
    MultiValue('require_context'),
    Processor('content_type'),
    Processor('template'),
    Processor('template-engine')
)))


def modified_datetime(src):
    stat_src = os.stat(src)
    return datetime.fromtimestamp(stat_src[stat.ST_MTIME])


def is_html(content_type):
    return content_type == 'text/html'


def is_text(content_type):
    return content_type in CONTENT_EXTENSIONS


def page_info(data, *include_keys):
    '''Yield only keys which are not associated with a dictionary
    unless they are included in ``included_keys``
    '''
    for key, value in data.items():
        if not isinstance(value, dict) or key in include_keys:
            yield key, value


def register_reader(cls):
    for extension in cls.file_extensions:
        READERS[extension] = cls
    return cls


def get_reader(app, src):
    bits = src.split('.')
    ext = bits[-1] if len(bits) > 1 else None
    Reader = READERS.get(ext) or READERS['']
    if not Reader.enabled:
        raise BuildError('Missing dependencies for %s' % Reader.__name__)
    return Reader(app, ext)


class Content(Cacheable):
    '''A class for managing a file-based content
    '''
    template = None
    template_engine = None

    def __init__(self, app, content, metadata, path, src=None, **params):
        self._app = app
        self._content = content
        self._path = path
        self._src = src
        self._meta = AttributeDictionary(params)
        self._update_meta(metadata)
        if not self._meta.modified:
            if src:
                self._meta.modified = modified_datetime(src)
            else:
                self._meta.modified = datetime.now()
        self._meta.name = slugify(self._path, separator='_')

    @property
    def app(self):
        return self._app

    @property
    def content_type(self):
        return self._meta.content_type

    @property
    def is_text(self):
        return self._meta.content_type in CONTENT_EXTENSIONS

    @property
    def is_html(self):
        return is_html(self._meta.content_type)

    @property
    def suffix(self):
        return CONTENT_EXTENSIONS.get(self._meta.content_type)

    @property
    def path(self):
        return self._path

    @property
    def reldate(self):
        return self._meta.date or self._meta.modified

    @property
    def year(self):
        return self.reldate.year

    @property
    def month(self):
        return self.reldate.month

    @property
    def month2(self):
        return self.reldate.strftime('%m')

    @property
    def month3(self):
        return self.reldate.strftime('%b').lower()

    @property
    def id(self):
        if self.is_html:
            return '%s.json' % self._path

    def cache_key(self, app):
        return self._meta.name

    def __repr__(self):
        return self._path
    __str__ = __repr__

    def key(self, name=None):
        '''The key for a context dictionary
        '''
        name = name or self.name
        suffix = self.suffix
        return '%s_%s' % (suffix, name) if suffix else name

    def context(self, context=None):
        '''Extract the context dictionary for server side template rendering
        '''
        ctx = dict(self._flatten(self._meta))
        if context:
            ctx.update(context)
        return ctx

    def urlparams(self, names=None):
        urlparams = {}
        if names:
            for name in names:
                value = self._meta.get(name) or getattr(self, name, None)
                if value in (None, ''):
                    if name == 'id':
                        raise SkipBuild
                    elif names:
                        raise KeyError("%s could not obtain url variable '%s'"
                                       % (self, name))
                urlparams[name] = value
        return urlparams

    def render(self, context=None):
        '''Render the content
        '''
        if self.is_html:
            context = self.context(context)
            content = self._engine(self._content, context)
            if self.template:
                template = self._app.template_full_path(self.template)
                if template:
                    context[self.key('main')] = content
                    with open(template, 'r') as file:
                        template_str = file.read()
                    content = self._engine(template_str, context)
            return content
        else:
            return self._content

    def raw(self, request):
        return self._content

    @cached
    def json(self, request):
        '''Convert the content into a Json dictionary for the API
        '''
        if self.is_html:
            context = self._app.context(request)
            context = self.context(context)
            #
            data = self._to_json(request, self._meta)
            text = data.get(self.suffix) or {}
            data[self.suffix] = text
            text['main'] = self.render(context)
            #
            head = {}
            for key in HEAD_META:
                value = data.get(key)
                if value:
                    head[key] = value
            #
            if 'head' in data:
                head.update(data['head'])

            data['url'] = request.absolute_uri(self._path)
            data['head'] = head
            return data

    def html(self, request):
        '''Build the ``html_main`` key for this content and set
        content specific values to the ``head`` tag of the
        HTML5 document.
        '''
        if not self.is_html:
            raise Unsupported
        # The JSON data for this page
        data = self.json(request)
        doc = request.html_document
        doc.jscontext['page'] = dict(page_info(data))
        #
        image = absolute_uri(request, data.get('image'))
        doc.meta.update({'og:image': image,
                         'og:published_time': data.get('date'),
                         'og:modified_time': data.get('modified')})
        doc.meta.update(data['head'])
        #
        if not request.config.get('HTML5_NAVIGATION'):
            for css in data.get('require_css') or ():
                doc.head.links.append(css)
            doc.head.scripts.require.extend(data.get('require_js') or ())
        #
        if request.cache.uirouter is False:
            doc.head.scripts.require.extend(data.get('require_js') or ())

        self.on_html(doc)
        return data[self.suffix]['main']

    def on_html(self, doc):
        pass

    @classmethod
    def as_draft(cls):
        mp = tuple((a for a in cls.mandatory_properties
                    if a not in no_draft_field))
        return cls.__class__('Draft', (cls,), {'mandatory_properties': mp})

    # INTERNALS
    def _update_meta(self, metadata):
        meta = self._meta
        meta.site = {}
        for name in ('template_engine', 'template'):
            default = getattr(self, name)
            value = metadata.pop(name, default)
            meta.site[name] = value
            setattr(self, name, value)

        context = self.context(self.app.config)
        self._engine = self._app.template_engine(self.template_engine)
        meta.update(((key, self._render_meta(value, context))
                    for key, value in metadata.items()))

    def _flatten(self, meta):
        for key, value in mapping_iterator(meta):
            if isinstance(value, Mapping):
                for child, value in self._flatten(value):
                    yield '%s_%s' % (key, child), value
            else:
                yield key, self._to_string(value)

    def _to_string(self, value):
        if isinstance(value, Mapping):
            raise BuildError('A dictionary found when coverting to string')
        elif isinstance(value, (list, tuple)):
            return ', '.join(self._to_string(v) for v in value)
        elif isinstance(value, date):
            return iso8601(value)
        else:
            return to_string(value)

    def _render_meta(self, value, context):
        if isinstance(value, Mapping):
            return dict(((k, self._render_meta(v, context))
                         for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._render_meta(v, context) for v in value]
        elif isinstance(value, str):
            return self._engine(to_string(value), context)
        else:
            return value

    def _to_json(self, request, value):
        if isinstance(value, Mapping):
            return dict(((k, self._to_json(request, v))
                         for k, v in value.items()))
        elif isinstance(value, (list, tuple)):
            return [self._to_json(request, v) for v in value]
        elif isinstance(value, date):
            return iso8601(value)
        elif isinstance(value, URLWrapper):
            return value.to_json(request)
        else:
            return value
