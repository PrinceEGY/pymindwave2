"""Provides a centralized logging configuration and management."""

import logging


class Logger:
    """A utility class for configuring and managing loggers in the application.

    It configures logging with both file and console output,
    using a consistent format across all loggers.
    """

    _logger = None

    @classmethod
    def configure_logger(
        cls,
        level: str = "INFO",
        filename: str = "mindwave.log",
        filemode: str = "w",
        console_output: bool = True,
        file_output: bool = True,
    ) -> None:
        """Configures the logger with the specified level and output options.

        Args:
            level (str): The logging level to use.
                Possible values are "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
            filename (str): The name of the file to write logs to.
            filemode (str): The mode to open the log file in.
            console_output (bool): Whether to enable logging to console.
            file_output (bool): Whether to enable logging to file.

        Raises:
            ValueError: If both console_output and file_output are False.

        Examples:
            >>> # Basic usage with default settings (both console and file logging)
            >>> MyClass.configure_logger()

            >>> # Debug level logging to console only
            >>> MyClass.configure_logger(
            ...     level="DEBUG",
            ...     console_output=True,
            ...     file_output=False
            ... )

            >>> # Error level logging to specific file in append mode
            >>> MyClass.configure_logger(
            ...     level="ERROR",
            ...     filename="errors.log",
            ...     filemode="a",
            ...     console_output=False,
            ...     file_output=True
            ... )

            >>> # Multiple output logging with custom configuration
            >>> MyClass.configure_logger(
            ...     level="INFO",
            ...     filename="application.log",
            ...     filemode="w",
            ...     console_output=True,
            ...     file_output=True
            ... )

            The resulting log entries will look like:
            2024-01-12 10:30:45,123 [INFO] my_module::MyClass.my_function - Log message here
        """
        if not (console_output or file_output):
            raise ValueError("At least one logging output (console or file) must be enabled")

        cls._logger = logging.getLogger()
        cls._logger.handlers.clear()  # Clear any existing handlers

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s::%(name)s.%(funcName)s - %(message)s")

        if console_output:
            st_handler = logging.StreamHandler()
            st_handler.setFormatter(formatter)
            st_handler.setLevel(level)
            cls._logger.addHandler(st_handler)

        if file_output:
            f_handler = logging.FileHandler(filename, mode=filemode)
            f_handler.setFormatter(formatter)
            f_handler.setLevel(level)
            cls._logger.addHandler(f_handler)

        cls._logger.setLevel(level)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Gets a named logger instance.

        Args:
            name: A string specifying the logger name, typically the module or
                 component name.

        Returns:
            logging.Logger: A configured logger instance with the specified name.

        Examples:
            >>> logger = Logger.get_logger(__name__)
            >>> logger.info("This is a log message from the module.")
        """
        if cls._logger is None:
            cls.configure_logger()
        return cls._logger.getChild(name)
