from unittest import TestCase
import unittest
from mock import patch

from pact.verifier import Verifier
from pact.verify_wrapper import VerifyWrapper

PACT_FILE = 'test.pact'

def assertVerifyCalled(mock_wrapper, *pacts, **options):
    tc = unittest.TestCase()
    tc.assertEqual(mock_wrapper.call_count, 1)

    mock_wrapper.assert_called_once_with(*pacts, **options)

class VerifierPactsTestCase(TestCase):

    def setUp(self):
        super(VerifierPactsTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.verifier = Verifier(provider='test_provider',
                                 provider_base_url="http://localhost:8888")

        self.mock_wrapper = patch.object(
            VerifyWrapper, 'call_verify').start()

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch('pact.verifier.path_exists', return_value=True)
    def test_verifier_with_provider_and_files(self, mock_path_exists, mock_wrapper):
        mock_wrapper.return_value = (True, 'some logs')

        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        assertVerifyCalled(mock_wrapper,
                           'path/to/pact1',
                           'path/to/pact2',
                           provider='test_provider',
                           provider_base_url='http://localhost:8888',
                           log_level='INFO',
                           verbose=False)

    def test_validate_on_publish_results(self):
        self.assertRaises(Exception, self.verifier.verify_pacts, 'path/to/pact1', publish=True)

    @patch('pact.verifier.path_exists', return_value=True)
    @unittest.skip("demonstrating skipping")
    def test_publish_on_success(self, mock_path_exists):
        self.mock_wrapper.return_value = (True, 'some logs')

        result = self.verifier.verify_pacts('path/to/pact1', publish=True, publish_version='1.0.0')
        print(result)  # todo

    @patch('pact.verifier.path_exists', return_value=True)
    @patch('pact.verifier.expand_directories', return_value='./pacts/consumer-provider.json')
    @patch('pact.verifier.rerun_command')
    @unittest.skip('should be in wrapper now')
    def test_rerun_command_called(self, mock_rerun_cmd, mock_expand_dirs, mock_path_exists):
        self.mock_wrapper.return_value = (True, 'some logs')

        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        mock_rerun_cmd.assert_called_once()

    @patch('pact.verifier.path_exists', return_value=False)
    def test_raises_error_on_missing_pact_files(self, mock_path_exists):
        self.assertRaises(Exception,
                          self.verifier.verify_pacts,
                          'path/to/pact1', 'path/to/pact2')

        mock_path_exists.assert_called_with('path/to/pact2')

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify", return_value=(0, None))
    @patch('pact.verifier.expand_directories', return_value=['./pacts/pact1', './pacts/pact2'])
    @patch('pact.verifier.path_exists', return_value=True)
    def test_expand_directories_called_for_pacts(self, mock_path_exists, mock_expand_dir, mock_wrapper):
        output, _ = self.verifier.verify_pacts('path/to/pact1',
                                               'path/to/pact2')

        mock_expand_dir.assert_called_once()


class VerifierBrokerTestCase(TestCase):

    def setUp(self):
        super(VerifierBrokerTestCase, self).setUp()
        self.addCleanup(patch.stopall)
        self.verifier = Verifier(provider='test_provider',
                                 provider_base_url="http://localhost:8888")

        self.mock_wrapper = patch.object(
            VerifyWrapper, 'call_verify').start()
        self.broker_username = 'broker_username'
        self.broker_password = 'broker_password'
        self.broker_url = 'http://broker'

        self.default_opts = {
            'broker_username': self.broker_username,
            'broker_password': self.broker_password,
            'broker_url': self.broker_url,
            'broker_token': 'token'
        }

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    def test_verifier_with_broker(self, mock_wrapper):

        mock_wrapper.return_value = (True, 'ddf')

        output, _ = self.verifier.verify_with_broker(**self.default_opts)

        self.assertTrue(output)
        assertVerifyCalled(mock_wrapper,
                           provider='test_provider',
                           provider_base_url='http://localhost:8888',
                           broker_password=self.broker_password,
                           broker_username=self.broker_username,
                           broker_token='token',
                           broker_url=self.broker_url,
                           log_level='INFO',
                           verbose=False)

    @patch("pact.verify_wrapper.VerifyWrapper.call_verify")
    @patch('pact.verifier.path_exists', return_value=True)
    @unittest.skip("demonstrating skipping")
    def test_publish_on_success(self, mock_path_exists, mock_wrapper):
        mock_wrapper.return_value = (True, 'some logs')

        result = self.verifier.verify_with_broker(publish_version='1.0.0', **self.default_opts)
        print(result)  # todo
