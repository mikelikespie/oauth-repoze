"""Setup the oauth-what application"""
import logging

from oauthwhat.config.environment import load_environment
from oauthwhat.model import meta

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup oauthwhat here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    meta.metadata.create_all(bind=meta.engine)
