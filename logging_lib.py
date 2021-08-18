import logging
import logging.handlers


class Logger:
    def __init__(self):
        LOG_FILENAME = "/var/log/website_monitor.log"
        LOG_LEVEL = logging.INFO

        # Configure logging to log to a file
        self.logger = logging.getLogger(__name__)
        # Set the log level to LOG_LEVEL
        self.logger.setLevel(LOG_LEVEL)
        # Make a handler that writes to a file, making a new file at midnight
        # and keeping 30 backups
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME,
                                                            when="midnight",
                                                            backupCount=30)
        # Format each log message like this
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)-8s %(message)s')
        # Attach the formatter to the handler
        handler.setFormatter(formatter)
        # Attach the handler to the logger
        self.logger.addHandler(handler)


# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            if self.level == logging.ERROR:
                self.logger.error(message)
            else:
                self.logger.info(message)


log = Logger()
