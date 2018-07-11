import time
import json
import collections
import os
import logging
import adb
import paths
from selenium.common.exceptions import WebDriverException
from abstraction import create_launch_event, create_home_event, create_back_event, synthesize, make_event_serializable
from ui_analysis import get_available_events, get_current_state
from hashing import generate_sequence_hash, generate_event_hash

logger = logging.getLogger(__name__)


def write_sequence_to_file(path_to_sequence, events, sequence_count, sequence_duration):
    sequence_count = str(sequence_count + 1).zfill(3)
    sequence_path = os.path.join(path_to_sequence, "tc{}_{}.json".format(sequence_count, sequence_duration))
    serializable_events = [make_event_serializable(event) for event in events]
    sequence_data = {
        "events": serializable_events,
        "length": len(events)
    }

    with open(sequence_path, 'w') as sequence_file:
        json.dump(sequence_data, sequence_file, sort_keys=True)

    return sequence_path


class SequenceGenerator:
    def __init__(self, database):
        self.database = database

    def remove_termination_events(self, test_suite_id, events):
        non_termination_events = []
        for event in events:
            event_hash = generate_event_hash(event)
            if self.database.is_termination_event(test_suite_id, event_hash):
                logger.debug("Removing termination event {}".format(event_hash))
                continue

            non_termination_events.append(event)

        return non_termination_events

    @staticmethod
    def initialize_sequence(apk_path, adb_path, setup_strategy):
        logger.debug("Path to APK is {}".format(apk_path))
        driver = setup_strategy(apk_path, adb_path)

        start_time = time.time()
        launch_event = create_launch_event()
        start_state = get_current_state(driver)
        complete_event = synthesize(launch_event, start_state)
        events = [complete_event]
        logger.debug("Test case initialization complete.")

        TestCase = collections.namedtuple("TestCase", ["driver", "events", "start_time", "start_state"])
        return TestCase(driver, events, start_time, start_state)

    def update_knowledge_base(self, test_suite, next_event, test_case):
        self.database.update_event_frequency(test_suite.id, next_event.event_hash)

    def generate_events(self, executor, test_case, test_suite, event_selection_strategy, termination_criterion):
        event_count = len(test_case.events)
        current_state = test_case.start_state
        while not termination_criterion(self.database, test_case_hash=generate_sequence_hash(test_case.events),
                                        event_count=event_count, test_suite_id=test_suite.id):
            next_event = self.process_next_event(executor, test_suite.id, event_selection_strategy)
            self.update_knowledge_base(test_suite, next_event, test_case)

            current_state = next_event.resulting_state
            test_case.events.append(next_event.event)
            event_count += 1

            # end the test case if event explores beyond boundary of the application under test
            current_package = test_case.driver.current_package
            if current_package != self.configuration["apk_package_name"]:
                self.database.add_termination_event(next_event.event_hash, test_suite.id)
                logger.debug("Identified termination event: {}".format(next_event.event))
                break

        return current_state

    def finalize_test_case(self, test_case, test_suite, path_to_test_cases, test_case_count):
        end_time = time.time()
        test_case_duration = int(end_time - test_case.start_time)
        self.database.add_test_case(generate_sequence_hash(test_case.events), test_suite.id, end_time,
                                    test_case_duration)
        test_case_path = write_sequence_to_file(path_to_test_cases, test_case.events, test_case_count,
                                                test_case_duration)
        logger.debug("Test case {} written to {}.".format(test_case_count, test_case_path))


class SuiteGenerator:
    def __init__(self, database, sequence_generator, configuration):
        self.database = database
        self.sequence_generator = sequence_generator
        self.configuration = configuration

    def construct_suite(self, completion_criterion):

        suite_duration = 0
        sequence_count = 0
        while not completion_criterion(test_duration=suite_duration, test_case_count=sequence_count):
            try:
                test_case = self.initialize_test_case(setup_strategy)
                logger.debug(
                    "Generating test case {}. Start time is {}.".format(sequence_count + 1, test_case.start_time))
                executor = executor_factory(test_case.driver, self.configuration["event_interval"],
                                            self.configuration["text_entry_values"])
                final_state = self.generate_events(executor, test_case, test_suite_info, event_selection_strategy,
                                                   termination_criterion)
            except WebDriverException as e:
                print(e)
                continue  # start a new test case

            # always end test cases by clicking the home event, but do not add the event to the test case
            home_event = create_home_event(final_state)
            executor.execute(home_event)

            self.get_coverage(output_paths.coverage, sequence_count)
            self.get_logs(output_paths.logs, sequence_count)
            self.finalize_test_case(test_case, test_suite_info, output_paths.test_cases, sequence_count)
            sequence_count += 1

            logger.debug("Beginning test case teardown.")
            teardown_strategy(test_case.driver, self.configuration["adb_path"])

        test_suite_end_time = int(time.time())
        suite_duration = test_suite_end_time - test_suite_info.creation_time
        self.database.update_test_suite(test_suite_info.id, test_suite_end_time, suite_duration)
        print("Test suite generation took {} seconds.".format(suite_duration))

