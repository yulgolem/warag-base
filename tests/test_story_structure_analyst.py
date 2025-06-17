from writeragents.agents.story_structure_analyst.agent import StoryStructureAnalyst


def test_detect_unresolved_subplots():
    text = (
        "The quest begins. Subplot treasure surfaces. The hero searches. "
        "Another twist. Subplot treasure still missing. The end."
    )
    agent = StoryStructureAnalyst()
    unresolved = agent.find_unresolved_subplots(text)
    assert "treasure" in unresolved


def test_custom_template_split():
    text = "one two three four five six"
    agent = StoryStructureAnalyst(template=["start", "middle", "end"])
    acts = agent.analyze_structure(text)
    assert list(acts.keys()) == ["start", "middle", "end"]
    assert acts["start"].split() == ["one", "two"]
