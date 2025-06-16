import logging
import os
from flask import Flask, jsonify, render_template_string, request

from writeragents.agents.writer_agent.agent import WriterAgent

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
agent = WriterAgent()

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
  log.innerHTML += `<div><b>Agent:</b> ${data.response}</div>`;
  log.scrollTop = log.scrollHeight;
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
    response = agent.run(msg)
    app.logger.info("Agent: %s", response)
    return jsonify({'response': response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
