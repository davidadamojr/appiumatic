import json
import logging
import os
from abstraction import make_event_serializable
from hashing import generate_event_hash

logger = logging.getLogger(__name__)


def write_sequence_to_file(path_to_sequence, events, sequence_count, sequence_duration):
    sequence_count = str(sequence_count).zfill(3)
    sequence_path = os.path.join(path_to_sequence, "tc{}_{}.json".format(sequence_count, sequence_duration))
    serializable_events = [make_event_serializable(event) for event in events]
    sequence_data = {
        "events": serializable_events,
        "length": len(events)
    }

    with open(sequence_path, 'w') as sequence_file:
        json.dump(sequence_data, sequence_file, sort_keys=True)

    return sequence_path


def remove_termination_events(database, suite_id, events):
    non_termination_events = []
    for event in events:
        event_hash = generate_event_hash(event)
        if database.is_termination_event(suite_id, event_hash):
            logger.debug("Removing termination event {}".format(event_hash))
            continue

        non_termination_events.append(event)

    return non_termination_events


def explored_beyond_boundaries(current_package, app_package_name):
    if current_package != app_package_name:
        return True

    return False
