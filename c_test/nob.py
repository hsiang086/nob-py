#!/usr/bin/env python

import sys
import subprocess
from enum import Enum, verify, UNIQUE
from typing import List, Optional
from datetime import datetime

# Define ANSI escape codes for colors
# These codes work on most modern terminals.
ANSI_RESET = "\033[0m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_CYAN = "\033[36m"
ANSI_BRIGHT_GREEN = "\033[92m" # For success messages

@verify(UNIQUE)
class LogType(Enum):
    """
    Defines different types of log messages.
    Each log type has a unique integer value.
    """
    DEBUG   = 0
    INFO    = 1
    WARNING = 2
    ERROR   = 3
    SUCCESS = 4

class Log:
    """
    A customizable logging class for printing messages to the console
    with syntax highlighting (colors) and optional file logging.
    """
    def __init__(self,
                 type: LogType = LogType.INFO,
                 log_level: LogType = LogType.DEBUG,
                 log_file_path: Optional[str] = None) -> None:
        """
        Initializes the Log instance.

        Args:
            type (LogType): The default type of log message this instance will produce.
            log_level (LogType): The minimum log level to display. Messages below this
                                 level will be ignored.
            log_file_path (Optional[str]): Path to a file where logs should also be written.
                                            If None, file logging is disabled.
        """
        self.type = type
        self.log_level = log_level
        self.log_file_path = log_file_path

    def _get_color(self) -> str:
        """
        Returns the ANSI color code corresponding to the current log type.
        """
        match self.type:
            case LogType.DEBUG:
                return ANSI_CYAN
            case LogType.INFO:
                return ANSI_GREEN
            case LogType.WARNING:
                return ANSI_YELLOW
            case LogType.ERROR:
                return ANSI_RED
            case LogType.SUCCESS:
                return ANSI_BRIGHT_GREEN
            case _: # Fallback for any unknown type
                return ANSI_RESET

    def _format_content(self, content: str) -> str:
        """
        Formats the log content with a timestamp and log type name,
        applying ANSI colors for console output.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = self._get_color()
        # Add color to the log type name and the content
        return f"{color}[{timestamp} {self.type._name_}]: {content}{ANSI_RESET}"

    def log(self, content: str) -> None:
        """
        Logs a message to the console and optionally to a file.
        The message is only logged if its type is at or above the configured log_level.

        Args:
            content (str): The message content to be logged.
        """
        # Check if the current log type is at or above the configured log_level
        if self.type.value < self.log_level.value:
            return

        formatted_content = self._format_content(content)
        plain_content_for_file = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {self.type._name_}]: {content}\n"

        # Print to console
        print(formatted_content)

        # Log to file if path is provided
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(plain_content_for_file)
            except IOError as e:
                # Log an error if file writing fails, but don't stop execution
                error_logger = Log(LogType.ERROR, log_level=self.log_level)
                error_logger.log(f"Failed to write to log file '{self.log_file_path}': {e}")


class Cmd:
    """
    A class for building and running shell commands,
    capturing their output, and managing success/failure.
    """
    def __init__(self, command: str) -> None:
        """
        Initializes the Cmd instance with a base command.

        Args:
            command (str): The base command (e.g., "ls", "echo").
        """
        self.command = command
        self.flags: List[str] = []
        # Default logger for Cmd operations
        self.logger = Log(log_level=LogType.DEBUG) # Can be customized later

    def add_flags(self, flags: List[str]) -> "Cmd":
        """
        Adds a list of flags to the command.

        Args:
            flags (List[str]): A list of string flags (e.g., ["-a", "-l"]).

        Returns:
            Cmd: The current Cmd instance, allowing for method chaining.
        """
        self.flags.extend(flags)
        return self

    def run(self, check_returncode: bool = False) -> subprocess.CompletedProcess:
        """
        Runs the constructed command in a subprocess.

        Args:
            check_returncode (bool): If True, raises a CalledProcessError if the
                                     command returns a non-zero exit code.

        Returns:
            subprocess.CompletedProcess: An object containing the command's
                                        return code, stdout, and stderr.
        """
        full_command = f"{self.command} {' '.join(self.flags)}"
        self.logger.type = LogType.INFO
        self.logger.log(f"Running command: '{full_command}'...")

        try:
            # subprocess.run is generally safer and more flexible than os.system
            # capture_output=True captures stdout and stderr
            # text=True decodes stdout/stderr as text (default encoding)
            # shell=True allows the command string to be executed directly by the shell
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                shell=True,
                check=check_returncode
            )

            if result.returncode == 0:
                self.logger.type = LogType.SUCCESS
                self.logger.log(f"Command '{self.command}' completed successfully.")
            else:
                self.logger.type = LogType.WARNING
                self.logger.log(f"Command '{self.command}' exited with code {result.returncode}.")

            if result.stdout:
                self.logger.type = LogType.INFO
                self.logger.log(f"--- STDOUT ---\n{result.stdout.strip()}")
            if result.stderr:
                self.logger.type = LogType.ERROR
                self.logger.log(f"--- STDERR ---\n{result.stderr.strip()}")

            return result

        except subprocess.CalledProcessError as e:
            # This block is executed if check_returncode was True and the command failed
            self.logger.type = LogType.ERROR
            self.logger.log(f"Command '{self.command}' failed with error: {e}")
            if e.stdout:
                self.logger.log(f"--- STDOUT ---\n{e.stdout.strip()}")
            if e.stderr:
                self.logger.log(f"--- STDERR ---\n{e.stderr.strip()}")
            raise # Re-raise the exception after logging
        except FileNotFoundError:
            self.logger.type = LogType.ERROR
            self.logger.log(f"Command '{self.command}' not found. Please ensure it is in your PATH.")
            raise
        except Exception as e:
            self.logger.type = LogType.ERROR
            self.logger.log(f"An unexpected error occurred while running command '{self.command}': {e}")
            raise

if __name__ == "__main__":
    Cmd("cc").add_flags([
        "./needs_to_link_to_raylib.c",
        "-o",
        "./needs_to_link_to_raylib",
        "-Wall",
        "-O3",
        "-lraylib",
        "-lm",
        "&&",
        "./needs_to_link_to_raylib"
        ]).run()

