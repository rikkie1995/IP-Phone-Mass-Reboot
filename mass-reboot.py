from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import itertools
import sys
import socket


# Device credentials
device_credentials = {
    "grandstream": {"user": "admin", "pass": "admin"},
    "snom": {"user": "admin", "pass": "admin"},
    "polycom": {"user": "Polycom", "pass": "456"},
}


# Read IPs from file
with open("data.txt", "r") as file:
    ips = [line.strip() for line in file if line.strip()]


# Helpers
def format_duration(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"


def log_result(text):
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)


def is_port_open(ip, port=80, timeout=2):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def wait_for_port_80(ip, timeout=200):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    log_result(f"⏳ Waiting for {ip} port 80 to become accessible...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_open(ip, port=80):
            duration = int(time.time() - start_time)
            sys.stdout.write(f"\r✅ Port 80 accessible after {duration} seconds.\n")
            log_result(f"✅ Device {ip} port 80 accessible after {duration} seconds.")
            return True, duration
        sys.stdout.write(f"\r🌐 Waiting for port 80... {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write("\r❌ Timeout waiting for port 80.\n")
    log_result(f"❌ Timeout waiting for port 80 on {ip}.")
    return False, 0


# Detection devices
def detect_grandstream(driver, ip, creds):
    try:
        log_result(f"🔍 Checking if {ip} is a supported Grandstream device...")
        driver.get(f"http://{ip}")


        try:
            footer_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.gwt-HTML"))
            )
            footer_text = footer_div.text.strip().lower()


            if "grandstream" in footer_text:
                log_result(f"✅ Detected Grandstream device at {ip}")
            else:
                raise TimeoutException()


        except TimeoutException:
            page_source = driver.page_source.lower()
            has_login_form = all(
                css in page_source for css in ["gwt-textbox", "gwt-butt", "gwt-passwordtextbox"]
            )
            if has_login_form:
                log_result(f"✅ Detected Grandstream device at {ip}")
            else:
                raise Exception("❌")


        # Login section
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.gwt-TextBox"))
        )
        driver.find_element(By.CSS_SELECTOR, "input.gwt-TextBox").clear()
        driver.find_element(By.CSS_SELECTOR, "input.gwt-TextBox").send_keys(creds["user"])
        driver.find_element(By.CSS_SELECTOR, "input.gwt-PasswordTextBox").clear()
        driver.find_element(By.CSS_SELECTOR, "input.gwt-PasswordTextBox").send_keys(creds["pass"])
        driver.find_element(By.CSS_SELECTOR, "button.gwt-Button").click()


        WebDriverWait(driver, 5).until(lambda d: d.title.strip() != "")


        # Reboot section
        reboot_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.feature[name="reboot"]'))
        )
        reboot_link.click()


        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.button.green'))
        ).click()
        log_result(f"🔁 Grandstream reboot confirmed for {ip}.")


        while is_port_open(ip, 80):
            sys.stdout.write("🔻 Still reachable on port 80...\r")
            sys.stdout.flush()
            time.sleep(0.5)


        log_result(f"✅ Device {ip} is now OFFLINE. Starting reboot timer...")
        return "grandstream", *wait_for_port_80(ip)


    except Exception as e:
        log_result(f"❌{ip} is not a Grandstream Device {e}")
        return None, False, 0






def detect_snom(driver, ip, creds):
    try:
        log_result(f"🔍 Checking if {ip} is a supported Snom device...")


        # Login section
        driver.get(f"http://{creds['user']}:{creds['pass']}@{ip}")
        time.sleep(2)
        log_result(f"✅ Detected Snom device at {ip}")


        if "snom" not in driver.page_source.lower():
            raise Exception("❌")


        # Reboot section
        driver.get(f"http://{ip}/advanced_update.htm")


        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "CONFIRM_REBOOT"))).click()
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "REBOOT"))).click()
        log_result(f"🔁 Snom reboot confirmed for {ip}.")


        while is_port_open(ip, 80):
            sys.stdout.write("🔻 Still reachable on port 80...\r")
            sys.stdout.flush()
            time.sleep(0.5)


        log_result(f"✅ Device {ip} is now OFFLINE. Starting reboot timer...")
        return "snom", *wait_for_port_80(ip)


    except Exception as e:
        log_result(f"❌{ip} is not a Snom Device {e}")
        return None, False, 0


def detect_polycom(driver, ip, creds):
    try:
        log_result(f"🔍 Checking if {ip} is a supported Polycom SoundPoint model...")
        driver.get(f"http://{ip}")
        time.sleep(1)
        log_result(f"✅ Detected Polycom device at {ip}")




        if "polycom web configuration utility" not in driver.page_source.lower():
            raise Exception("❌")


        # Login section
        driver.find_element(By.CSS_SELECTOR, 'input[type="radio"][value="Polycom"]').click()
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(creds["pass"])
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()




        # Reboot section
        utilities_menu = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "topMenuItem6"))
        )
        ActionChains(driver).move_to_element(utilities_menu).perform()
        time.sleep(1)


        submenu = utilities_menu.find_element(By.TAG_NAME, "ul")
        if submenu.value_of_css_property("display") == "none":
            utilities_menu.click()
            time.sleep(1)


        submenu.find_element(By.CSS_SELECTOR, 'li[src="restartPhone.htm"] a').click()


        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "popupbtn0"))
        ).click()


        log_result(f"🔁 Reboot confirmed on Polycom {ip}.")


        while is_port_open(ip, 80):
            sys.stdout.write("🔻 Still reachable on port 80...\r")
            sys.stdout.flush()
            time.sleep(0.5)


        log_result(f"✅ Device {ip} is now OFFLINE. Starting reboot timer...")
        return "polycom", *wait_for_port_80(ip)


    except Exception as e:
        log_result(f"❌{ip} is not a Polycom Device {e}")
        return None, False, 0


# Device detector mapping
device_detectors = {
    "grandstream": detect_grandstream,
    "snom": detect_snom,
    "polycom": detect_polycom,
}


#WebDriver Settings
options = Options()
options.add_argument("--headless=new")  
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")


#WebDriver initialization
with webdriver.Chrome(ChromeDriverManager().install(), options=options) as driver:
    total_duration_seconds = 0
    open("results.txt", "w").close()


    #Main Loop
    for ip in ips:
        log_result(f"\n➡️ Scanning IP: {ip}")
        device_found = False


        for device_type, creds in device_credentials.items():
            detector = device_detectors[device_type]
            time.sleep(2)
            result, success, duration = detector(driver, ip, creds)


            if result:
                device_found = True
                if success:
                    total_duration_seconds += duration
                    log_result(f"✅ Device {ip} ({result}) rebooted successfully in {format_duration(duration)}.")
                else:
                    log_result(f"❌ Device {ip} ({result}) reboot failed or timed out.")
                break


        if not device_found:
            log_result(f"⚠️ Could not detect device type or login failed for {ip}.")


    log_result(f"\n⏱️ Total reboot time for all devices: {format_duration(total_duration_seconds)}")