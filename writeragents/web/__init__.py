"""Simple Flask web interface."""

# Lazily import the Flask app so running ``python -m writeragents.web.app``
# does not trigger a ``RuntimeWarning`` about the module already being in
# ``sys.modules``.  Importing only when the ``app`` attribute is accessed
# avoids premature execution when the package is loaded.

def __getattr__(name):
    if name == "app":
        from .app import app
        return app
    raise AttributeError(name)

__all__ = ["app"]
