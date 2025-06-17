# Story Structure Analysis

The story-structure analyst evaluates scene order and pacing. It will use
narrative templates to suggest revisions that strengthen the overall plot.

## Dynamic templates

The default configuration divides stories into the classic three acts. You can
define your own structure in ``config/local.yaml`` under ``story_structure``.
Specify an ordered list of section names::

  story_structure:
    template: [setup, confrontation, climax, denouement]

The ``StoryStructureAnalyst`` will split the text evenly across these sections
and report the word counts for each one.
