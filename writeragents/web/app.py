import logging
import os
from pathlib import Path
from flask import Flask, jsonify, render_template_string, request

from writeragents.agents.orchestrator.agent import Orchestrator

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
agent = Orchestrator()

INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>WriterAgents Chat</title>
  <style>
    body { font-family: sans-serif; margin: 2em; }
    #log { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
    #input { width: 80%; }
  </style>
</head>
<body>
  <div id='log'></div>
  <form id='form'>
    <input id='input' autocomplete='off'/>
    <button>Send</button>
  </form>
  <button id='load'>Load samples</button>
  <button id='clear'>Clear store</button>
<script>
const log = document.getElementById('log');
const form = document.getElementById('form');
form.onsubmit = async (e) => {
  e.preventDefault();
  const text = document.getElementById('input').value;
  log.innerHTML += `<div><b>You:</b> ${text}</div>`;
  document.getElementById('input').value = '';
  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text })
  });
  const data = await res.json();
  for (const line of data.logs) {
    log.innerHTML += `<div><i>${line}</i></div>`;
  }
  log.innerHTML += `<div><b>Agent:</b> ${data.response}</div>`;
  log.scrollTop = log.scrollHeight;
};
document.getElementById('load').onclick = async () => {
  const r = await fetch('/load-samples');
  const d = await r.json();
  for (const line of d.logs) {
    log.innerHTML += `<div><i>${line}</i></div>`;
  }
  log.innerHTML += `<div><i>${d.message}</i></div>`;
};
document.getElementById('clear').onclick = async () => {
  const r = await fetch('/clear-store');
  const d = await r.json();
  for (const line of d.logs) {
    log.innerHTML += `<div><i>${line}</i></div>`;
  }
  log.innerHTML += `<div><i>${d.message}</i></div>`;
};
</script>
</body>
</html>
"""


@app.route('/')
def index() -> str:
    """Return the chat page."""
    return render_template_string(INDEX_HTML)


@app.route('/chat', methods=['POST'])
def chat():
    """Return agent response to posted message."""
    msg = request.json.get('message', '')
    app.logger.info("User: %s", msg)
    logs: list[str] = []
    response = agent.run(msg, log=logs)
    app.logger.info("Agent: %s", response)
    return jsonify({'response': response, 'logs': logs})


@app.route('/load-samples')
def load_samples():
    """Load sample markdown files into the archive."""
    sample_dir = os.environ.get(
        'WBA_DOCS',
        str(Path(__file__).resolve().parent.parent.parent / 'docs' / 'wba_samples'),
    )
    logs: list[str] = []
    agent.wba.load_markdown_directory(sample_dir, log=logs)
    return jsonify({'message': 'Loaded', 'logs': logs})


@app.route('/clear-store')
def clear_store():
    """Clear archived records from the RAG store."""
    logs: list[str] = []
    agent.wba.clear_rag_store(log=logs)
    return jsonify({'message': 'Cleared', 'logs': logs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
