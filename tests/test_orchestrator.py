from writeragents.agents.orchestrator.agent import Orchestrator


def test_default_routes_to_writer(monkeypatch):
    called = {}

    def fake_writer_run(self, prompt):
        called['writer'] = prompt
        return 'writer:' + prompt

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'writer_agent', type('W', (), {'run': fake_writer_run})())
    response = orch.run('hello there')
    assert called['writer'] == 'hello there'
    assert 'writer:' in response


def test_archive_intent(monkeypatch):
    called = {}

    def fake_archive(self, text):
        called['archive'] = text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'wba', type('WBA', (), {'archive_text': fake_archive})())
    result = orch.run('archive: test text')
    assert called['archive'] == 'test text'
    assert result == 'Archived'


def test_structure_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'report'

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'structure_analyst', type('S', (), {'run': fake_run})())
    result = orch.run('structure: the story')
    assert called['text'] == 'the story'
    assert result == 'report'
