import unittest
import abstraction
from constants import *
from execution import Executor
from appium import webdriver

"""These integration tests require a running emulator, appium server and Tomdroid 0.7.5"""


class ExecutionTests(unittest.TestCase):

    def setUp(self):
        desired_caps = {
            "platformName": "Android",
            "app": "/home/davidadamojr/git/autodroid/apps/org.tomdroid-0.7.5.apk",
            "deviceName": "Android",
            "newCommandTimeout": 3600
        }

        self.driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
        self.executor = Executor(self.driver, 2, ["Hello", "World", "12345"])

    def test_can_press_home(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        home_event = abstraction.create_home_event(precondition)

        # Act
        self.executor.execute(home_event)

    def test_can_press_back(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        back_event = abstraction.create_back_event(precondition)

        # Act
        self.executor.execute(back_event)

    def test_can_press_return(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        enter_key_target = abstraction.create_enter_target()
        enter_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.ENTER_KEY, enter_key_target)]
        }
        self.navigate_to_note_creation()

        # Act

        self.executor.execute(enter_event)

    def test_can_run_in_background(self):
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        background_event = abstraction.create_background_event(precondition)
        self.driver.find_element_by_id("android:id/button3").click()
        self.executor.execute(background_event)

    def test_can_long_click(self):
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        self.driver.find_element_by_id("android:id/button3").click()

        long_click_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title",
                                                      "Tomdroid's First Note", "TextView", TargetState.ENABLED)
        long_click_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.LONG_CLICK, long_click_target)]
        }

        # Act
        self.executor.execute(long_click_event)

    def test_can_swipe_up(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        swipe_up_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title", "", "RelativeLayout",
                                                    TargetState.ENABLED)
        swipe_up_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.SWIPE_UP, swipe_up_target)]
        }
        self.driver.find_element_by_id("android:id/button3").click()

        # Act
        self.executor.execute(swipe_up_event)

    def test_can_swipe_down(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        swipe_down_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title", "", "RelativeLayout",
                                                    TargetState.ENABLED)
        swipe_down_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.SWIPE_DOWN, swipe_down_target)]
        }
        self.driver.find_element_by_id("android:id/button3").click()

        # Act
        self.executor.execute(swipe_down_event)

    def test_can_swipe_right(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        swipe_right_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title", "", "RelativeLayout",
                                                       TargetState.ENABLED)
        swipe_right_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.SWIPE_RIGHT, swipe_right_target)]
        }
        self.driver.find_element_by_id("android:id/button3").click()

        # Act
        self.executor.execute(swipe_right_event)

    def test_can_swipe_left(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        swipe_left_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title", "", "RelativeLayout",
                                                      TargetState.ENABLED)
        swipe_left_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.SWIPE_LEFT, swipe_left_target)]
        }
        self.driver.find_element_by_id("android:id/button3").click()

        # Act
        self.executor.execute(swipe_left_event)

    def test_can_click(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        click_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/note_title", "", "RelativeLayout",
                                                 TargetState.ENABLED)
        click_event = {
            "precondition": precondition,
            "actions": [abstraction.create_action(GUIActionType.CLICK, click_target)]
        }
        self.driver.find_element_by_id("android:id/button3").click()

        # Act
        self.executor.execute(click_event)

    def test_can_type_text_in_single_field(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        text_field_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/title", "", "EditText",
                                                      TargetState.ENABLED)
        text_entry_action = abstraction.create_action(GUIActionType.TEXT_ENTRY, text_field_target)
        text_entry_action.value = "[random string]"

        enter_key_action = abstraction.create_action(GUIActionType.ENTER_KEY, abstraction.create_enter_target())
        text_entry_event = {
            "precondition": precondition,
            "actions": [text_entry_action, enter_key_action]
        }
        self.navigate_to_note_creation()

        # Act
        self.executor.execute(text_entry_event)

        # Assert
        self.assertNotEqual(text_entry_action.value, "[random string]")

    def test_can_type_text_in_multiple_text_fields_and_click_button(self):
        # Arrange
        precondition = abstraction.create_state("contactsActivity", "abcdef")
        text_field_target_1 = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/title", "", "EditText",
                                                        TargetState.ENABLED)
        text_field_target_2 = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/content", "", "EditText",
                                                        TargetState.ENABLED)
        non_text_target = abstraction.create_target(SelectorType.ID, "org.tomdroid:id/edit_note_save", "Save",
                                                    "TextView", TargetState.ENABLED)

        text_entry_action_1 = abstraction.create_action(GUIActionType.TEXT_ENTRY, text_field_target_1)
        text_entry_action_1.value = "[random string]"

        text_entry_action_2 = abstraction.create_action(GUIActionType.TEXT_ENTRY, text_field_target_2)
        text_entry_action_2.value = "[random string]"

        non_text_action = abstraction.create_action(GUIActionType.CLICK, non_text_target)

        multiple_text_entry_event = {
            "precondition": precondition,
            "actions": [text_entry_action_1, text_entry_action_2, non_text_action]
        }
        self.navigate_to_note_creation()

        # Act
        self.executor.execute(multiple_text_entry_event)

        # Assert
        self.assertNotEqual(text_entry_action_1.value, "[random string]")
        self.assertNotEqual(text_entry_action_2.value, "[random string]")

    def navigate_to_note_creation(self):
        self.driver.find_element_by_id("android:id/button3").click()
        self.driver.find_element_by_id("org.tomdroid:id/menuNew").click()

    def tearDown(self):
        self.driver.quit()
