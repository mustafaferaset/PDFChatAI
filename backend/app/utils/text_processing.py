import re
import unicodedata

def preprocess_text(text: str, nlp) -> str:
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Replace newlines and carriage returns with spaces
    text = re.sub(r'[\n\r]', ' ', text)
    
    # Remove special characters except apostrophes
    text = re.sub(r'[^\w\s\']', ' ', text)
    
    # Tokenize the text
    doc = nlp(text)
    
    # Process tokens: lowercase, keep numbers and important words
    tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    
    # Join tokens and remove extra whitespace
    processed_text = ' '.join(tokens)
    
    return processed_text