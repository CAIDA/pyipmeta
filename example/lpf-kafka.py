#!/usr/bin/env python
"""
Trivial sample code for writing InfluxDB LPF-formatted data into the hicube time series platform.

This code will not work as-is (i.e., you need a kafka topic created), but should serve as a starting point for writing
producers.

See https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_tutorial/ for information about LPF.
"""

import confluent_kafka

KAFKA_TOPIC = "telegraf-production.changeme"
KAFKA_BROKERS = "kafka.rogues.caida.org:9092"

kp = confluent_kafka.Producer({"bootstrap.servers": KAFKA_BROKERS,})

# send some time series data in LPF
kp.produce(KAFKA_TOPIC, "weather,location=us-midwest temperature=82 1465839830100400200")
# NB: in production you will likely want to batch these up and send many newline-separated points
# in each kafka message, like this:
kp.produce(KAFKA_TOPIC, "weather,location=us-midwest temperature=82 1465839830100400200\n"
                        "weather,location=us-midwest temperature=83 1465839830200400200\n"
                        "weather,location=us-midwest temperature=84 1465839830300400200\n"
                        "weather,location=us-midwest temperature=85 1465839830400400200\n")

# ensure all pending messages are written
kp.flush(10)