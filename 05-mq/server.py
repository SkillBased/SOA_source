#!/usr/bin/env python
import pika
from grabber import scan_from_to

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='wikilinks')

def callback(ch, method, properties, body):
    mid, orig, dest = str(body).split("|")
    mid, orig, dest = mid[2:], orig, dest[:-1]
    print(f" [x] Received request {mid}", flush=True)
    print(f" [x] Scanning from {orig} to {dest}", flush=True)
    dist = scan_from_to(orig, dest)
    print(f" [x] found a path of length {dist}")
    response = f"{mid}|{dist}"
    ch.basic_publish(exchange='', routing_key=properties.reply_to, body=response)

channel.basic_consume('wikilinks', callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()