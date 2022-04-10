#!/usr/bin/env python
import pika

usename = "user"
msg_cnt = 0

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

res = channel.queue_declare(queue='wikilinks')
callback_queue = res.method.queue

waiting = False
requests = {}

def exec_response(ch, method, properties, body):
    global waiting
    
    print(body)
    try:
        mid, dist = str(body).split("|")
        mid, dist = mid[2:], dist[:-1]
        print(f"got answer to {mid}")
        from_, to_ = requests[mid]
        print(f"{from_} and {to_}")
        print(f"are just {dist} away from each other", flush=True)
        waiting = False
    except Exception as e:
        print(e)

channel.basic_consume(queue=callback_queue, on_message_callback=exec_response, auto_ack=True)

command = ""
while (command != "exit"):

    if (command == "scan"):
        origin = input("Where to start from: ")
        destination = input("Where to stop: ")
        message_id = usename + "-" + str(msg_cnt)
        msg_cnt += 1
        request = f"{message_id}|{origin}|{destination}"
        requests[message_id] = [origin, destination]
        waiting = True
        channel.basic_publish(exchange='', routing_key='wikilinks', 
                              properties=pika.BasicProperties(reply_to = callback_queue,),
                              body=request)
        print("~/ # Sent request, awaiting answer")
        while waiting:
            connection.process_data_events()

    command = input("~/ ")

connection.close()