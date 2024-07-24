# Create your tests here.
from django.core.exceptions import ValidationError
from django.template import Template, Context
from django.test import LiveServerTestCase
from django.test import TestCase
from selenium import webdriver

from hooshunt.models import Clue

username = "uvaprojectb14@gmail.com"
pssword = "DJANGOiss0h4rd"


#checking if google maps loaded
def test_google_maps_api_included(self):
    template = Template("{% include 'map.html' %}")
    rendered_template = template.render(Context({}))
    self.assertIn('https://maps.googleapis.com/maps/api/js', rendered_template)

class HomeTest(LiveServerTestCase):

    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(options=chrome_options)

    #Trying out selenium. Seeing if it can pull the website and items in the homepage
    # Getting Started (Selenium) Citation
    def test_home_page(self):
        driver = self.driver
        driver.get("https://b14-3240-4659467253be.herokuapp.com/")
        driver.implicitly_wait(100)
        driver.maximize_window()
        actual_title = driver.title #the title of the tab
        html_source = driver.page_source
        self.assertIn("HoosHunt", actual_title)
        #Seeing if some of the texts on home page loaded
        if "Welcome to HoosHunt" in html_source:
            print("found")
        else:
            print("not found")
        driver.close()

        #finished
        print("test_home_page successful")

        #selenium doesn't work up to the password due to google blocking automated tests and github actions x selenium issues
        #though if you were to run this locally, it should work
        # button = driver.find_element(By.CLASS_NAME, "gsi-material-button-icon")
        # button.click()
        # driver.find_element(By.ID, "identifierId").send_keys(username)
        # driver.find_element(By.ID, "identifierNext").click()
        # driver.implicitly_wait(100)
        # driver.find_element(By.NAME, "Passwd").send_keys(pssword)
        # driver.find_element(By.ID, "passwordNext").click()
        # print("done")

class ClueModelTest(TestCase):
    #unit tests for correct and incorrect clues
    def setUp(self):
        # Create a mock clue with correct information
        self.correct_clue_data = {
            'description': 'Correct Clue Description',
            'hints': 'Hint 1, Hint 2',
            'longitude': 12.3456789,
            'latitude': 23.4567890,
            'approved': True,
            'bundle': 'E-Way',
        }

        # Create a mock clue with incorrect information (exceeding boundaries)
        self.incorrect_clue_data = {
            'description': 'Incorrect Clue Description',
            'hints': 'Incorrect Hint 1, Incorrect Hint 2',
            'longitude': 200.0,  # Invalid longitude (exceeds the boundary)
            'latitude': 100.0,   # Invalid latitude (exceeds the boundary)
            'approved': False,
            'bundle': 'InvalidBundle',
        }

    def test_correct_clue_creation(self):
        correct_clue = Clue.objects.create(**self.correct_clue_data)
        self.assertIsInstance(correct_clue, Clue)

    def test_incorrect_clue_creation(self):
        incorrect_clue = Clue.objects.create(**self.incorrect_clue_data)
        with self.assertRaises(ValidationError):
            incorrect_clue.full_clean()



