import unittest
import os
import paths
import shutil


class PathTests(unittest.TestCase):
    def setUp(self):
        home_directory = os.path.expanduser('~')
        self.output_path = os.path.join(home_directory, "autodroid", "output")

    def test_can_create_sequence_path(self):
        path_to_sequences = paths.create_sequence_path(self.output_path)
        self.assertTrue(os.path.exists(path_to_sequences))
        self.assertEqual(path_to_sequences, os.path.join(self.output_path, "sequences"))

    def test_can_create_log_path(self):
        path_to_logs = paths.create_log_path(self.output_path)
        self.assertTrue(os.path.exists(path_to_logs))
        self.assertEqual(path_to_logs, os.path.join(self.output_path, "logs"))

    def test_can_create_coverage_path(self):
        path_to_coverage = paths.create_coverage_path(self.output_path)
        self.assertTrue(os.path.exists(path_to_coverage))
        self.assertEqual(path_to_coverage, os.path.join(self.output_path, "coverage"))

    def test_can_create_output_directories(self):
        output_directories = paths.create_output_directories("org.tomdroid", self.output_path, 123456)
        expected_sequence_path = os.path.join(self.output_path, "org.tomdroid_123456", "sequences")
        expected_logs_path = os.path.join(self.output_path, "org.tomdroid_123456", "logs")
        expected_coverage_path = os.path.join(self.output_path, "org.tomdroid_123456", "coverage")
        self.assertEqual(output_directories.sequences, expected_sequence_path)
        self.assertEqual(output_directories.logs, expected_logs_path)
        self.assertEqual(output_directories.coverage, expected_coverage_path)

    def tearDown(self):
        if os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
