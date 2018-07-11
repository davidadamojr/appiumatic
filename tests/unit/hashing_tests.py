import hashing
import actions
import unittest
import random
from constants import *


class HashingTests(unittest.TestCase):

    def test_state_hash_is_stable(self):
        widgets = [
            {
                "selector": "id",
                "selectorValue": "android:id/title1",
                "description": "",
                "type": "EditText",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/title2",
                "description": "",
                "type": "EditText",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/btn2",
                "description": "Login",
                "type": "TextView",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/checkbox1",
                "description": "Show All",
                "type": "CheckBox",
                "state": "enabled"
            }
        ]

        possible_actions = [
            actions.TextEntry(widgets[0], GUIActionType.TEXT_ENTRY, "Hello World!"),
            actions.TextEntry(widgets[1], GUIActionType.TEXT_ENTRY, None),
            actions.Click(widgets[2], GUIActionType.CLICK, None),
            actions.Click(widgets[3], GUIActionType.CHECK, None),
            actions.Click(widgets[3], GUIActionType.UNCHECK, None)
        ]

        hashes = []
        for i in range(10):
            state_id = hashing.generate_state_hash(possible_actions)
            hashes.append(state_id)
        self.assertEqual(len(set(hashes)), 1)

    def test_state_hash_ignores_order(self):
        widgets = [
            {
                "selector": "id",
                "selectorValue": "android:id/title1",
                "description": "",
                "type": "EditText",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/title2",
                "description": "",
                "type": "EditText",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/btn2",
                "description": "Login",
                "type": "TextView",
                "state": "enabled"
            },
            {
                "selector": "id",
                "selectorValue": "android:id/checkbox1",
                "description": "Show All",
                "type": "CheckBox",
                "state": "enabled"
            }
        ]

        possible_actions = [
            actions.TextEntry(widgets[0], GUIActionType.TEXT_ENTRY, "Hello World!"),
            actions.TextEntry(widgets[1], GUIActionType.TEXT_ENTRY, None),
            actions.Click(widgets[2], GUIActionType.CLICK, None),
            actions.Click(widgets[3], GUIActionType.CHECK, None),
            actions.Click(widgets[3], GUIActionType.UNCHECK, None)
        ]

        hashes = []
        for i in range(10):
            random.shuffle(possible_actions)
            state_id = hashing.generate_state_hash(possible_actions)
            hashes.append(state_id)

        self.assertEqual(len(set(hashes)), 1)

    def test_get_hash_event(self):
        # Arrange
        target = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        event = {
            "actions": [actions.Click(target, GUIActionType.CLICK, None)],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        # Act
        hash_event = hashing._get_hash_event(event)

        # Assert
        self.assertNotIn("value", hash_event["actions"][0])

    def test_event_hashing(self):
        # Arrange
        target = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        event = {
            "actions": [actions.Click(target, GUIActionType.CLICK, None)],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        # Act
        event_hash = hashing.generate_event_hash(event)

        # Assert
        self.assertEqual(event_hash, "1c7d92889def3c42168491899e45bfb9a70ef790")

    def test_event_hash_is_stable(self):
        # Arrange
        target = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        event = {
            "actions": [actions.Click(target, GUIActionType.CLICK, None)],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        # Act
        hashes = []
        for i in range(10):
            event_hash = hashing.generate_event_hash(event)
            hashes.append(event_hash)

        # Assert
        self.assertEqual(len(set(hashes)), 1)

    def test_event_hashing_does_not_change_with_key_order(self):
        # Arrange
        target_1 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        action_1 = actions.Click(target_1, GUIActionType.CLICK, None)
        event_1 = {
            "actions": [action_1],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        target_2 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        action_2 = actions.Click(target_2, GUIActionType.CLICK, None)
        event_2 = {
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            },
            "actions": [action_2]
        }

        # Act
        event_hash1 = hashing.generate_event_hash(event_1)
        event_hash2 = hashing.generate_event_hash(event_2)

        # Assert
        self.assertEqual(event_hash1, event_hash2)

    def test_event_hash_is_same_regardless_of_value(self):
        # Arrange
        target_1 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "EditText",
            "state": "enabled"
        }
        action_1 = actions.Click(target_1, GUIActionType.CLICK, "Wunderland")
        event_1 = {
            "actions": [action_1],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        target_2 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "EditText",
            "state": "enabled"
        }
        action_2 = actions.Click(target_2, GUIActionType.CLICK, "Jekyll")
        event_2 = {
            "actions": [action_2],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        # Act
        event_hash1 = hashing.generate_event_hash(event_1)
        event_hash2 = hashing.generate_event_hash(event_2)

        # Assert
        self.assertEqual(event_hash1, event_hash2)

    def test_that_disabled_and_enabled_events_have_different_hash(self):
        # Arrange
        enabled_target = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        enabled_action = actions.Click(enabled_target, GUIActionType.CLICK, None)
        enabled_event = {
            "actions": [enabled_action],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        disabled_target = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "disabled"
        }
        disabled_action = actions.Click(disabled_target, GUIActionType.CLICK, None)
        disabled_event = {
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            },
            "actions": [disabled_action]
        }

        # Act
        enabled_event_hash = hashing.generate_event_hash(enabled_event)
        disabled_event_hash = hashing.generate_event_hash(disabled_event)

        # Assert
        self.assertNotEqual(enabled_event_hash, disabled_event_hash)

    def test_generate_test_case_hash(self):
        # Arrange
        target_1 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        action_1 = actions.Click(target_1, GUIActionType.CLICK, None)
        event_1 = {
            "actions": [action_1],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        target_2 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "disabled"
        }
        action_2 = actions.Click(target_2, GUIActionType.CLICK, None)
        event_2 = {
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            },
            "actions": [action_2]
        }
        test_case = [event_1, event_2]

        # Act
        test_case_hash = hashing.generate_sequence_hash(test_case)

        # Assert
        self.assertEqual(test_case_hash, "854ec40eabd6348cd96507a1339d9bd64919e747")

    def test_generate_test_case_hash_with_different_order_of_events(self):
        # Arrange
        target_1 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "enabled"
        }
        action_1 = actions.Click(target_1, GUIActionType.CLICK, None)
        event_1 = {
            "actions": [action_1],
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            }
        }

        target_2 = {
            "selector": "id",
            "selectorValue": "android:id/display_preferences",
            "description": "Display Preferences",
            "type": "TextView",
            "state": "disabled"
        }
        action_2 = actions.Click(target_2, GUIActionType.CLICK, None)
        event_2 = {
            "precondition": {
                "activityName": "launchActivity",
                "stateId": "abcdef"
            },
            "actions": [action_2]
        }
        test_case1 = [event_1, event_2]
        test_case2 = [event_2, event_1]

        # Act
        test_case_hash1 = hashing.generate_sequence_hash(test_case1)
        test_case_hash2 = hashing.generate_sequence_hash(test_case2)

        # Assert
        self.assertNotEqual(test_case_hash1, test_case_hash2)



