import requests
from writeragents.llm.client import LLMClient
from writeragents.agents.creativity_assistant.agent import CreativityAssistant
from writeragents.agents.rag_search.agent import RAGSearchAgent
from writeragents.agents.wba.agent import WorldBuildingArchivist
from writeragents.storage import RAGEmbeddingStore


def test_llmclient_openai(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured['url'] = url
        captured['payload'] = json
        return type('R', (), {
            'json': lambda self: {'choices': [{'message': {'content': 'ok'}}]},
            'raise_for_status': lambda self: None,
        })()

    monkeypatch.setattr(requests, 'post', fake_post)
    client = LLMClient(endpoint='http://example.com/v1', model='gpt', api_key='k')
    assert client.generate('hi') == 'ok'
    assert captured['url'].endswith('/chat/completions')
    assert captured['payload']['model'] == 'gpt'


def test_llmclient_ollama(monkeypatch):
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured['url'] = url
        captured['payload'] = json
        return type('R', (), {
            'json': lambda self: {'response': 'fine'},
            'raise_for_status': lambda self: None,
        })()

    monkeypatch.setattr(requests, 'post', fake_post)
    client = LLMClient(endpoint='http://localhost:11434', model='llama')
    assert client.generate('hi') == 'fine'
    assert captured['url'].endswith('/api/generate')
    assert 'stream' in captured['payload']


def test_creativity_assistant(monkeypatch):
    monkeypatch.setattr(LLMClient, 'generate', lambda self, prompt: 'idea')
    agent = CreativityAssistant(llm_client=LLMClient(endpoint='x'))
    assert agent.run('text') == 'idea'


def test_rag_search_agent(monkeypatch):
    store = RAGEmbeddingStore()
    wba = WorldBuildingArchivist(store=store)
    wba.archive_text('Dragons live in the north.')
    monkeypatch.setattr(LLMClient, 'generate', lambda self, prompt: 'summary')
    agent = RAGSearchAgent(archivist=wba, llm_client=LLMClient(endpoint='x'))
    assert agent.run('Where do dragons live?') == 'summary'
