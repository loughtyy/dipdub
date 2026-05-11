from transformers import pipeline
import logging

logger = logging.getLogger(__name__)
_sentiment_pipeline = None

def get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        try:
            _sentiment_pipeline = pipeline(
                "text-classification",
                model="seara/rubert-tiny2-russian-sentiment",
                tokenizer="seara/rubert-tiny2-russian-sentiment",
                device=-1
            )
            logger.info("Анализатор тональности успешно загружен.")
        except Exception:
            logger.exception("Не удалось загрузить анализатор тональности!")
    return _sentiment_pipeline

def analyze_sentiment(text):
    pipe = get_sentiment_pipeline()
    if pipe is None:
        return ('error', 0.0)
    try:
        result = pipe(text[:512])[0]
        label_map = {'LABEL_0': 'NEGATIVE', 'LABEL_1': 'POSITIVE'}
        label = label_map.get(result['label'], result['label'])
        return (label, result['score'])
    except Exception:
        logger.exception("Ошибка анализа тональности")
        return ('error', 0.0)
