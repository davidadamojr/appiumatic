import logging
import subprocess

logger = logging.getLogger(__name__)


def clear_sdcard_data(script_path, adb_path):
    clear_sdcard_cmd = "{} {}".format(script_path, adb_path)
    subprocess.check_call(clear_sdcard_cmd, shell=True)
    logger.info("Successfully cleared SD card data.")


def clear_logs(script_path, adb_path):
    clear_logs_cmd = "{} {}".format(script_path, adb_path)
    subprocess.check_call(clear_logs_cmd, shell=True)
    logger.info("Successfully cleared logs.")


def get_process_id(script_path, adb_path, package_name):
    process_id_cmd = "{} {} {}".format(script_path, adb_path, package_name)
    process = subprocess.Popen(process_id_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = process.communicate()
    process_id = output.decode("utf-8").strip()
    logger.info("Process id for {} is {}.".format(package_name, adb_path))
    return process_id


def get_coverage(script_path, adb_path, device_path, coverage_path, coverage_name, broadcast):
    coverage_file_path = self.configuration["coverage_file_path"] + "/coverage.ec"
    coverage_file_name = "coverage{}.ec".format(str(test_case_count + 1).zfill(3))
    coverage_broadcast = self.configuration["coverage_broadcast"]
    adb.get_coverage(self.configuration["adb_path"], coverage_file_path, coverage_path, coverage_file_name,
                     coverage_broadcast)
    get_coverage_cmd = "{} {} {} {} {} {}".format(script_path, adb_path, device_path, coverage_path,
                                                  coverage_name, broadcast)
    subprocess.call(get_coverage_cmd, shell=True)
    logger.info("Successfully retrieved coverage file: {}.".format(coverage_name))


def get_logs(script_path, adb_path, log_file_path, process_id):
    get_logs_cmd = "{} {} {} {}".format(script_path, adb_path, log_file_path, process_id)
    subprocess.call(get_logs_cmd, shell=True)
    logger.info("Successfully retrieved log file: {}".format(log_file_path))

    log_file_name = "log{}.txt".format(str(test_case_count + 1).zfill(3))
    log_file_path = os.path.join(logs_path, log_file_name)
    app_process_id = adb.get_process_id(adb_path, apk_package_name)
    adb.get_logs(adb_path, log_file_path, app_process_id)

