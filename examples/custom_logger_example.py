import logging

from vkpymusic import Service
from vkpymusic.utils import create_logger

# Here we create a Service object with a base configuration:
# 1. INFO level logging to the console
# 2. WARNING level logging to the file
service = Service.parse_config()

# Here we set the base logger with custom configuration:
# 1. Disable logging to the console
# 2. WARNING level logging to the file
logger1 = create_logger("logger1", console=False, file=True)
service.set_logger(logger1) # or Service.set_logger(logger1)

# Here we set the custom logger with custom configuration:
# 1. Disable logging to the console
# 2. INFO level logging to the file
logger2 = logging.getLogger("logger2")
logger2.setLevel(logging.INFO)
service.set_logger(logger2) # or Service.set_logger(logger2)