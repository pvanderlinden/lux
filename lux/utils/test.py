'''Utilities for testing Lux applications
'''
import unittest
import string
import logging
import json
from unittest import mock
from io import StringIO

from pulsar import send, get_event_loop
from pulsar.utils.httpurl import encode_multipart_formdata
from pulsar.utils.string import random_string
from pulsar.apps.test import test_timeout

import lux
from lux.core.commands.generate_secret_key import generate_secret

logger = logging.getLogger('lux.test')


def randomname(prefix=None):
    prefix = prefix or 'luxtest_'
    name = random_string(min_len=8, max_len=8, characters=string.ascii_letters)
    return ('%s%s' % (prefix, name)).lower()


def green(test_fun):
    '''Decorator to run a test function in the lux application green_pool
    if available, otherwise in the event loop executor.

    In both cases it returns a :class:`~asyncio.Future`.

    This decorator should not be used for functions returning a coroutine
    or a :class:`~asyncio.Future`.
    '''
    def _(o):
        try:
            pool = o.app.green_pool
        except AttributeError:
            pool = None
        if pool:
            return pool.submit(test_fun, o)
        else:
            loop = get_event_loop()
            return loop.run_in_executor(None, test_fun, o)

    return _


def test_app(test, config_file=None, argv=None, **params):
    '''Return an application for testing. Override if needed.
    '''
    kwargs = test.config_params.copy()
    kwargs.update(params)
    if 'SECRET_KEY' not in kwargs:
        kwargs['SECRET_KEY'] = generate_secret()
    config_file = config_file or test.config_file
    if argv is None:
        argv = []
    if '--log-level' not in argv:
        argv.append('--log-level')
        levels = test.cfg.loglevel if hasattr(test, 'cfg') else ['none']
        argv.extend(levels)

    app = lux.App(config_file, argv=argv, **kwargs).setup()
    #
    # Data mapper
    app.stdout = StringIO()
    app.stderr = StringIO()
    return app


class TestClient:
    '''An utility for simulating lux clients
    '''
    def __init__(self, app):
        self.app = app

    def run_command(self, command, argv=None, **kwargs):
        argv = argv or []
        cmd = self.app.get_command(command)
        return cmd(argv, **kwargs)

    def request_start_response(self, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, content_type=None,
                               token=None, **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        if content_type:
            headers = headers or []
            headers.append(('content-type', content_type))
        if token:
            headers = headers or []
            headers.append(('Authorization', 'Bearer %s' % token))
        request = self.app.wsgi_request(path=path, headers=headers, body=body,
                                        extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def request(self, **params):
        request, sr = self.request_start_response(**params)
        yield from self.app(request.environ, sr)
        return request

    def get(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'GET'
        return self.request(path=path, **extra)

    def post(self, path=None, body=None, content_type=None, **extra):
        extra['REQUEST_METHOD'] = 'POST'
        if body and not isinstance(body, bytes):
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
            elif content_type == 'application/json':
                body = json.dumps(body).encode('utf-8')

        return self.request(path=path, content_type=content_type,
                            body=body, **extra)

    def delete(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'DELETE'
        return self.request(path=path, **extra)


class TestMixin:
    config_file = 'tests.config'
    '''The config file to use when building an :meth:`application`'''
    config_params = {}
    '''Dictionary of parameters to override the parameters from
    :attr:`config_file`'''
    prefixdb = 'luxtest_'

    def bs(self, response):
        from bs4 import BeautifulSoup
        self.assertEqual(response.headers['content-type'],
                         'text/html; charset=utf-8')
        return BeautifulSoup(response.get_content())

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}

    def json(self, response):
        '''Get JSON object from response
        '''
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
        return json.loads(response.content[0].decode('utf-8'))


class TestCase(unittest.TestCase, TestMixin):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    apps = None

    def application(self, **params):
        '''Return an application for testing. Override if needed.
        '''
        app = test_app(self, **params)
        if self.apps is None:
            self.apps = []
        self.apps.append(app)
        return app

    def request_start_response(self, app, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        request = app.wsgi_request(path=path, headers=headers, body=body,
                                   extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def fetch_command(self, command, app=None):
        '''Fetch a command.'''
        if not app:
            app = self.application()
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd


class AppTestCase(unittest.TestCase, TestMixin):
    '''Test calss for testing applications
    '''
    odm = None
    app = None

    @classmethod
    def setUpClass(cls):
        # Create the application
        cls.dbs = {}
        cls.app = test_app(cls)
        cls.client = TestClient(cls.app)
        if hasattr(cls.app, 'odm'):
            cls.odm = cls.app.odm
            return cls.setupdb()

    @classmethod
    def tearDownClass(cls):
        if cls.odm:
            return cls.dropdb()

    @classmethod
    def dbname(cls, engine):
        if engine not in cls.dbs:
            cls.dbs[engine] = randomname(cls.prefixdb)
        return cls.dbs[engine]

    @classmethod
    @green
    def setupdb(cls):
        cls.app.odm = cls.odm.database_create(database=cls.dbname)
        logger.info('Create test tables')
        cls.app.odm().table_create()
        cls.populatedb()

    @classmethod
    @green
    def dropdb(cls):
        logger.info('Drop databases')
        cls.app.odm().close()
        cls.odm().database_drop(database=cls.dbname)

    @classmethod
    def populatedb(cls):
        pass

    def create_superuser(self, username, email, password):
        '''A shortcut for the create_superuser command
        '''
        return self.client.run_command('create_superuser',
                                       ['--username', username,
                                        '--email', email,
                                        '--password', password])


class TestServer(unittest.TestCase, TestMixin):
    app_cfg = None

    @test_timeout(30)
    @classmethod
    def setUpClass(cls):
        name = cls.__name__.lower()
        cfg = cls.cfg
        argv = [__file__, 'serve', '-b', '127.0.0.1:0',
                '--concurrency', cfg.concurrency]
        loglevel = cfg.loglevel
        cls.app = app = lux.execute_from_config(cls.config_file, argv=argv,
                                                name=name, loglevel=loglevel)
        mapper = cls.on_loaded(app)
        if mapper:
            app.params['DATASTORE'] = mapper._default_store.dns
            yield from app.get_command('create_databases')([])
            yield from app.get_command('create_tables')([])
        cls.app_cfg = yield from app._started
        cls.url = 'http://{0}:{1}'.format(*cls.app_cfg.addresses[0])

    @classmethod
    def tearDownClass(cls):
        from lux.extensions.odm import database_drop
        if cls.app_cfg is not None:
            yield from send('arbiter', 'kill_actor', cls.app_cfg.name)
            yield from database_drop(cls.app)
