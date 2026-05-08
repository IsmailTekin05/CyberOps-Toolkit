import pytest
import os
import tempfile
import base64
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
from hypothesis import given, strategies as st
import responses

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ops.web_auto import BrowserAutomator

class TestBrowserAutomator:

    @pytest.fixture
    def temp_screenshot_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def browser_automator(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        yield automator
        automator.close()

    def test_initialization_creates_output_directory(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        assert automator.output_dir.exists()
        automator.close()

    def test_initialization_sets_output_dir_attribute(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        assert automator.output_dir == Path(temp_screenshot_dir)
        automator.close()

    def test_initialization_creates_driver(self, browser_automator):
        assert browser_automator.driver is not None
        assert hasattr(browser_automator.driver, 'get')

    def test_initialization_sets_headless_mode(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        options_str = str(automator.options.arguments)
        assert '--headless' in options_str
        automator.close()

    def test_initialization_sets_window_size(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        options_str = str(automator.options.arguments)
        assert '--window-size=1920,1080' in options_str
        automator.close()

    def test_initialization_sets_disable_gpu(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        options_str = str(automator.options.arguments)
        assert '--disable-gpu' in options_str
        automator.close()

    def test_initialization_sets_no_sandbox(self, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        options_str = str(automator.options.arguments)
        assert '--no-sandbox' in options_str
        automator.close()

    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_returns_dict(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator, 'driver.save_screenshot', return_value=None):
            with patch('PIL.Image.open'):
                test_file = os.path.join(temp_screenshot_dir, 'test.png')
                open(test_file, 'wb').close()

                result = automator.capture_screenshot("http://example.com")

                assert isinstance(result, dict)
                assert 'url' in result
                assert 'screenshot_path' in result
                assert 'base64_image' in result

    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_image_show_exception(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100))
                img.save(f)

            with patch('PIL.Image.open') as mock_image_open:
                mock_img = MagicMock()
                mock_img.show.side_effect = Exception("Display error")
                mock_image_open.return_value = mock_img

                result = automator.capture_screenshot("http://example.com")

                assert result is not None
                assert 'base64_image' in result

    @pytest.mark.parametrize("url", [
        "http://example.com",
        "https://example.com",
        "http://example.com/path",
        "https://example.com/path/to/page"
    ])
    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_various_urls(self, mock_driver_class, url, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100))
                img.save(f)

            with patch('PIL.Image.open'):
                result = automator.capture_screenshot(url)

                assert result is not None
                assert result['url'] == url

    @given(url=st.from_regex(r'https?://[\w\-\.]+\.[a-z]{2,}', fullmatch=True))
    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_with_generated_urls(self, mock_driver_class, url):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_driver = MagicMock()
            mock_driver_class.return_value = mock_driver

            automator = BrowserAutomator(output_dir=temp_dir)
            automator.driver = mock_driver

            with patch.object(automator.driver, 'save_screenshot'):
                test_file = os.path.join(temp_dir, 'test.png')
                with open(test_file, 'wb') as f:
                    img = Image.new('RGB', (100, 100))
                    img.save(f)

                with patch('PIL.Image.open'):
                    result = automator.capture_screenshot(url)

                    assert result is not None
                    assert 'screenshot_path' in result

    @responses.activate
    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_with_mocked_http(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        responses.add(responses.GET, 'http://example.com', status=200)

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100))
                img.save(f)

            with patch('PIL.Image.open'):
                result = automator.capture_screenshot("http://example.com")

                assert result is not None

    @patch('selenium.webdriver.Chrome')
    def test_output_dir_path_object(self, mock_driver_class, temp_screenshot_dir):
        automator = BrowserAutomator(output_dir=temp_screenshot_dir)

        assert isinstance(automator.output_dir, Path)

        automator.close()

    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_saves_in_correct_directory(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100))
                img.save(f)

            with patch('PIL.Image.open'):
                result = automator.capture_screenshot("http://example.com")

                saved_dir = Path(result['screenshot_path']).parent
                assert saved_dir == automator.output_dir

    @patch('selenium.webdriver.Chrome')
    def test_capture_screenshot_base64_can_be_decoded_to_image(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100), color='red')
                img.save(f)

            with patch('PIL.Image.open'):
                result = automator.capture_screenshot("http://example.com")

                decoded = base64.b64decode(result['base64_image'])
                assert len(decoded) > 0

    @patch('selenium.webdriver.Chrome')
    def test_screenshot_path_is_string(self, mock_driver_class, temp_screenshot_dir):
        mock_driver = MagicMock()
        mock_driver_class.return_value = mock_driver

        automator = BrowserAutomator(output_dir=temp_screenshot_dir)
        automator.driver = mock_driver

        with patch.object(automator.driver, 'save_screenshot'):
            test_file = os.path.join(temp_screenshot_dir, 'test.png')
            with open(test_file, 'wb') as f:
                img = Image.new('RGB', (100, 100))
                img.save(f)

            with patch('PIL.Image.open'):
                result = automator.capture_screenshot("http://example.com")

                assert isinstance(result['screenshot_path'], str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

