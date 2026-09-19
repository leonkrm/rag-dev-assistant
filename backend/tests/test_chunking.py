from app.services.chunking import split_into_chunks


def test_short_text_returns_single_chunk():
    text = "короткий текст"
    chunks = split_into_chunks(text)
    assert chunks == [text]


def test_empty_text_returns_no_chunks():
    assert split_into_chunks("") == []
    assert split_into_chunks("   ") == []


def test_long_text_splits_with_overlap():
    text = "A" * 2000
    chunks = split_into_chunks(text)
    assert len(chunks) == 4
    assert len(chunks[0]) == 800
