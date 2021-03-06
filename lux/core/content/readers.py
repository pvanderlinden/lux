import os
import imp
import mimetypes
from itertools import chain

from pulsar.apps.wsgi import String

from .contents import (Content, METADATA_PROCESSORS, slugify, is_html,
                       SkipBuild, register_reader)
from .urlwrappers import MultiValue

try:
    from markdown import Markdown
except ImportError:     # pragma    nocover
    Markdown = False

Restructured = False


def guess(value):
    return value if len(value) > 1 else value[-1]


DEFAULTS = (('priority', 1),
            ('order', 0))


@register_reader
class BaseReader(object):
    """Base class to read files.

    This class is used to process static files, and it can be inherited for
    other types of file. A Reader class must have the following attributes:

    - enabled: (boolean) tell if the Reader class is enabled. It
      generally depends on the import of some dependency.
    - file_extensions: a list of file extensions that the Reader will process.
    - extensions: a list of extensions to use in the reader (typical use is
      Markdown).

    """
    enabled = True
    file_extensions = ['']
    extensions = None
    content = Content

    def __init__(self, app, ext=None):
        self.app = app
        self.ext = ext
        self.logger = app.logger
        self.config = app.config

    def __str__(self):
        return self.__class__.__name__

    def read(self, src, path, **params):
        """Parse content and metadata of markdown files"""
        with open(src, 'rb') as text:
            raw = text.read()
        return self.process(raw, path, src=src, **params)

    def process(self, raw, path, src=None, **params):
        ct, encoding = None, None
        if src:
            ct, encoding = mimetypes.guess_type(src)
        body = raw
        if is_html(ct):
            if isinstance(raw, bytes):
                body = raw.decode(encoding=encoding or 'utf-8')
        else:
            ct = ct or 'application/octet-stream'
            if self.ext and not path.endswith('.%s' % self.ext):
                path = '%s.%s' % (path, self.ext)
        metadata = {'content_type': ct}
        return self.post_process(body, metadata, path, src=src, **params)

    def post_process(self, body, meta_input, path, content=None,
                     meta=None, **params):
        """Return the dict containing document metadata
        """
        cfg = self.config
        head_meta = {}
        meta_input = meta_input.items()
        meta = meta.items() if meta else ()
        meta_input = chain(DEFAULTS, meta, meta_input)
        meta = {}
        as_list = MultiValue()
        for key, values in meta_input:
            key = slugify(key, separator='_')
            if not isinstance(values, (list, tuple)):
                values = (values,)
            if key not in METADATA_PROCESSORS:
                bits = key.split('_', 1)
                if len(bits) > 1:
                    k = ':'.join(bits[1:])
                    if bits[0] == 'meta':
                        meta[k] = guess(as_list(values, cfg))
                        continue
                    if bits[0] == 'head':
                        head_meta[k] = guess(as_list(values, cfg))
                        continue
                    if bits[0] == 'og' or bits[0] == 'twitter':
                        k = ':'.join(bits)
                        head_meta[k] = guess(as_list(values, cfg))
                        continue
                self.logger.warning("Unknown meta '%s' in '%s'", key, path)
            #
            elif values:
                # Remove default values if any
                proc = METADATA_PROCESSORS[key]
                meta[key] = proc(values, cfg)
        content = content or self.content
        if meta.get('priority') == '0':
            content = content.as_draft()
            head_meta['robots'] = ['noindex', 'nofollow']
        meta['head'] = head_meta
        if params:
            pass
        return content(self.app, body, meta, path, **params)


@register_reader
class MarkdownReader(BaseReader):
    """Reader for Markdown files"""

    enabled = bool(Markdown)
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def __init__(self, *args, **kwargs):
        super(MarkdownReader, self).__init__(*args, **kwargs)
        self.extensions = list(self.config['MD_EXTENSIONS'])
        if 'meta' not in self.extensions:
            self.extensions.append('meta')

    def process(self, raw, path, src=None, **params):
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        self._md = md = Markdown(extensions=self.extensions)
        raw = '%s\n\n%s' % (raw, self.links())
        body = md.convert(raw)
        meta = self._md.Meta
        meta['content_type'] = 'text/html'
        return self.post_process(body, meta, path, src=src, **params)

    def links(self):
        links = self.app.config.get('_MARKDOWN_LINKS_')
        if links is None:
            links = []
            for name, href in self.app.config['LINKS'].items():
                title = None
                if isinstance(href, dict):
                    title = href.get('title')
                    href = href['href']
                md = '[%s]: %s "%s"' % (name, href, title or name)
                links.append(md)
            links = '\n'.join(links)
            self.app.config['_MARKDOWN_LINKS_'] = links
        return links


@register_reader
class PythonReader(BaseReader):
    '''Reader for Python template generator files
    '''
    file_extensions = ['py']

    def read(self, src, path, **params):
        name = os.path.basename(src).split('.')[0]
        mod = imp.load_source(name, src)
        if not hasattr(mod, 'template'):
            raise SkipBuild
        return self.process(mod.template(), path, src=src, **params)

    def process(self, raw, path, **params):
        if isinstance(raw, String):
            ct = raw._content_type
            body = raw.render()
        else:
            body = raw
            ct = 'text/plain'
        metadata = {'content_type': [ct]}
        return self.post_process(body, metadata, path, **params)


@register_reader
class RestructuredReader(BaseReader):
    enabled = bool(Restructured)
    file_extensions = ['rst']

    def process(self, raw, path, **params):
        raw = raw.decode('utf-8')
        re = Restructured(raw)
        body = re.convert()
        return self.post_process(body, re.Meta, path, **params)
