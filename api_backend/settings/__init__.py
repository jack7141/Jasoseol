import os

ENV_TYPE = os.getenv('RUNNING_ENV', 'local')

try:
    exec('from .{} import *'.format(ENV_TYPE))
except ImportError:
    from .base import *
