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


def test_check_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'checked:' + text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'consistency_checker', type('CC', (), {'run': fake_run})())
    result = orch.run('check: passage')
    assert called['text'] == 'passage'
    assert result == 'checked:passage'


def test_consistency_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'checked:' + text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'consistency_checker', type('CC', (), {'run': fake_run})())
    result = orch.run('consistency: story')
    assert called['text'] == 'story'
    assert result == 'checked:story'


def test_creative_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'idea:' + text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'creativity_assistant', type('CA', (), {'run': fake_run})())
    result = orch.run('creative: spark')
    assert called['text'] == 'spark'
    assert result == 'idea:spark'


def test_brainstorm_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'idea:' + text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'creativity_assistant', type('CA', (), {'run': fake_run})())
    result = orch.run('brainstorm: spark')
    assert called['text'] == 'spark'
    assert result == 'idea:spark'


def test_search_intent(monkeypatch):
    called = {}

    def fake_run(self, text):
        called['text'] = text
        return 'found:' + text

    orch = Orchestrator()
    monkeypatch.setattr(orch, 'rag_search_agent', type('RS', (), {'run': fake_run})())
    result = orch.run('search: query')
    assert called['text'] == 'query'
    assert result == 'found:query'
