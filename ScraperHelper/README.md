# This package help you use selenium to scrape the web more easily
## 1. Minimal Selenium code
- In a normal selenium project
```python
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

options = Options()
options.add_argument("--headless")
options.add_argument("--incognito")

driver = Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://google.com")
driver.find_element(By.XPATH, "./html/body")
```
- Achieving the same result, using ScraperHelper
```python
from ScraperHelper.Scrape import *

helper = driverHelper()

helper.addOptions(
    options = ["--incognito", "--headless"]
    # behave like Option().add_argument()
    # add multiple arguments to option
)

helper.driver.get("https://google.com") 
# helper.driver behaves axactly like Selenium Chrome driver 

helper.findForceElement(By.XPATH, "./html/body")
```
## 2. Avoid blocking, using your VPN subscription 
**only support **NordVPN**, more **VPN provider** will be updated in the future*
```python
from ScraperHelper.Scrape import *
helper = driverHelper()
helper.addVPN("nordvpn")

helper.forceGet( "https://google.com",retry=8 )
# retry up to 8 times, until the desired website is reached
# each retry, `helper` will change VPN, quit and reopen driver or refresh page

helper.findForceElement(By.XPATH, "./html/body")
```
## 3. Easy logging setup: save all scraping process in a **.log** file  
[*using logging package](https://realpython.com/python-logging/)
```python
from ScraperHelper.Scrape import *

helper = driverHelper(
    logging_path: "/path/to/your/log_file.log",
    auto_logging_setup=True)
# now everything you do with the `helper` will be recorded...
# ...and save in the text file log_file.log

helper.forceGet( "https://google.com" )
helper.findForceElement(By.XPATH, "./html/body")
```