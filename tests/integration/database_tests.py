import os
import sqlite3
import time
import unittest
import uuid

from database import Database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db_path = "autodroid_test.db"

        connection = sqlite3.connect(self.db_path)
        self.database = Database(connection)
        self.database.create_tables()

        cursor = self.database.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND (name='suites' OR name='stats' OR name='sequences'" +
            " OR name='event_info')")
        self.assertEqual(len(cursor.fetchall()), 4)

    def tearDown(self):
        self.database.close()
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)

    def test_can_add_test_suite(self):
        # Arrange
        suite_id = uuid.uuid4().hex
        creation_time = time.time()

        # Act
        suite_id, creation_time = self.database.create_suite()

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM suites WHERE id=?", (suite_id, ))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], suite_id)
        self.assertEqual(rows[0][1], creation_time)

    def test_can_update_test_suite(self):
        # Arrange
        suite_id = uuid.uuid4().hex
        creation_time = 5555
        suite_id, creation_time = self.database.create_suite()
        end_time = 6666
        duration = end_time - creation_time

        # Act
        suite_id, end_time = self.database.update_suite(suite_id, end_time, duration)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM suites WHERE id=?", (suite_id, ))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], end_time)
        self.assertEqual(rows[0][3], duration)

    def test_can_add_test_case(self):
        # Arrange
        test_case_hash = "test_case_hash"
        test_suite_id = "b927bd995c5d4204a3c1e1420dde735c"
        creation_time = 1516959397
        duration = 10

        # Act
        self.database.add_sequence(test_case_hash, test_suite_id, creation_time, duration)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM sequences WHERE hash_key=?", (test_case_hash, ))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], test_case_hash)
        self.assertEqual(rows[0][1], test_suite_id)
        self.assertEqual(rows[0][2], creation_time)
        self.assertEqual(rows[0][3], duration)

    def test_test_case_exists(self):
        # Arrange
        sequence_hash = "sequence_hash"
        suite_id = "suite_id"
        creation_time = 1234567890
        duration = 10
        self.database.add_sequence(sequence_hash, suite_id, creation_time, duration)

        # Act
        test_case_exists = self.database.sequence_exists(suite_id, sequence_hash)

        # Assert
        self.assertTrue(test_case_exists)

    def test_test_case_does_not_exist(self):
        # Arrange
        sequence_hash = "sequence_hash"
        suite_id = "suite_id"
        creation_time = 1234567890
        duration = 10
        self.database.add_sequence(sequence_hash, suite_id, creation_time, duration)

        # Act
        test_case_exists = self.database.sequence_exists("fake_test_suite_id", "fake_test_case_hash")

        # Assert
        self.assertFalse(test_case_exists)

    def test_add_termination_event_when_not_existing(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"

        # Act
        self.database.add_termination_event(event_hash, suite_id)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM event_info WHERE event_hash=? AND suite_id=?", (event_hash, suite_id))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], event_hash)
        self.assertEqual(rows[0][1], suite_id)
        self.assertEqual(rows[0][3], 1)

    def test_add_termination_event_when_existing(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"
        self.database.add_termination_event(event_hash, suite_id)

        # Act
        self.database.add_termination_event(event_hash, suite_id)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT * FROM event_info WHERE event_hash=? AND suite_id=?", (event_hash, suite_id))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][3], 1)

    def test_is_termination_event(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"
        self.database.add_termination_event(suite_id, event_hash)

        # Act
        is_termination_event = self.database.is_termination_event(event_hash, suite_id)

        # Assert
        self.assertTrue(is_termination_event)

    def test_is_not_termination_event(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"

        # Act
        is_termination_event = self.database.is_termination_event(suite_id, event_hash)

        # Assert
        self.assertFalse(is_termination_event)

    def test_update_event_frequency_when_not_existing(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"

        # Act
        self.database.update_event_frequency(suite_id, event_hash)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT frequency FROM event_info WHERE suite_id=? AND event_hash=?", (suite_id, event_hash))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 1)

    def test_update_event_frequency_when_existing(self):
        # Arrange
        event_hash = "event_hash"
        suite_id = "suite_id"
        self.database.update_event_frequency(suite_id, event_hash)

        # Act
        self.database.update_event_frequency(suite_id, event_hash)

        # Assert
        cursor = self.database.cursor()
        cursor.execute("SELECT frequency FROM event_info WHERE suite_id=? AND event_hash=?", (suite_id, event_hash))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 2)

    def test_get_event_frequencies_when_all_events_exist(self):
        # Arrange
        event_hashes = ["event_hash_1", "event_hash_2"]
        suite_id = "suite_id"
        self.database.update_event_frequency(suite_id, event_hashes[0])
        self.database.update_event_frequency(suite_id, event_hashes[1])

        # Act
        event_frequencies = self.database.get_event_frequencies(event_hashes, suite_id)

        # Assert
        self.assertEqual(len(event_frequencies), len(event_hashes))
        self.assertEqual(event_frequencies[event_hashes[0]], 1)
        self.assertEqual(event_frequencies[event_hashes[1]], 1)

    def test_get_event_frequencies_when_events_do_not_exist(self):
        # Arrange
        event_hashes = ["event_hash_1", "event_hash_2"]
        suite_id = "suite_id"

        # Act
        event_frequencies = self.database.get_event_frequencies(event_hashes, suite_id)

        # Assert
        self.assertEqual(len(event_frequencies), len(event_hashes))
        self.assertEqual(event_frequencies[event_hashes[0]], 0)
        self.assertEqual(event_frequencies[event_hashes[1]], 0)

    def test_get_event_frequencies_when_only_some_events_exist(self):
        # Arrange
        event_hashes = ["event_hash_1", "event_hash_2", "event_hash_3"]
        suite_id = "suite_id"
        self.database.update_event_frequency(suite_id, event_hashes[0])

        # Act
        event_frequencies = self.database.get_event_frequencies(event_hashes, suite_id)

        # Assert
        self.assertEqual(len(event_frequencies), len(event_hashes))
        self.assertEqual(event_frequencies[event_hashes[0]], 1)
        self.assertEqual(event_frequencies[event_hashes[1]], 0)
        self.assertEqual(event_frequencies[event_hashes[2]], 0)

    def test_can_get_suite_details(self):
        # Arrange
        suite_info = self.database.create_suite()

        # Act
        suite_details = self.database.get_suite_details(suite_info.id)

        # Assert
        self.assertEqual(suite_info.id, suite_details["id"])
        self.assertEqual(suite_info.creation_time, suite_details["creation_time"])
