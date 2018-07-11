import os
import logging
from collections import namedtuple

logger = logging.getLogger(__name__)


def create_sequence_path(output_path):
    path_to_test_cases = os.path.join(output_path, "testcases")
    if not os.path.exists(path_to_test_cases):
        os.makedirs(path_to_test_cases)
    logger.debug("Test cases are stored in {}.".format(path_to_test_cases))

    return path_to_test_cases


def create_log_path(output_path):
    path_to_logs = os.path.join(output_path, "logs")
    if not os.path.exists(path_to_logs):
        os.makedirs(path_to_logs)
    logger.debug("Logs are stored in {}.".format(path_to_logs))

    return path_to_logs


def create_coverage_path(output_path):
    path_to_coverage = os.path.join(output_path, "coverage")
    if not os.path.exists(path_to_coverage):
        os.makedirs(path_to_coverage)
    logger.debug("Coverage files are stored in {}.".format(path_to_coverage))

    return path_to_coverage


def create_output_directories(apk_package_name, output_path, suite_creation_time):
    logger.debug("APK package name is {}".format(apk_package_name))
    logger.debug("Output path is {}".format(output_path))
    output_path = os.path.join(output_path, "{}_{}".format(apk_package_name, str(suite_creation_time)))

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    path_to_sequences = create_sequence_path(output_path)
    path_to_logs = create_log_path(output_path)
    path_to_coverage = create_coverage_path(output_path)

    OutputPaths = namedtuple("OutputPaths", ["sequences", "logs", "coverage"])
    return OutputPaths(path_to_sequences, path_to_logs, path_to_coverage)