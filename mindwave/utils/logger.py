"""Provides a centralized logging configuration and management."""

import logging


class Logger:
    """A utility class for configuring and managing loggers in the application.

    It configures logging with both file and console output,
    using a consistent format across all loggers.
    """

    _logger = None

    @classmethod
    def configure_logger(cls, level: str = "INFO", filename: str = "mindwave.log", filemode: str = "w") -> None:
        """Configures the logger with the specified level and output file.

        Args:
            level (str): The logging level to use.
            Possible values are "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
            filename (str): The name of the file to write logs to.
            filemode (str): The mode to open the log file in.
        """
        cls._logger = logging.getLogger()
        st_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(filename, mode=filemode)
        f_handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s::%(name)s.%(funcName)s - %(message)s")
        f_handler.setFormatter(formatter)
        st_handler.setFormatter(formatter)
        cls._logger.addHandler(st_handler)
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

        Example:
            >>> logger = Logger.get_logger(self.__class__.__name__)
            >>> logger.info("This is an info message")
        """
        if cls._logger is None:
            cls.configure_logger()
        return cls._logger.getChild(name)
