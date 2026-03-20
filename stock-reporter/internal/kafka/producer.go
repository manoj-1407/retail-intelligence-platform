// producer — wraps sarama SyncProducer with a simple Publish method.
//
// WHY SYNC PRODUCER HERE?
// This is a reporter service, not a high-throughput pipeline.
// We want to know immediately if a message failed to deliver.
// Async producer would need a separate error-reading goroutine and
// complicates the code for no benefit at 10-store scale.
//
// In a 10,000-store deployment, switch to AsyncProducer + error channel.

package kafka

import (
	"encoding/json"
	"log"
	"strings"

	"github.com/IBM/sarama"
	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/models"
)

type Producer struct {
	producer sarama.SyncProducer
	topic    string
}

func NewProducer(brokers string, topic string) (*Producer, error) {
	cfg := sarama.NewConfig()
	cfg.Producer.Return.Successes = true   // required for SyncProducer
	cfg.Producer.Return.Errors   = true
	cfg.Producer.RequiredAcks    = sarama.WaitForLocal   // leader ack only
	cfg.Producer.Compression     = sarama.CompressionSnappy

	brokerList := strings.Split(brokers, ",")
	p, err := sarama.NewSyncProducer(brokerList, cfg)
	if err != nil {
		return nil, err
	}

	log.Printf("[kafka] producer connected | brokers=%v topic=%s", brokerList, topic)
	return &Producer{producer: p, topic: topic}, nil
}

// Publish serialises a StockEvent and sends it to Kafka.
// Key = "store:{storeID}" — ensures all events for a store go to same partition.
// Same partition = ordered delivery per store.
func (p *Producer) Publish(event models.StockEvent) error {
	data, err := json.Marshal(event)
	if err != nil {
		return err
	}

	key := sarama.StringEncoder(
		"store:" + itoa(event.StoreID),
	)

	msg := &sarama.ProducerMessage{
		Topic: p.topic,
		Key:   key,
		Value: sarama.ByteEncoder(data),
	}

	partition, offset, err := p.producer.SendMessage(msg)
	if err != nil {
		return err
	}

	log.Printf("[kafka] published | store=%d product=%d severity=%s partition=%d offset=%d",
		event.StoreID, event.ProductID, event.Severity, partition, offset)
	return nil
}

func (p *Producer) Close() error {
	return p.producer.Close()
}

func itoa(n int) string {
	return strings.TrimSpace(strings.Replace(" "+string(rune('0'+n%10)), " ", "", 1))
}
