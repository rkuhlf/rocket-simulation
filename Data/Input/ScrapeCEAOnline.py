



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


from pynput.keyboard import Key, Controller

#region SCRAPING SETTINGS
options = webdriver.ChromeOptions()
# options.add_argument("--headless")

chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver, options=options)

keyboard = Controller()

timeout = 3

#endregion

#region DESIRED INPUTS

# bothh of these will overshoot unless you line up the increment perfectly
min_pressure = 1
max_pressure = 50
pressure_increment = 2


min_OF = 0
max_OF = 25
OF_increment = 5


nozzleDivergingRatio = 4

#endregion


runs_for_pressure = []
pressure_iterated_so_far = 0

while pressure_iterated_so_far < max_pressure:
    # The max it can take is 24, and it is inclusive-inclusive
    runs_for_pressure.append((pressure_iterated_so_far, pressure_iterated_so_far + pressure_increment * 23))
    pressure_iterated_so_far += pressure_increment * 24


runs_for_OF = []
OF_iterated_so_far = 0

while OF_iterated_so_far < max_OF:
    # The max it can take is 30, and it is inclusive-inclusive
    runs_for_OF.append((OF_iterated_so_far, OF_iterated_so_far + OF_increment * 29))
    OF_iterated_so_far += OF_increment * 30




def on_load(wait_selector, func):
    try:
        element_present = EC.presence_of_element_located(
            (By.CSS_SELECTOR, wait_selector))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load", wait_selector)
    finally:
        print("Page loaded", wait_selector)
        func()


submit_button = "input[name='.submit']"

def click_css(selector):
    driver.find_element_by_css_selector(selector).click()


def submitRocketType():
    driver.find_element_by_css_selector("input[value='Submit']").click()

def clickSubmit():
    driver.find_element_by_css_selector(submit_button).click()


def selectRange(small, high, increment):
    def temp():
        keyboard.type(str(small))
        keyboard.press(Key.tab)
        keyboard.type(str(high))
        keyboard.press(Key.tab)
        keyboard.type(str(increment))


        driver.find_element_by_css_selector(submit_button).click()

    return temp


# this is the most annoying one to automate. If you want to do something like HTPB or ABS you have to select all of its components. For simplicity, I am doing paraffin rn
# Acrylonitrile: C3H3N
# Butadiene: C4H6
# Styrene: C8H8

def selectPeriodic():
    driver.find_element_by_css_selector("input[value='Use Periodic Table (mixtures)']").click()

    driver.find_element_by_css_selector(submit_button).click()


def selectHydrocarbon():
    driver.find_element_by_css_selector("input[value='H-C']").click()


def selectParaffin():
    driver.find_element_by_css_selector("input[value='paraffin']").click()

    driver.find_element_by_css_selector(submit_button).click()

def inputProperties():
    # TODO: input proper properties here, I don't think the assumptions are good
    # Temperature Density Enthalpy

    clickSubmit()

def selectNitrous():
    click_css("input[value='N2O']")
    clickSubmit()

def inputExpansion():
    click_css("#supar1")
    keyboard.type(str(nozzleDivergingRatio))

    clickSubmit()

def finalSubmission():
    # Lots of settings here
    click_css("input[name='Frozen']")
    click_css("input[name='Equilibrium']")

    clickSubmit()

iters = 0
def saveOutput():
    global iters
    output = driver.find_element_by_tag_name("body").text
    print(output)

    f = open("./Data/Input/CEAOutput/" + str(iters), "w")
    f.write(output)
    f.close()

    iters += 1

for pressure_range in [(1, 10)]:# runs_for_pressure:
    for OF_range in [(0.1, 10)]:# runs_for_OF:
        driver.get("https://cearun.grc.nasa.gov/")
        on_load('.submitBtn', submitRocketType)

        on_load(submit_button, selectRange(pressure_range[0], pressure_range[1], pressure_increment))

        on_load("input[value='Use Periodic Table (mixtures)']", selectPeriodic)
        on_load(submit_button, selectHydrocarbon)
        on_load(submit_button, selectParaffin)
        on_load(submit_button, clickSubmit)
        on_load(submit_button, clickSubmit)
        on_load(submit_button, inputProperties)

        on_load(submit_button, selectNitrous)

        on_load(submit_button, selectRange(OF_range[0], OF_range[1], OF_increment))
        on_load("#supar1", inputExpansion)
        on_load(submit_button, finalSubmission)
        on_load("body", lambda : click_css("a[href='showFileOnBrowser.cgi?results=o']"))

        on_load("body", saveOutput)






