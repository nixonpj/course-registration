import logging
from mongolog.handlers import MongoHandler

"""
A Mongodb based logger used for logging
"""


log = logging.getLogger('demo')
log.setLevel(logging.DEBUG)
# The collection log is created locally using the default local port
log.addHandler(MongoHandler.to(db='mongolog', collection='log'))