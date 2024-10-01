import pytest
from app.utils.gemini_utils import TokenBucket
import time

@pytest.fixture
def token_bucket():
    return TokenBucket(tokens_per_minute=60, tokens_per_day=1000)

def test_token_bucket_initialization(token_bucket):
    assert token_bucket.tokens_per_minute == 60
    assert token_bucket.tokens_per_day == 1000
    assert token_bucket.tokens == 1000

def test_token_bucket_consume_success(token_bucket):
    assert token_bucket.consume(50) == True
    assert token_bucket.tokens == 950

def test_token_bucket_consume_failure(token_bucket):
    assert token_bucket.consume(1100) == False
    assert token_bucket.tokens == 1000

def test_token_bucket_refill():
    bucket = TokenBucket(tokens_per_minute=60, tokens_per_day=1000)
    bucket.consume(60)
    assert bucket.tokens == 940
    
    time.sleep(1)  # Wait for 1 second
    
    assert bucket.consume(1) == True
    assert 940 < bucket.tokens < 942  # Tokens should have slightly increased

def test_token_bucket_max_tokens():
    bucket = TokenBucket(tokens_per_minute=60, tokens_per_day=1000)
    time.sleep(2)  # Wait for 2 seconds
    
    assert bucket.tokens == 1000  # Tokens should not exceed the daily limit
