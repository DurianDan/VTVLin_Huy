from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# type casting in the function
from typing import List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver 

# Error handling
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException,WebDriverException, TimeoutException
from selenium import common
from urllib3.exceptions import NewConnectionError, MaxRetryError

# logging
from .Debug import LoggingQuickSetup,logging

#change VPN
from .VPN import VPN_helper

# wait seconds between retry 
import time

class seleniumHelper():
    def __init__(self,
                 logging_path: str| None=None,
                 auto_logging_setup=True) -> None:
        self.options = Options()
        self.element_exception = (NoSuchElementException, StaleElementReferenceException)
        self.driver_exception = (WebDriverException, TimeoutException,common.TimeoutException)
        self.network_exception = (NewConnectionError, MaxRetryError)
        self.driver = 0
        self.logging_path = logging_path
        if auto_logging_setup:
            LoggingQuickSetup(logging_file_path=logging_path).minimalConfig()
    
    def addVPN(self,vpn_provider: str):
        self.vpn_provider = vpn_provider

    def checkDriver(self):
        checks = { # for future checks
            "driverExist": type(self.driver) == WebDriver,
        }

        if not checks["driverExist"]:
            logging.error("There isn't any running driver")
        return checks
    
    def addOptions(self,
                arguments: list|None = ["--incognito"],
                page_load_strategy:str="none"
                 ) ->None:
        '''
        Add `arguments`, before starting driver\n
        `page_load_strategy` https://www.selenium.dev/documentation/webdriver/drivers/options/\n
            --headless : run driver without opening window\n
            --incognito : run driver in incognito mode
        '''
        # add options
        if self.checkDriver()["driverExist"]:
            raise ValueError(f"")
        for op in arguments:
            self.options.add_argument(op)
            logging.info(f"Driver will perform option: {op}")
        logging.info(f"Driver will have page_load_strategy: {page_load_strategy}")
        self.options.page_load_strategy = page_load_strategy
    
    def addFunctions(self,
                maximize:bool=True,
                timeout = None,
                 ) ->None:
        '''
        Add functions, to running selenium driver\n
        maximize : maximize window or stay in normal window\n
        timeout : set limit to the time spent loading a page, raise error after timeout
        '''
        if not self.checkDriver()["driverExist"]:
            raise ValueError("There aren't any running-driver to maximize window or to set timeout\nYou can initialize diver using: normalCreateDriver() or forceCreateDriver()")
        if maximize:
            self.driver.maximize_window()
            logging.info("Maximizied window")
        if type(timeout) == int and timeout > 0:
            self.driver.set_page_load_timeout(timeout)

    def quitRunningDriver(self):
        '''
        Quit any running driver
        '''
        if type(self.driver) == WebDriver:
            try:
                self.driver.quit()
            except Exception as err:
                logging.warning("quitRunningDriver(): error while quitting driver:\n")
                logging.warning(err)
            self.driver = 0
            logging.info("Driver has quit, and the variable 'driver' is now of type 'int', containing value 0")
        else:
            logging.warning("There isn't any running driver to quit()")
    def normalCreateDriver(self, quit_running_driver:bool=True)-> WebDriver:
        if quit_running_driver: self.quitRunningDriver()
        self.driver = Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.options )
        return self.driver 
    def forceCreateDriver(self,
                    vpn_provider:str | None=None,
                    reconnect_vpn:bool=True,
                    quit_running_driver:bool=True,
                    retry:int=10,
                    retry_interval:int=1
                    ):
        if type(vpn_provider) == str and vpn_provider not in ["hotspotshield","nordvpn","protonvpn"]:
            raise ValueError (f"{vpn_provider} is not avalid vpn provider\nProvider can only be one of hotspotshield, nordvpn, protonvpn")
        '''
        `vpn_provider` can be one of "hotspotshield"|"nordvpn"|"protonvpn"\n
            if `vpn_provider` is None, vpn will not be reset
        `retry` number of retries if the driver can't start\n
        `retry_interval` seconds wait each retry
        '''
        self.vpn_provider = vpn_provider
        if quit_running_driver: self.quitRunningDriver()
        retry_record = 0
        last_err = ""
        for _ in range(retry):
            try:
                return self.normalCreateDriver()
            except self.driver_exception as err:
                last_err = str(err)
                retry_record += 1
                time.sleep(retry_interval)
                logging.error(f"forceCreateDriver(): re-opening driver for the {retry_record} time(s): {err}")
                if reconnect_vpn:
                    logging.info(VPN_helper(vpn_provider=vpn_provider).autoConnect())
        
        raise ValueError(f"Can't start driver after {retry} retries, last error was {last_err}")

