# Shelly Energy Meter MQTT to Prometheus

Translates Shelly Energy Monitor MQTT messages to Prometheus metrics.
Specifically, this was built for a Shelly Pro3 EM three-phase energy meter.
We don't measure N in our setup, but this can be added easily.

## Configuration

At the top of the script, adjust these constants for your setup:
```python
# Update with your power meter ID
POWER_METER_ID = '08f9e0e957c8'

# The port to host the Prometheus server on
PROMETHEUS_PORT = 8000

# The MQTT exchange to connect to
MQTT_EXCHANGE_HOST='192.168.12.34'
# The exchange name to connect to.
# We use RabbitMQ as the broker, in which case this is a Topic exchange.
MQTT_EXCHANGE_NAME='some.exchange'

# The log level
LOG_LEVEL = logging.INFO

# MQTT topics for the energy meter.
POWER_METER_MQTT_TOPIC = f'shellypro3em-{POWER_METER_ID}'
POWER_METER_MQTT_TOPIC_STATUS_EM = f'{POWER_METER_MQTT_TOPIC}.status.em:0'
POWER_METER_MQTT_TOPIC_STATUS_EMDATA = f'{POWER_METER_MQTT_TOPIC}.status.emdata:0'
```

## Running

This uses PEP 723 for dependency specification in the Python script.
You can use `uv` to run it:
```bash
uv run --script shelly_power_meter_prometheus.py
```