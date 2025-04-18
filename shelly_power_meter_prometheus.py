#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pika>=1.3",
#   "requests>=2",
#   "prometheus-client>=0.21",
# ]
# ///

import json
import logging
import pika
from prometheus_client import start_http_server, Gauge

# Update with your power meter ID
POWER_METER_ID = '08f9e0e957c8'

# The port to host the Prometheus server on
PROMETHEUS_PORT = 8000

# The MQTT exchange to connect to
MQTT_EXCHANGE_HOST='192.168.88.64'
# The exchange name to connect to.
# We use RabbitMQ as the broker, in which case this is a Topic exchange.
MQTT_EXCHANGE_NAME='shack.mqtt'

# The log level
LOG_LEVEL = logging.INFO

# MQTT topics for the energy meter.
POWER_METER_MQTT_TOPIC = f'shellypro3em-{POWER_METER_ID}'
POWER_METER_MQTT_TOPIC_STATUS_EM = f'{POWER_METER_MQTT_TOPIC}.status.em:0'
POWER_METER_MQTT_TOPIC_STATUS_EMDATA = f'{POWER_METER_MQTT_TOPIC}.status.emdata:0'

CURRENT = Gauge('energy_meter_current',
                'Momentary current in A by phase, or total for all phases',
                ['phase'])
VOLTAGE = Gauge('energy_meter_voltage', 'Momentary voltage in V by phase',
                ['phase'])
ACTIVE_POWER = Gauge('energy_meter_active_power',
                     'Momentary active power in W by phase, or total for all phases',
                     ['phase'])
APPARENT_POWER = Gauge('energy_meter_apparent_power',
                       'Momentary apparent power in W by phase, or total for all phases',
                       ['phase'])
PF = Gauge('energy_meter_pf', 'Momentary power factor by phase', ['phase'])
FREQ = Gauge('energy_meter_freq', 'Momentary freq in Hz by phase', ['phase'])
TOTAL_ACTIVE_ENERGY = Gauge('energy_meter_total_active_energy',
                            'Total active energy in Wh by phase, or total for all phases',
                            ['phase'])
TOTAL_ACTIVE_ENERGY_RETURNED = Gauge(
    'energy_meter_total_active_energy_returned',
    'Total active energy returned in Wh by phase, or total for all phases',
    ['phase'])

logging.basicConfig(level=LOG_LEVEL)

logging.info("listening for EM events on routing key %s",POWER_METER_MQTT_TOPIC_STATUS_EM)
logging.info("listening for EMData events on routing key %s",POWER_METER_MQTT_TOPIC_STATUS_EMDATA)
logging.info("starting Prometheus server on %d",PROMETHEUS_PORT)
logging.info("using MQTT exchange on %s",MQTT_EXCHANGE_HOST)

start_http_server(PROMETHEUS_PORT)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=MQTT_EXCHANGE_HOST))

channel = connection.channel()
channel.exchange_declare(exchange=MQTT_EXCHANGE_NAME, exchange_type='topic')
result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=MQTT_EXCHANGE_NAME, queue=queue_name, routing_key="#")

def handle_em(body):
    # {
    #     "id": 0,
    #     "a_current": 1.141,
    #     "a_voltage": 229,
    #     "a_act_power": 195.9,
    #     "a_aprt_power": 261.8,
    #     "a_pf": 0.75,
    #     "a_freq": 50,
    #     "b_current": 0.945,
    #     "b_voltage": 228.7,
    #     "b_act_power": 144.5,
    #     "b_aprt_power": 216.5,
    #     "b_pf": 0.67,
    #     "b_freq": 50,
    #     "c_current": 0.106,
    #     "c_voltage": 228.7,
    #     "c_act_power": 15.8,
    #     "c_aprt_power": 24.2,
    #     "c_pf": 0.66,
    #     "c_freq": 50,
    #     "n_current": null,
    #     "total_current": 2.192,
    #     "total_act_power": 356.235,
    #     "total_aprt_power": 502.525,
    #     "user_calibrated_phase": []
    # }
    CURRENT.labels("A").set(body['a_current'])
    CURRENT.labels("B").set(body['b_current'])
    CURRENT.labels("C").set(body['c_current'])
    CURRENT.labels("total").set(body['total_current'])
    VOLTAGE.labels("A").set(body['a_voltage'])
    VOLTAGE.labels("B").set(body['b_voltage'])
    VOLTAGE.labels("C").set(body['c_voltage'])
    ACTIVE_POWER.labels("A").set(body['a_act_power'])
    ACTIVE_POWER.labels("B").set(body['b_act_power'])
    ACTIVE_POWER.labels("C").set(body['c_act_power'])
    ACTIVE_POWER.labels("total").set(body['total_act_power'])
    APPARENT_POWER.labels("A").set(body['a_aprt_power'])
    APPARENT_POWER.labels("B").set(body['b_aprt_power'])
    APPARENT_POWER.labels("C").set(body['c_aprt_power'])
    APPARENT_POWER.labels("total").set(body['total_aprt_power'])
    PF.labels("A").set(body['a_pf'])
    PF.labels("B").set(body['b_pf'])
    PF.labels("C").set(body['c_pf'])
    FREQ.labels("A").set(body['a_freq'])
    FREQ.labels("B").set(body['b_freq'])
    FREQ.labels("C").set(body['c_freq'])

def handle_emdata(body):
    # {
    #     "id": 0,
    #     "a_total_act_energy": 81574.47,
    #     "a_total_act_ret_energy": 0,
    #     "b_total_act_energy": 8784.89,
    #     "b_total_act_ret_energy": 0,
    #     "c_total_act_energy": 6557.2,
    #     "c_total_act_ret_energy": 0,
    #     "total_act": 96916.55,
    #     "total_act_ret": 0
    # }
    TOTAL_ACTIVE_ENERGY.labels("A").set(body['a_total_act_energy'])
    TOTAL_ACTIVE_ENERGY.labels("B").set(body['b_total_act_energy'])
    TOTAL_ACTIVE_ENERGY.labels("C").set(body['c_total_act_energy'])
    TOTAL_ACTIVE_ENERGY.labels("total").set(body['total_act'])
    TOTAL_ACTIVE_ENERGY_RETURNED.labels("A").set(body['a_total_act_ret_energy'])
    TOTAL_ACTIVE_ENERGY_RETURNED.labels("B").set(body['b_total_act_ret_energy'])
    TOTAL_ACTIVE_ENERGY_RETURNED.labels("C").set(body['c_total_act_ret_energy'])
    TOTAL_ACTIVE_ENERGY_RETURNED.labels("total").set(body['total_act_ret'])

def callback(ch, method, properties, body):
    logging.debug(f" [{method.exchange}] {method.routing_key}: %r", body)
    if method.routing_key == POWER_METER_MQTT_TOPIC_STATUS_EM:
        json_body = json.loads(body)
        logging.debug("received EM: %s",json.dumps(json_body))
        handle_em(json_body)
    elif method.routing_key == POWER_METER_MQTT_TOPIC_STATUS_EMDATA:
        json_body = json.loads(body)
        logging.debug("received EMData: %s",json.dumps(json_body))
        handle_emdata(json_body)

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
