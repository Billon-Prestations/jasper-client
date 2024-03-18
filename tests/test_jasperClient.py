import unittest
import xmltodict
from jasperClient.client import JasperClient
from unittest.mock import Mock, patch


class TestJasperClient(unittest.TestCase):
    @patch("requests.post", autospec=True)
    def test_getCookie(self, mock_post):
        print("test_getCookie")
        mock_response = Mock()
        expected_cookie = "test_cookie"
        mock_response.cookies.get_dict.return_value = {"JSESSIONID": expected_cookie}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        client = JasperClient("https://host", "username", "password")
        actual_cookie = client.getCookie()

        self.assertEqual("JSESSIONID=" + expected_cookie, actual_cookie)

    @patch("requests.get", autospec=True)
    def test_get(self, mock_get):
        print("test_get")
        expected_response = Mock()
        mock_get.return_value = expected_response

        client = JasperClient("https://host", "username", "password")
        actual_response = client.get("url")

        self.assertEqual(expected_response, actual_response)

    @patch("requests.get", autospec=True)
    def test_getListParameters(self, mock_get):
        print("test_getListParameters")
        expected_response = Mock()
        expected_response.status_code = 200
        mock_get.return_value = expected_response

        client = JasperClient("https://host", "username", "password")
        actual_response = client.getListParameters("path")

        self.assertEqual(xmltodict.parse(expected_response.content), actual_response)

    @patch("requests.get", autospec=True)
    def test_getParameters(self, mock_get):
        print("test_getParameters")
        expected_response = Mock()
        expected_ic = [{"label": "label_value", "dataType": {"type": "data_type"}}]
        expected_response.json.return_value = expected_ic
        mock_get.return_value = {"inputControls": {"inputControl": expected_response}}

        client = JasperClient("https://host", "username", "password")
        actual_param = client.getParameters("path")

        self.assertEqual(expected_ic[0]["label"], actual_param[0]["label"])
        self.assertEqual(expected_ic[0]["dataType"]["type"], actual_param[0]["type"])


if __name__ == "__main__":
    unittest.main()
