from src.utils.chunking import chunk_markdown


def test_chunk_markdown():
    text = "Sentence. " * 60
    chunks = chunk_markdown(text, "test")
    assert len(chunks) > 1
    assert all(c["file_name"] == "test" for c in chunks)
