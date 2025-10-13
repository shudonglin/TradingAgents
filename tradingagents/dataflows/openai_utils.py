"""
OpenAI API utilities with rate limiting and error handling.
"""
import time
import random
from typing import Any, Dict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import OpenAI, RateLimitError


class OpenAIRateLimitError(Exception):
    """Exception raised when OpenAI API rate limit is exceeded."""
    pass


@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    stop=stop_after_attempt(5),
)
def make_openai_request_with_retry(client: OpenAI, method_name: str, **kwargs) -> Any:
    """
    Make an OpenAI API request with retry logic for rate limiting.
    
    Args:
        client: OpenAI client instance
        method_name: The method to call (e.g., 'chat.completions.create', 'embeddings.create')
        **kwargs: Arguments to pass to the method
        
    Returns:
        API response
        
    Raises:
        OpenAIRateLimitError: When rate limit is exceeded after all retries
    """
    try:
        # Add small random delay to avoid thundering herd
        time.sleep(random.uniform(0.1, 0.5))
        
        # Get the method from the client
        method_parts = method_name.split('.')
        method = client
        for part in method_parts:
            method = getattr(method, part)
            
        # Make the API call
        response = method(**kwargs)
        return response
        
    except RateLimitError as e:
        print(f"OpenAI rate limit exceeded: {e}")
        raise OpenAIRateLimitError(f"OpenAI rate limit exceeded: {e}")


def safe_openai_call(client: OpenAI, method_name: str, fallback_value=None, **kwargs) -> Any:
    """
    Make an OpenAI API call with error handling and optional fallback.
    
    Args:
        client: OpenAI client instance
        method_name: The method to call
        fallback_value: Value to return if API call fails
        **kwargs: Arguments to pass to the method
        
    Returns:
        API response or fallback_value if call fails
    """
    try:
        return make_openai_request_with_retry(client, method_name, **kwargs)
    except OpenAIRateLimitError as e:
        print(f"OpenAI API rate limit exceeded, using fallback: {e}")
        return fallback_value
    except Exception as e:
        print(f"OpenAI API call failed, using fallback: {e}")
        return fallback_value
