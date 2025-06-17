import tiktoken
from src.utils.chunking import recursive_chunk_text


def test_recursive_chunking():
    text = (
        "# Header 1\n\nParagraph 1 with many words.\n\n"
        "Paragraph 2 with many words.\n\n# Header 2\n\nAnother paragraph."
    )
    chunks = recursive_chunk_text(text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) > 1
    assert chunks[0]["text"].startswith("# Header 1")
    # verify overlap exists using tokens
    enc = tiktoken.get_encoding("cl100k_base")
    for i in range(1, len(chunks)):
        last_word = chunks[i - 1]["text"].split()[-1]
        assert chunks[i]["text"].startswith(last_word)


def test_hard_split_fallback():
    text = " ".join(["word"] * 200)
    chunks = recursive_chunk_text(text, chunk_size=20, chunk_overlap=0, separators=["###"])
    assert len(chunks) > 1
    assert all(ch["tokens_count"] <= 20 for ch in chunks)


def test_overlap_preservation():
    text = "First part.\n\nSecond part.\n\nThird part."
    chunks = recursive_chunk_text(text, chunk_size=30, chunk_overlap=5)
    enc = tiktoken.get_encoding("cl100k_base")
    for i in range(1, len(chunks)):
        prev_tokens = enc.encode(chunks[i - 1]["text"])
        curr_tokens = enc.encode(chunks[i]["text"])
        assert prev_tokens[-5:] == curr_tokens[:5]
