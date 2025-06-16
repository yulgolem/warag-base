from writeragents.web.app import app


def test_chat_endpoint():
    client = app.test_client()
    resp = client.post('/chat', json={'message': 'hello'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'Echo:' in data['response']

