import os
import sys

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cli import main


def test_default_config_loading():
    config, db_mem, redis_mem = main([])
    with open('config/local.yaml') as fh:
        expected = yaml.safe_load(fh)

    assert config == expected
    assert db_mem.url == expected['storage']['database_url']
    assert redis_mem.host == expected['storage']['redis_host']
