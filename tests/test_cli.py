import os
import sys

import yaml
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cli import main


def test_default_config_loading():
    config, db_mem, redis_mem = main([])
    with open('config/local.yaml') as fh:
        expected = yaml.safe_load(fh)

    assert config == expected
    assert db_mem.url == expected['storage']['database_url']
    assert redis_mem.host == expected['storage']['redis_host']


def test_env_overrides(monkeypatch):
    monkeypatch.setenv('WRITERAGENTS_CONFIG', 'config/remote.yaml')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///override.db')
    monkeypatch.setenv('REDIS_HOST', 'example.com')

    config, db_mem, redis_mem = main([])
    with open('config/remote.yaml') as fh:
        expected = yaml.safe_load(fh)

    assert config == expected
    assert db_mem.url == 'sqlite:///override.db'
    assert redis_mem.host == 'example.com'
