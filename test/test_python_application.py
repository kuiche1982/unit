import unittest
import unit

class TestUnitPythonApplication(unit.TestUnitApplicationPython):

    def setUpClass():
        unit.TestUnit().check_modules('python')

    def test_python_application_variables(self):
        self.load('variables')

        body = 'Test body string.'

        resp = self.post(headers={
            'Host': 'localhost',
            'Content-Type': 'text/html',
            'Custom-Header': 'blah'
        }, body=body)

        self.assertEqual(resp['status'], 200, 'status')
        headers = resp['headers']
        self.assertRegex(headers.pop('Server'), r'Unit/[\d\.]+',
            'server header')

        date = headers.pop('Date')
        self.assertEqual(date[-4:], ' GMT', 'date header timezone')
        self.assertLess(abs(self.date_to_sec_epoch(date) - self.sec_epoch()), 5,
            'date header')

        self.assertDictEqual(headers, {
            'Content-Length': str(len(body)),
            'Content-Type': 'text/html',
            'Request-Method': 'POST',
            'Request-Uri': '/',
            'Http-Host': 'localhost',
            'Server-Protocol': 'HTTP/1.1',
            'Custom-Header': 'blah',
            'Wsgi-Version': '(1, 0)',
            'Wsgi-Url-Scheme': 'http',
            'Wsgi-Multithread': 'False',
            'Wsgi-Multiprocess': 'True',
            'Wsgi-Run-Once': 'False'
        }, 'headers')
        self.assertEqual(resp['body'], body, 'body')

    def test_python_application_query_string(self):
        self.load('query_string')

        resp = self.get(url='/?var1=val1&var2=val2')

        self.assertEqual(resp['headers']['Query-String'], 'var1=val1&var2=val2',
            'Query-String header')

    @unittest.expectedFailure
    def test_python_application_server_port(self):
        self.load('server_port')

        self.assertEqual(self.get()['headers']['Server-Port'], '7080',
            'Server-Port header')

    @unittest.expectedFailure
    def test_python_application_204_transfer_encoding(self):
        self.load('204_no_content')

        self.assertNotIn('Transfer-Encoding', self.get()['headers'],
            '204 header transfer encoding')

    def test_python_application_ctx_iter_atexit(self):
        self.skip_alerts.append(r'sendmsg.+failed')
        self.load('ctx_iter_atexit')

        resp = self.post(headers={
            'Connection': 'close',
            'Content-Type': 'text/html',
            'Host': 'localhost'
        }, body='0123456789')

        self.assertEqual(resp['status'], 200, 'ctx iter status')
        self.assertEqual(resp['body'], '0123456789', 'ctx iter body')

        self.conf({
            "listeners": {},
            "applications": {}
        })

        self.stop()

        self.assertIsNotNone(self.search_in_log(r'RuntimeError'),
            'ctx iter atexit')

    def test_python_keepalive_body(self):
        self.load('mirror')

        (resp, sock) = self.post(headers={
            'Connection': 'keep-alive',
            'Content-Type': 'text/html',
            'Host': 'localhost'
        }, start=True, body='0123456789' * 500)

        self.assertEqual(resp['body'], '0123456789' * 500, 'keep-alive 1')

        resp = self.post(headers={
            'Connection': 'close',
            'Content-Type': 'text/html',
            'Host': 'localhost'
        }, sock=sock, body='0123456789')

        self.assertEqual(resp['body'], '0123456789', 'keep-alive 2')

    def test_python_atexit(self):
        self.skip_alerts.append(r'sendmsg.+failed')
        self.load('atexit')

        self.get()

        self.conf({
            "listeners": {},
            "applications": {}
        })

        self.stop()

        self.assertIsNotNone(self.search_in_log(r'At exit called\.'), 'atexit')

    @unittest.expectedFailure
    def test_python_application_start_response_exit(self):
        self.load('start_response_exit')

        self.assertEqual(self.get()['status'], 500, 'start response exit')

    @unittest.expectedFailure
    def test_python_application_input_iter(self):
        self.load('input_iter')

        body = '0123456789'

        self.assertEqual(self.post(body=body)['body'], body, 'input iter')

    @unittest.expectedFailure
    def test_python_application_input_read_length(self):
        self.load('input_read_length')

        body = '0123456789'

        resp = self.post(headers={
            'Host': 'localhost',
            'Input-Length': '5',
            'Connection': 'close'
        }, body=body)

        self.assertEqual(resp['body'], body[:5], 'input read length lt body')

        resp = self.post(headers={
            'Host': 'localhost',
            'Input-Length': '15',
            'Connection': 'close'
        }, body=body)

        self.assertEqual(resp['body'], body, 'input read length gt body')

        resp = self.post(headers={
            'Host': 'localhost',
            'Input-Length': '0',
            'Connection': 'close'
        }, body=body)

        self.assertEqual(resp['body'], '', 'input read length zero')

        resp = self.post(headers={
            'Host': 'localhost',
            'Input-Length': '-1',
            'Connection': 'close'
        }, body=body)

        self.assertEqual(resp['body'], body, 'input read length negative')

    @unittest.expectedFailure
    def test_python_application_errors_write(self):
        self.load('errors_write')

        self.get()

        self.stop()

        self.assertIsNotNone(
            self.search_in_log(r'\[error\].+Error in application\.'),
            'errors write')

    def test_python_application_body_array(self):
        self.load('body_array')

        self.assertEqual(self.get()['body'], '0123456789', 'body array')

    def test_python_application_body_io(self):
        self.load('body_io')

        self.assertEqual(self.get()['body'], '0123456789', 'body io')

    def test_python_application_body_io_file(self):
        self.load('body_io_file')

        self.assertEqual(self.get()['body'], 'body\n', 'body io file')

    @unittest.expectedFailure
    def test_python_application_syntax_error(self):
        self.skip_alerts.append(r'Python failed to import module "wsgi"')
        self.load('syntax_error')

        self.assertEqual(self.get()['status'], 500, 'syntax error')

    def test_python_application_close(self):
        self.load('close')

        self.get()

        self.stop()

        self.assertIsNotNone(self.search_in_log(r'Close called\.'), 'close')

    def test_python_application_close_error(self):
        self.load('close_error')

        self.get()

        self.stop()

        self.assertIsNotNone(self.search_in_log(r'Close called\.'),
            'close error')

if __name__ == '__main__':
    unittest.main()
