import unittest
from appium import webdriver
from unittest.mock import patch, MagicMock
from abstraction import create_state, create_launch_event, synthesize
from exploration.sequence import SequenceGenerator


class SequenceGeneratorTests(unittest.TestCase):
    @patch("exploration.sequence.get_current_state")
    @patch("exploration.sequence.time")
    def test_can_initialize_sequence(self, time_mock, get_current_state_mock):
        # Arrange
        def setup_strategy():
            return MagicMock(webdriver.Remote)

        time_mock.time.return_value = 10
        start_state = create_state(current_activity=".startActivity",
                                   state_id="state_id")
        get_current_state_mock.return_value = start_state
        sequence_generator = SequenceGenerator(None, None, None, setup_strategy, None, None)

        # Act
        sequence_info = sequence_generator.initialize()

        # Assert
        expected_events = [synthesize(create_launch_event(), start_state)]
        self.assertEqual(sequence_info.events, expected_events)
        self.assertEqual(sequence_info.start_state, start_state)
        self.assertEqual(sequence_info.start_time, 10)


