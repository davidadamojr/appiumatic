import time
import collections
import logging
from abstraction import create_launch_event, create_home_event, create_back_event, synthesize, make_event_serializable
from ui_analysis import get_available_events, get_current_state
from hashing import generate_sequence_hash, generate_event_hash
from exploration.utils import remove_termination_events, write_sequence_to_file, explored_beyond_boundaries

logger = logging.getLogger(__name__)


class SequenceGenerator:
    def __init__(self,
                 database,
                 termination_criterion,
                 event_selection_strategy,
                 setup_strategy,
                 tear_down_strategy,
                 executor_factory):
        self.database = database
        self.termination_criterion = termination_criterion
        self.event_selection_strategy = event_selection_strategy
        self.setup_strategy = setup_strategy
        self.tear_down_strategy = tear_down_strategy
        self.executor_factory = executor_factory

    def generate(self, sequence_info, app_package_name, suite_id):
        current_state = sequence_info.start_state
        executor = self.executor_factory(driver=sequence_info.driver)
        while not self.termination_criterion(database=self.database,
                                             sequence_hash=generate_sequence_hash(sequence_info.events),
                                             suite_id=suite_id,
                                             event_count=len(sequence_info.events)):
            next_event_info = self.process_next_event(sequence_info, suite_id, executor)
            current_state = next_event_info.resulting_state
            self.update_knowledge_base(suite_id, next_event_info, sequence_info)
            sequence_info.events.append(next_event_info.event)

            # end the sequence if event explores beyond boundary of the application
            if explored_beyond_boundaries(sequence_info.driver.current_package, app_package_name):
                self.database.add_termination_event(next_event_info.event_hash, suite_id)
                logger.debug("Identified termination event: {}".format(next_event_info.event_hash))
                break

        # always end sequences by clicking the home event, but do not add the event to the test case
        home_event = create_home_event(current_state)
        executor.execute(home_event)

        return int(time.time() - sequence_info.start_time)

    def initialize(self):
        start_time = int(time.time())

        driver = self.setup_strategy()
        launch_event = create_launch_event()
        start_state = get_current_state(driver)
        complete_event = synthesize(launch_event, start_state)
        events = [complete_event]
        logger.debug("Test case initialization complete.")

        SequenceInfo = collections.namedtuple("SequenceInfo", ["driver", "events", "start_time", "start_state"])
        return SequenceInfo(driver, events, start_time, start_state)

    def process_next_event(self, sequence_info, suite_id, executor):
        selected_event = self.choose_event(sequence_info, suite_id)
        executor.execute(selected_event)
        resulting_state = get_current_state(sequence_info.driver)
        complete_event = synthesize(selected_event, resulting_state)
        event_hash = generate_event_hash(complete_event)
        NextEventInfo = collections.namedtuple("NextEventInfo", ["event", "event_hash", "resulting_state"])
        return NextEventInfo(complete_event, event_hash, resulting_state)

    def choose_event(self, sequence_info, suite_id):
        partial_events = get_available_events(sequence_info.driver)
        non_termination_events = remove_termination_events(self.database, suite_id, partial_events)
        if non_termination_events:
            selected_event = self.event_selection_strategy(events=non_termination_events,
                                                           database=self.database,
                                                           suite_id=suite_id)
        else:
            logger.warning("No events available for selection. All events in the current state are marked as "
                           "termination events.")
            current_state = partial_events[0]["precondition"]
            selected_event = create_back_event(current_state)

        return selected_event

    def update_knowledge_base(self, suite_id, next_event_info, sequence_info):
        self.database.update_event_frequency(suite_id, next_event_info.event_hash)

    def finalize(self, sequence_count, suite_id, sequence_info, output_paths):
        end_time = time.time()
        sequence_duration = int(end_time - sequence_info.start_time)
        self.database.add_sequence(generate_sequence_hash(sequence_info.events),
                                   suite_id,
                                   sequence_info.start_time,
                                   sequence_duration)
        sequence_path = write_sequence_to_file(output_paths.sequences,
                                               sequence_info.events,
                                               sequence_count,
                                               sequence_duration)
        logger.debug("Sequence {} written to {}.".format(sequence_count, sequence_path))

        logger.debug("Beginning test case teardown.")
        self.tear_down_strategy(sequence_info.driver)


