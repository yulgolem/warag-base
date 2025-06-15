import yaml
from importlib import resources

from writeragents.cli import main


def test_default_config_loading():
    config, db_mem, redis_mem = main([])
    text = resources.files("writeragents").joinpath("config/local.yaml").read_text()
    expected = yaml.safe_load(text)

    assert config == expected
    assert db_mem.url == expected['storage']['database_url']
    assert redis_mem.host == expected['storage']['redis_host']
