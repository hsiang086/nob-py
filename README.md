nob-pyNob (no build) is a simple Python library for logging and command execution with syntax highlighting, designed for projects that don't require complex build processes. It provides an easy way to print colored log messages to the console and run shell commands, capturing their output and return codes.FeaturesSyntax Highlighting: Log messages are automatically colored (INFO: Green, WARNING: Yellow, ERROR: Red, DEBUG: Cyan, SUCCESS: Bright Green) for better readability in the terminal.Timestamps: All log messages include a timestamp.Logging Levels: Control the verbosity of your logs by setting a minimum display level (e.g., only show warnings and errors).File Logging: Option to duplicate all console logs to a specified file.Command Execution: Run shell commands, capture their standard output and error, and check their return codes.Return Code Checking: Automatically raise a Python exception if a command exits with a non-zero status.InstallationSince nob-py is designed to be a "no build" library, you don't need pip or any complex installation steps.Download nob.py: Simply download the nob.py file directly into your project directory.Import: You can then import it in your Python scripts like any other local module:from nob import Log, LogType, Cmd
UsageLogging Examplefrom nob import Log, LogType

## Quick Install

Just drop **nob.py** into your project with curl or wget:

```bash
# with curl
curl -sSL https://raw.githubusercontent.com/hsiang086/nob-py/main/nob.py -o nob.py

# or with wget
wget -qO nob.py https://raw.githubusercontent.com/hsiang086/nob-py/main/nob.py


# use it directly
if __name__ == "__main__":
    Cmd("ls").add_flags("-la").run()
```

# Log different types of messages
my_logger.type = LogType.INFO
my_logger.log("This is an informational message.")

my_logger.type = LogType.WARNING
my_logger.log("Something might need attention here.")

my_logger.type = LogType.ERROR
my_logger.log("An error occurred!")

my_logger.type = LogType.DEBUG
my_logger.log("Debugging details (won't show if log_level is higher than DEBUG).")

my_logger.type = LogType.SUCCESS
my_logger.log("Operation completed successfully!")

# Logger with a specific log level and file output
file_and_warning_logger = Log(log_level=LogType.WARNING, log_file_path="app_events.log")
file_and_warning_logger.type = LogType.INFO
file_and_warning_logger.log("This info message will NOT be printed to console, but WILL be written to 'app_events.log' (if log_level is lower).")
file_and_warning_logger.type = LogType.ERROR
file_and_warning_logger.log("This error message will be printed and logged to file.")
Command Execution Examplefrom nob import Cmd, LogType

# Run a simple command
print("\n--- Running 'ls -l' ---")
cmd_ls = Cmd("ls").add_flags(["-l", "-a"])
result_ls = cmd_ls.run()
print(f"ls command exited with code: {result_ls.returncode}")

# Run a command that is expected to fail and catch the error
print("\n--- Running a failing command with error checking ---")
try:
    # On Unix: 'false', On Windows: 'cmd /c exit 1' or 'powershell -command "exit 1"'
    failing_command = "false" # Adjust for your OS if needed
    cmd_fail = Cmd(failing_command)
    cmd_fail.run(check_returncode=True) # This will raise an exception
except Exception as e:
    print(f"Caught expected exception for failing command: {e}")

# Customize the logger for Cmd
print("\n--- Running 'echo' with a custom logger ---")
custom_logger_for_cmd = Log(log_level=LogType.INFO, log_file_path="cmd_log.txt")
cmd_echo = Cmd("echo").add_flags(["Hello from nob-py!"])
cmd_echo.logger = custom_logger_for_cmd # Assign the custom logger
cmd_echo.run()
ContributingFeel free to contribute to this "no build" utility! If you have suggestions or find issues, please open an issue on the GitHub repository.LicenseThis project is licensed under the MIT License - see the pyproject.toml for details.
