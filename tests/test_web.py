from writeragents.web.app import app
from writeragents.llm.client import LLMClient


def test_chat_endpoint(monkeypatch):
    monkeypatch.setattr(LLMClient, 'generate', lambda self, prompt: 'result')
    client = app.test_client()
    resp = client.post('/chat', json={'message': 'hello'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['response'] == 'result'

