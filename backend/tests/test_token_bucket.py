import pytest
from app.utils.gemini_utils import TokenBucket
import time

@pytest.fixture
def token_bucket():
    # Create a reusable TokenBucket instance for testing
    # Rate limits: 60 tokens per minute, 1000 tokens per day
    return TokenBucket(tokens_per_minute=60, tokens_per_day=1000)

def test_token_bucket_initialization(token_bucket):
    # Verify that the TokenBucket is initialized with correct values
    # - Minute rate limit should be 60
    # - Daily rate limit should be 1000
    # - Initial token count should equal the daily limit
    assert token_bucket.tokens_per_minute == 60
    assert token_bucket.tokens_per_day == 1000
    assert token_bucket.tokens == 1000

def test_token_bucket_consume_success(token_bucket):
    # Test successful token consumption
    # - Consume 50 tokens (less than available)
    # - Verify remaining token count is reduced by 50
    assert token_bucket.consume(50) == True
    assert token_bucket.tokens == 950

def test_token_bucket_consume_failure(token_bucket):
    # Test token consumption failure when requesting more than available
    # - Attempt to consume 1100 tokens (more than daily limit)
    # - Verify consumption fails and token count remains unchanged
    assert token_bucket.consume(1100) == False
    assert token_bucket.tokens == 1000

def test_token_bucket_refill():
    # Test token refill mechanism
    bucket = TokenBucket(tokens_per_minute=60, tokens_per_day=1000)
    # Consume initial tokens
    bucket.consume(60)
    assert bucket.tokens == 940
    
    # Wait for refill to occur
    time.sleep(1)  # Wait for 1 second
    
    # Verify tokens have been refilled
    # - Should be able to consume 1 token
    # - Token count should have increased slightly due to refill
    assert bucket.consume(1) == True
    assert 940 < bucket.tokens < 942  # Tokens should have slightly increased

def test_token_bucket_max_tokens():
    # Test that tokens don't exceed the daily maximum
    bucket = TokenBucket(tokens_per_minute=60, tokens_per_day=1000)
    # Wait for potential refill
    time.sleep(2)  # Wait for 2 seconds
    
    # Verify tokens don't exceed daily limit even after waiting
    assert bucket.tokens == 1000  # Tokens should not exceed the daily limit
