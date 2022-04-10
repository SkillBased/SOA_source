Docker runs server side of the app, client has a console with two commands: "scan" to scan wiki and "exit" to end the process

Locally tested with docker image of rabbitMQ:
`docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management`

Known issues: slow execution; AMQP connection error occurs when testing docked version of server with docked rabbitMQ, but simply running server works fine
