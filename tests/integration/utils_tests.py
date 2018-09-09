import unittest
import os
import shutil
import sqlite3
import actions
import json
from database import Database
from constants import GUIActionType
from hashing import generate_event_hash
from exploration.utils import remove_termination_events, write_sequence_to_file


def remove_db_file(db_path):
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except Exception as e:
            print(e)


def remove_output_files(output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)


def create_available_events():
    target_1 = {
        "selector": "id",
        "selectorValue": "android:id/display_preferences",
        "description": "Display Preferences",
        "type": "TextView",
        "state": "enabled"
    }
    action_1 = actions.Click(target=target_1, action_type=GUIActionType.CLICK)
    event_1 = {
        "actions": [action_1],
        "precondition": {
            "activityName": "launchActivity",
            "stateId": "abcdef"
        }
    }

    target_2 = {
        "selector": "id",
        "selectorValue": "android:id/add_contact",
        "description": "Add contact",
        "type": "Button",
        "state": "enabled"
    }
    action_2 = actions.Click(target=target_2, action_type=GUIActionType.CLICK)
    event_2 = {
        "actions": [action_2],
        "precondition": {
            "activityName": "contactActivity",
            "stateId": "a1b1c1"
        }
    }

    target_3 = {
        "selector": "id",
        "selectorValue": "android:id/contact_name",
        "description": "Contact Name",
        "type": "EditText",
        "state": "disabled"
    }
    action_3 = actions.Click(target=target_3, action_type=GUIActionType.CLICK)
    event_3 = {
        "actions": [action_3],
        "precondition": {
            "activityName": "launchActivity",
            "stateId": "abcdef"
        }
    }

    available_events = [event_1, event_2, event_3]
    return available_events


class UtilsTests(unittest.TestCase):
    def setUp(self):
        self.output_path = "output"
        self.db_path = "autodroid_test.db"
        self.available_events = create_available_events()

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def tearDown(self):
        remove_db_file(self.db_path)
        remove_output_files(self.output_path)

    def test_can_remove_termination_events_when_none(self):
        # Arrange
        db_connection = sqlite3.connect(self.db_path)
        database = Database(db_connection)
        database.create_tables()
        suite_id = "suite_id"

        # Act
        non_termination_events = remove_termination_events(database, suite_id, self.available_events)

        # Assert
        self.assertEqual(non_termination_events, self.available_events)

        database.close()

    def test_can_remove_termination_events_when_one(self):
        # Arrange
        db_connection = sqlite3.connect(self.db_path)
        database = Database(db_connection)
        database.create_tables()
        suite_id = "suite_id"
        event_hash_1 = generate_event_hash(self.available_events[0])
        database.add_termination_event(event_hash_1, suite_id)

        # Act
        non_termination_events = remove_termination_events(database, suite_id, self.available_events)

        # Assert
        self.assertEqual(len(non_termination_events), 2)
        self.assertEqual(non_termination_events[0], self.available_events[1])
        self.assertEqual(non_termination_events[1], self.available_events[2])

    def test_can_remove_termination_events_when_all(self):
        # Arrange
        db_connection = sqlite3.connect(self.db_path)
        database = Database(db_connection)
        database.create_tables()
        suite_id = "suite_id"
        event_hash_1 = generate_event_hash(self.available_events[0])
        event_hash_2 = generate_event_hash(self.available_events[1])
        database.add_termination_event(event_hash_1, suite_id)
        database.add_termination_event(event_hash_2, suite_id)

        # Act
        non_termination_events = remove_termination_events(database, suite_id, self.available_events)

        # Assert
        self.assertEqual(len(non_termination_events), 1)
        self.assertEqual(non_termination_events[0], self.available_events[2])

    def test_can_write_sequence_file(self):
        # Arrange
        sequence_count = 1
        sequence_duration = 50

        # Act
        sequence_path = write_sequence_to_file(self.output_path, self.available_events, sequence_count,
                                               sequence_duration)

        # Assert
        self.assertTrue(os.path.exists(sequence_path))
        self.assertEqual(sequence_path, os.path.join(self.output_path, "tc001_50.json"))
        with open(sequence_path) as sequence_file:
            sequence_from_json = json.load(sequence_file)
            self.assertEqual(len(sequence_from_json["events"]), 3)

