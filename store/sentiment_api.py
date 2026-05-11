import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.environ.get("HF_TOKEN")
MODEL_ID = "blanchefort/rubert-base-cased-sentiment"

client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)

def analyze_sentiment(text):
    if not text or not isinstance(text, str):
        return ('NEUTRAL', 0.5)
    try:
        text = text[:512]
        result = client.text_classification(text)
        print(f"Raw API result: {result}") 
        
        if isinstance(result, list) and len(result) > 0:
            first = result[0]
            label = first.label
            score = first.score
        elif isinstance(result, dict):
            label = result.get('label', 'NEUTRAL')
            score = result.get('score', 0.5)
        else:
            return ('NEUTRAL', 0.5)
        
        label_upper = label.upper()
        if 'POSITIVE' in label_upper or 'POS' in label_upper:
            sentiment = 'POSITIVE'
        elif 'NEGATIVE' in label_upper or 'NEG' in label_upper:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'
        
        return (sentiment, score)
    except Exception as e:
        print(f"Sentiment error: {e}")
        return ('NEUTRAL', 0.5)