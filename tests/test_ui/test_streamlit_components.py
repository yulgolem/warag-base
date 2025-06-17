from src.ui import components


def test_components_exist():
    assert hasattr(components, "log_expander")
    assert hasattr(components, "json_expander")
