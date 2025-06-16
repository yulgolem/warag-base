class WriterAgent:
    """Coordinates other agents and produces the final narrative."""

    def run(self, prompt):
        """Generate a text response for ``prompt``.

        This placeholder implementation simply echoes the prompt back. It
        allows the CLI and Web UI to provide basic interaction while the
        full agent workflow is still under development.
        """
        return f"Echo: {prompt}"
