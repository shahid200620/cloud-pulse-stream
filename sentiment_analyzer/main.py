import base64
import json
import logging

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    if not isinstance(text, str):
        raise ValueError("Input must be a string.")

    text = text.strip()

    if not text:
        raise ValueError("Input text cannot be empty.")

    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "POSITIVE"
    elif compound <= -0.05:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"

    return {
        "text": text,
        "sentiment_label": label,
        "sentiment_score": compound
    }


def process_pubsub_message(event, context):
    if "data" not in event:
        logger.error("No data found in Pub/Sub message.")
        return

    try:
        message_data = base64.b64decode(event["data"]).decode("utf-8")
        payload = json.loads(message_data)

        text = payload.get("text")

        if not text:
            logger.warning(
                "Missing text field. Event ID: %s",
                context.event_id
            )
            return

        result = analyze_sentiment(text)

        logger.info(
            json.dumps(
                {
                    "text": result["text"],
                    "sentiment_label": result["sentiment_label"],
                    "sentiment_score": result["sentiment_score"]
                }
            )
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON payload received.")

    except ValueError as exc:
        logger.error("Validation error: %s", str(exc))

    except Exception as exc:
        logger.error(
            "Unexpected error: %s Event ID: %s",
            str(exc),
            context.event_id
        )