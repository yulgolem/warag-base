from writeragents.web.app import app
from writeragents.llm.client import LLMClient
from writeragents.agents.wba.agent import WorldBuildingArchivist


def test_chat_endpoint(monkeypatch):
    def fake_gen(self, prompt, *, log=None):
        if log is not None:
            log.append('gen')
        return 'result'

    monkeypatch.setattr(LLMClient, 'generate', fake_gen)
    client = app.test_client()
    resp = client.post('/chat', json={'message': 'hello'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['response'] == 'result'
    assert data['logs'] == ['gen']


def test_load_samples_endpoint(monkeypatch):
    called = {}

    def fake_load(self, path, *, log=None):
        called['path'] = path
        if log is not None:
            log.append('done')

    monkeypatch.setattr(WorldBuildingArchivist, 'load_markdown_directory', fake_load)
    monkeypatch.setenv('WBA_DOCS', '/tmp/docs')
    client = app.test_client()
    resp = client.get('/load-samples')
    assert resp.status_code == 200
    assert called['path'] == '/tmp/docs'
    data = resp.get_json()
    assert data['message'] == 'Loaded'
    assert data['logs'] == ['done']


def test_clear_store_endpoint(monkeypatch):
    called = {}

    def fake_clear(self, *, log=None):
        called['cleared'] = True
        if log is not None:
            log.append('cleared')

    monkeypatch.setattr(WorldBuildingArchivist, 'clear_rag_store', fake_clear)
    client = app.test_client()
    resp = client.get('/clear-store')
    assert resp.status_code == 200
    assert called == {'cleared': True}
    data = resp.get_json()
    assert data['message'] == 'Cleared'
    assert data['logs'] == ['cleared']

