import json
import os
import time

from google.cloud import pubsub_v1


project_id = os.getenv("GCP_PROJECT_ID")
topic_id = os.getenv("PUB_SUB_TOPIC_ID")


def publish_message(publisher, topic_path, message):
    data = json.dumps(message).encode("utf-8")

    future = publisher.publish(topic_path, data)

    print(
        f"Published message: {message.get('id')} "
        f"Message ID: {future.result()}"
    )


def main():
    if not project_id or not topic_id:
        raise ValueError(
            "GCP_PROJECT_ID and PUB_SUB_TOPIC_ID "
            "environment variables must be set."
        )

    publisher = pubsub_v1.PublisherClient()

    topic_path = publisher.topic_path(
        project_id,
        topic_id
    )

    with open(
        "sample_texts.json",
        "r",
        encoding="utf-8"
    ) as file:
        messages = json.load(file)

    for message in messages:
        publish_message(
            publisher,
            topic_path,
            message
        )

        time.sleep(1)


if __name__ == "__main__":
    main()