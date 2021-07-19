#!/usr/bin/env python

# This file is part of pyipmeta.
#
# Copyright (C) 2017-2020 The Regents of the University of California.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
