import base64
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image


class BrowserAutomator:
    def __init__(self, output_dir="../data/screenshots"):
        self.output_dir = Path(output_dir)

        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)

        #Standard config
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=self.options)

    def capture_screenshot(self, url):
        try:
            #goes to site
            self.driver.get(url)

            #save the file with corresponding date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_")
            filename = f"{safe_url}_{timestamp}.png"
            file_path = self.output_dir / filename

            #take screenshot
            self.driver.save_screenshot(str(file_path))

            with open(file_path, "rb") as image_file:
                b64_data = base64.b64encode(image_file.read()).decode("utf-8")

            #open image
            try:
                img = Image.open(file_path)
                img.show()
            except Exception as e:
                print(f"[-] Could not open image: {e}")

            return {
                "url": url,
                "screenshot_path": str(file_path),
                "base64_image": b64_data
            }

        except Exception as e:
            print(f"[-] Failed to capture screenshot for {url}: {e}")
            return None

    def close(self):
        self.driver.quit()