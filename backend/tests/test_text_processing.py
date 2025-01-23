import pytest
from app.utils.text_processing import preprocess_text
import spacy

@pytest.fixture(scope="module")
def nlp():
    """
    Fixture that loads the spaCy English language model.
    Returns a spaCy NLP object that can be used across multiple tests.
    """
    import spacy
    return spacy.load("en_core_web_sm")

def test_preprocess_text_basic(nlp):
    """
    Tests basic text preprocessing functionality.
    Verifies that the function converts text to lowercase and removes basic punctuation.
    """
    text = "Hello, world! This is a test."
    result = preprocess_text(text, nlp)
    assert result == "hello world this is a test"

def test_preprocess_text_multiple_spaces(nlp):
    """
    Tests handling of multiple consecutive spaces.
    Verifies that multiple spaces are normalized to single spaces.
    """
    text = "This   has   multiple    spaces."
    result = preprocess_text(text, nlp)
    assert result == "this has multiple spaces"

def test_preprocess_text_punctuation(nlp):
    """
    Tests removal of various punctuation marks.
    Verifies that different types of punctuation are properly removed while preserving words.
    """
    text = "Hello, world! This is a test. With? Multiple! Punctuation marks."
    result = preprocess_text(text, nlp)
    assert result == "hello world this is a test with multiple punctuation marks"

def test_preprocess_text_numbers(nlp):
    """
    Tests handling of numeric values in text.
    Verifies that numbers are preserved in the processed output.
    """
    text = "There are 123 apples and 456 oranges."
    result = preprocess_text(text, nlp)
    assert result == "there are 123 apples and 456 oranges"

def test_preprocess_text_special_characters(nlp):
    """
    Tests removal of special characters.
    Verifies that non-alphanumeric special characters are removed from the text.
    """
    text = "This has some special characters: @#$%^&*()_+"
    result = preprocess_text(text, nlp)
    assert result == "this has some special characters"

def test_preprocess_text_unicode(nlp):
    """
    Tests handling of unicode characters.
    Verifies that accented characters are converted to their basic ASCII equivalents.
    """
    text = "This has some unicode characters: é è ñ ü"
    result = preprocess_text(text, nlp)
    assert result == "this has some unicode characters e e n u"

def test_preprocess_text_empty(nlp):
    """
    Tests processing of empty string input.
    Verifies that empty strings remain empty after processing.
    """
    text = ""
    result = preprocess_text(text, nlp)
    assert result == ""

def test_preprocess_text_only_spaces(nlp):
    """
    Tests processing of strings containing only whitespace.
    Verifies that strings with only spaces are converted to empty strings.
    """
    text = "     "
    result = preprocess_text(text, nlp)
    assert result == ""

def test_preprocess_text_newlines(nlp):
    """
    Tests handling of different types of line breaks.
    Verifies that newlines and carriage returns are properly handled and normalized.
    """
    text = "This has\nnewlines\nand\rcarriage returns."
    result = preprocess_text(text, nlp)
    assert result == "this has newlines and carriage returns"
