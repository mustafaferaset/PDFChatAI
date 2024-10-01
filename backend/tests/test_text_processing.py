import pytest
from app.utils.text_processing import preprocess_text
import spacy

@pytest.fixture(scope="module")
def nlp():
    import spacy
    return spacy.load("en_core_web_sm")

def test_preprocess_text_basic(nlp):
    text = "Hello, world! This is a test."
    result = preprocess_text(text, nlp)
    assert result == "hello world this is a test"

def test_preprocess_text_multiple_spaces(nlp):
    text = "This   has   multiple    spaces."
    result = preprocess_text(text, nlp)
    assert result == "this has multiple spaces"

def test_preprocess_text_punctuation(nlp):
    text = "Hello, world! This is a test. With? Multiple! Punctuation marks."
    result = preprocess_text(text, nlp)
    assert result == "hello world this is a test with multiple punctuation marks"

def test_preprocess_text_numbers(nlp):
    text = "There are 123 apples and 456 oranges."
    result = preprocess_text(text, nlp)
    assert result == "there are 123 apples and 456 oranges"

def test_preprocess_text_special_characters(nlp):
    text = "This has some special characters: @#$%^&*()_+"
    result = preprocess_text(text, nlp)
    assert result == "this has some special characters"

def test_preprocess_text_unicode(nlp):
    text = "This has some unicode characters: é è ñ ü"
    result = preprocess_text(text, nlp)
    assert result == "this has some unicode characters e e n u"

def test_preprocess_text_empty(nlp):
    text = ""
    result = preprocess_text(text, nlp)
    assert result == ""

def test_preprocess_text_only_spaces(nlp):
    text = "     "
    result = preprocess_text(text, nlp)
    assert result == ""


def test_preprocess_text_newlines(nlp):
    text = "This has\nnewlines\nand\rcarriage returns."
    result = preprocess_text(text, nlp)
    assert result == "this has newlines and carriage returns"
