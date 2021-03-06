import unittest
import lux.extensions.smtp.views as views
from unittest.mock import MagicMock, patch


class EmptyClass:
    pass


get_html_return_value = 'return val'
http_response_return_value = 'another return val'
tojson_return_value = 'tojson dummy data'
dummy_rule = '/a_rule'
empty_request = {}


class ContactRouterTestCase(unittest.TestCase):
    def setUp(self):
        self.cr = views.ContactRouter(dummy_rule)

    def _reset_mocks(self):
        self.request_mock.reset_mock()
        self.string_mock.http_response.reset_mock()

    def _create_mocks(self, JsonMock, is_form_valid=True):
        self.request_mock = MagicMock()
        self.request_mock.data_and_files.return_value = ({}, '')

        self.request_mock.app.config = dict(ENQUIRY_EMAILS=[
            {
                'sender': 'FOO Technologies <noreply@foo.com>',
                'to': 'info@foo.com',
                'subject': 'website enquiry form',
                'message': ('Enquiry from: {name} <{email}>\n\n'
                            'Message:\n'
                            '{body}\n')
            },
        ])

        form_mock = MagicMock()
        FormMock = MagicMock()
        form_mock.is_valid.return_value = is_form_valid
        form_mock.cleaned_data = dict(name='Mr Blog',
                                      email='mr@blog.com',
                                      body='Here is my message to you')
        form_mock.tojson.return_value = tojson_return_value
        FormMock.return_value = form_mock
        views.ContactForm = FormMock

        self.string_mock = EmptyClass()
        self.string_mock.http_response = MagicMock(
            return_value=http_response_return_value)
        JsonMock.return_value = self.string_mock

    def test_get_html(self):
        mock_form = EmptyClass()
        mock_form.as_form = MagicMock(return_value=get_html_return_value)
        views.HtmlContactForm = MagicMock(return_value=mock_form)

        actual_return_value = self.cr.get_html(empty_request)

        self.assertEqual(get_html_return_value,
                         actual_return_value,
                         msg='get_html return value')
        views.HtmlContactForm.assert_called_once_with(empty_request)
        mock_form.as_form.assert_called_once_with(action=dummy_rule)

    def test_post_one_email_form_valid(self):
        with patch('lux.extensions.smtp.views.Json') as JsonMock:
            self._create_mocks(JsonMock, is_form_valid=True)

            self.cr.post(self.request_mock)
            mock = self.request_mock
            mock.app.email_backend.send_mail.assert_called_once_with(
                sender='FOO Technologies <noreply@foo.com>',
                to='info@foo.com',
                subject='website enquiry form',
                message=('Enquiry from: Mr Blog <mr@blog.com>\n\n'
                         'Message:\n'
                         'Here is my message to you\n')
            )

            JsonMock.assert_called_once_with(
                dict(success=True, message="Message sent"))
            self.string_mock.http_response.assert_called_once_with(
                self.request_mock)

            self._reset_mocks()

    def test_post_one_email_form_invalid(self):
        with patch('lux.extensions.smtp.views.Json') as JsonMock:
            self._create_mocks(JsonMock, is_form_valid=False)

            self.cr.post(self.request_mock)

            JsonMock.assert_called_once_with(tojson_return_value)
            self.string_mock.http_response.assert_called_once_with(
                self.request_mock)

            self._reset_mocks()
