FROM python:3.11-slim
WORKDIR /app
# build context is the stage root: docker build -f src/Dockerfile -t tinywms-pick-ticket-worker .
COPY src/pick_ticket_worker.py /app/pick_ticket_worker.py
COPY src/sqs_consumer.py /app/sqs_consumer.py
COPY src/local_aws.py /app/local_aws.py
ENTRYPOINT ["python3", "/app/pick_ticket_worker.py"]
CMD ["pick-work-queue-url", "pick-tickets.txt", "--state-file", "pick-ticket-worker-state.json"]
