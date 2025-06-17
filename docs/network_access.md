# Network Troubleshooting

If `pip install` fails with a message like:

```
Some requests were blocked due to network access restrictions. Consider granting access in environment settings.
    files.pythonhosted.org: via pip install and other commands
```

make sure the environment allows outgoing HTTPS requests to `files.pythonhosted.org`.
You can also set the package index explicitly:

```bash
pip install --index-url https://pypi.org/simple -r requirements.txt
```

Or configure `pip.conf` so the index is always set:

```
[global]
index-url = https://pypi.org/simple
```

With access enabled and the index configured, package downloads should succeed.
