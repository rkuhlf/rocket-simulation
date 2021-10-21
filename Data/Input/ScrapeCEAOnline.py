# SCRAPE CHEMICAL EQUILIBRIUM ANALYSIS from NASA
# Using https://cearun.grc.nasa.gov/, which is an online implementation of a thingy that gives properties of combustion depending on the chamber pressure and the mixture ratio of reactants
# This is slightly illegal (all website scraping is), and I would really like to re-implement this kind of thing with either RocketCEA or the CEA app


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
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# options.add_argument("--headless")

# chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome("C:/Users/rkuhlman813/Documents/chromedriver.exe", options=options)

keyboard = Controller()

timeout = 3

#endregion

#region DESIRED INPUTS
# https://ntrs.nasa.gov/api/citations/19960044559/downloads/19960044559.pdf

# both of these will overshoot unless you line up the increment perfectly
# min should realistically be one, it starts at one
min_pressure = 1
max_pressure = 50
pressure_increment = 1


min_OF = 0.3
max_OF = 25
OF_increment = 0.2


nozzleDivergingRatio = 4

paraffin_temperature = 293 # Kelvin, idk
paraffin_enthalpy = "" # J/mol

nitrous_temperature = 270 # Kelvin, it is coming out and evaporating, I think it might be pretty low
#endregion


runs_for_pressure = []
pressure_iterated_so_far = min_pressure

while pressure_iterated_so_far < max_pressure:
    # The max it can take is 24, and it is inclusive-inclusive
    runs_for_pressure.append((pressure_iterated_so_far, pressure_iterated_so_far + pressure_increment * 23))
    pressure_iterated_so_far += pressure_increment * 24


runs_for_OF = []
OF_iterated_so_far = min_OF

while OF_iterated_so_far < max_OF:
    # The max it can take is 30, and it is inclusive-inclusive
    runs_for_OF.append((OF_iterated_so_far, OF_iterated_so_far + OF_increment * 29))
    OF_iterated_so_far += OF_increment * 30


#region SCRAPING FUNCTIONS

def on_load(wait_selector, func):
    try:
        element_present = EC.presence_of_element_located(
            (By.CSS_SELECTOR, wait_selector))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load", wait_selector)
    finally:
        # print("Page loaded", wait_selector)
        func()

#region FUNCTIONS FOR SCRAPING
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

#endregion

iters = 0
def saveOutput():
    global iters
    output = driver.find_element_by_tag_name("body").text

    f = open("./Data/Input/CEAOutput/" + str(iters), "w")
    f.write(output)
    f.close()
    print("Saved output")


    iters += 1

#endregion

print(runs_for_OF, "\n", runs_for_pressure)
for pressure_range in runs_for_pressure:
    for OF_range in runs_for_OF:
        print(pressure_range, OF_range)

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
        # driver.close()






