import json
import os
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
log = logging.getLogger("kafka-consumer")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "stock-updates"
GROUP_ID = "retail-inventory-consumer"
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() == "true"


def process_event(event: dict, db_conn=None) -> bool:
    """
    Process one stock-update event.
    Event shape: {"store_id": int, "product_id": int, "quantity": int}
    Returns True if processed successfully.
    """
    try:
        store_id   = int(event["store_id"])
        product_id = int(event["product_id"])
        quantity   = int(event["quantity"])

        if quantity < 0:
            log.warning("Skipping event with negative quantity: %s", event)
            return False

        if db_conn:
            cur = db_conn.cursor()
            cur.execute(
                """INSERT INTO inventory (product_id, store_id, quantity, updated_at)
                   VALUES (%s, %s, %s, NOW())
                   ON CONFLICT (product_id, store_id)
                   DO UPDATE SET quantity = EXCLUDED.quantity, updated_at = NOW()""",
                (product_id, store_id, quantity),
            )
            db_conn.commit()
            cur.close()

        log.info("Processed store=%d product=%d quantity=%d", store_id, product_id, quantity)
        return True
    except (KeyError, ValueError) as e:
        log.error("Malformed event %s: %s", event, e)
        return False
    except Exception as e:
        log.error("Error processing event %s: %s", event, e)
        if db_conn:
            db_conn.rollback()
        return False


def run_real_kafka():
    try:
        from kafka import KafkaConsumer
    except ImportError:
        log.error("kafka-python not installed — pip install kafka-python")
        sys.exit(1)

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=30000,
    )

    log.info("Listening to topic=%s group=%s", TOPIC, GROUP_ID)
    processed, failed = 0, 0

    for message in consumer:
        ok = process_event(message.value)
        if ok:
            consumer.commit()
            processed += 1
        else:
            failed += 1
        if (processed + failed) % 100 == 0:
            log.info("Stats: processed=%d failed=%d", processed, failed)


def run_simulation():
    log.info("Running in simulation mode (no Kafka broker required)")
    fake_events = [
        {"store_id": 1, "product_id": 1, "quantity": 45},
        {"store_id": 2, "product_id": 1, "quantity": 12},
        {"store_id": 3, "product_id": 2, "quantity": 0},
        {"store_id": 1, "product_id": 3, "quantity": 200},
        {"store_id": "bad", "product_id": 1, "quantity": -5},
    ]
    for event in fake_events:
        result = process_event(event)
        time.sleep(0.1)
    log.info("Simulation complete")


if __name__ == "__main__":
    if SIMULATION_MODE:
        run_simulation()
    else:
        run_real_kafka()
