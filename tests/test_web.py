from writeragents.web.app import app
from writeragents.llm.client import LLMClient
from writeragents.agents.wba.agent import WorldBuildingArchivist


def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(LLMClient, 'generate', lambda self, prompt: 'result')
    client = app.test_client()
    resp = client.post('/chat', json={'message': 'hello'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['response'] == 'result'


def test_load_samples_endpoint(monkeypatch):
    called = {}

    def fake_load(self, path):
        called['path'] = path

    monkeypatch.setattr(WorldBuildingArchivist, 'load_markdown_directory', fake_load)
    monkeypatch.setenv('WBA_DOCS', '/tmp/docs')
    client = app.test_client()
    resp = client.get('/load-samples')
    assert resp.status_code == 200
    assert called['path'] == '/tmp/docs'
    assert resp.get_json()['message'] == 'Loaded'


def test_clear_store_endpoint(monkeypatch):
    called = {}

    def fake_clear(self):
        called['cleared'] = True

    monkeypatch.setattr(WorldBuildingArchivist, 'clear_rag_store', fake_clear)
    client = app.test_client()
    resp = client.get('/clear-store')
    assert resp.status_code == 200
    assert called == {'cleared': True}
    assert resp.get_json()['message'] == 'Cleared'

