import os
from datetime import datetime

class LogManager:
    def __init__(self):
        self.log_directory = "./logs"
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            self.default_user = "DummyUser"
        print(f"Logs will be saved to: {os.path.abspath(self.log_directory)}") 


    def _get_log_file_name(self):
        # generates a log file name based on the current date
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_directory, f"logs_{today}.log")

    # logs an action to the daily log file

    def log_action(self, username, action, details):
        filename = self._get_log_file_name()
        with open(filename, "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp} - {username} - {action} - {details}\n"
            file.write(log_entry)
