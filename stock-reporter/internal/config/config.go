// config — loads all configuration from environment variables.
// Centralised here so no other package imports os.Getenv directly.

package config

import (
	"os"
	"strconv"
)

type Config struct {
	KafkaBrokers    string
	KafkaTopic      string
	APIBaseURL      string
	APIToken        string
	StoreCount      int
	PollIntervalSec int
	Port            string
}

func Load() *Config {
	return &Config{
		KafkaBrokers:    getEnv("KAFKA_BROKERS", "localhost:9092"),
		KafkaTopic:      getEnv("KAFKA_TOPIC", "stock-updates"),
		APIBaseURL:      getEnv("API_BASE_URL", "http://localhost:8000"),
		APIToken:        getEnv("API_TOKEN", ""),
		StoreCount:      getEnvInt("STORE_COUNT", 10),
		PollIntervalSec: getEnvInt("POLL_INTERVAL_SEC", 30),
		Port:            getEnv("PORT", "8080"),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func getEnvInt(key string, fallback int) int {
	if v := os.Getenv(key); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return fallback
}