class driverHelper(seleniumHelper):
    def __init__(self, logging_path=None, auto_logging_setup=True) -> None:
        super().__init__(logging_path, auto_logging_setup)
    
    def reopenDriver(self, retry_count:int=1,reconnect_vpn:bool=True ):
        '''
        `retry_count` is the times that the driver has been quit and reopen,
        this argument is only for `logging`
        '''
        self.quitRunningDriver()
        logging.warning(f"Reopening driver for the {retry_count} time(s)")
        self.forceCreateDriver(reconnect_vpn=reconnect_vpn)
    
    def forceFindElement(self,
                     by:By,
                     element_string:str,
                     element_as_finder:WebElement | None = None,
                     retry:int=10,
                     retry_interval:int|str=1,
                     find_element_message:str|None=None,
                     try_refresh_before_retry:bool=False
                     ):
        '''
        Retry until getting the element\n
        `elment_string` : E.g. "./html/body/div\n
        `by` : Method for the driver to get the element: \n
        `retry` : number of retries\n
        `element_as_finder` : using an element to find sub-element, instead of driver\n
        `retry_interval` : Seconds between each retry\n
            if `retry_interval` receive `incremental`, increase second wait after each retry 
        if `vpn_provider` is not empty (empty by default), `forceFindElement()` will change vpn after each retry   
        '''
        self.checkDriver()["driverExist"]

        last_err = ""
        if find_element_message:
            logging.info(f"Trying to get the element {element_string}")

        for i in range(retry):
            try:
                if element_as_finder == WebElement:
                    return element_as_finder.find_element(by=by, value=element_string)
                else:
                    return self.driver.find_element(by=by, value=element_string)
            except self.element_exception as err:
                last_err = err
                if try_refresh_before_retry: self.driver.refresh()
                pass
            except self.driver_exception + self.network_exceptionas as err:
                last_err = err
                if try_refresh_before_retry: self.driver.refresh()
                else: self.reopenDriver(reconnect_vpn=False,retry_count=i)
            logging.error(f"Retrying getting element for the {i} time(s), while handling this error :{last_err}")
            if retry_interval == "incremental":
                time.sleep(i)
            elif type(retry_interval) == int:
                time.sleep(retry_interval)
        raise ValueError(f"Cant find the element after {i} retries, last error was {last_err}")

    def forceGet(
            self,
            url:str,
            try_refresh_before_retry:bool=False,
            retry:int=4,
            retry_interval: int=0,
            error_message_in_page: List[str]|None =None
            ):
        '''
        Retry until can access the desired `url`\n
        `try_refresh_before_retry` if set to `True`, driver will refresh page before atempting reopen the whole driver,\n
            if the desired url is available after refresh, helper won't change VPN and reopen driver\n 
        `retry` is the number of retries\n
        `retry_interval` seconds wait each retry
        '''
        if not self.checkDriver()["driverExist"]:
            raise ValueError("Can't find element without a proper driver")
        
        retry_record = 0
        last_err = ""
        logging.info(f"Trying to reach the website {url}")
        for _ in range(retry):
            try:
                self.driver.get(url)
                if error_message_in_page:
                    # find if any of the parsed error_message_in_page...
                    # ...exist in page_source
                    error_message_exist = any([
                        mes in self.driver.page_source
                        for mes in error_message_in_page
                    ])
                    if error_message_exist:
                        self.reopenDriver(reconnect_vpn=True,retry_count=retry_record)
                        continue
                return
            except self.driver_exception + self.network_exception as err:
                last_err = err
                if try_refresh_before_retry:
                    try:
                        self.driver.refresh()
                        return
                    except:
                        logging.warning("Driver cant refresh => quit and reopening driver")
                self.reopenDriver(reconnect_vpn=True,retry_count=retry_record)
            retry_record += 1
            logging.error(f"Retrying getting element for the {retry_record} time(s), while handling whis error :{last_err}")
            time.sleep(retry_interval)
        raise ValueError(f"Cant find the element after {retry_record} retries, last error was {last_err}")
