import functions_framework
from google.cloud import storage
from google.cloud import pubsub_v1
import io

# Função disparada por uma mudança em um bucket do GCS
@functions_framework.cloud_event
def hello_gcs(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]
    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    # Criando o conteúdo do log
    log_content = (
        f"Event ID: {event_id}\n"
        f"Event type: {event_type}\n"
        f"Bucket: {bucket}\n"
        f"File: {name}\n"
        f"Metageneration: {metageneration}\n"
        f"Created: {timeCreated}\n"
        f"Updated: {updated}\n"
    )

    # Printando o log
    print(log_content)

    # Salvando o log no GCS
    save_log_to_gcs(log_content)
    
    # Enviando mensagem ao Pub/Sub
    publish_message_to_pubsub(log_content)
    

def save_log_to_gcs(content):
    # Configurações do bucket e nome do arquivo
    bucket_name = "bucket-raw-1526"
    destination_blob_name = "teste.txt"

    # Inicializando o cliente de storage
    storage_client = storage.Client(project="etlpontapontagcp")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Salvando o conteúdo no arquivo txt no GCS
    blob.upload_from_string(content)
    print(f"Arquivo {destination_blob_name} salvo no bucket {bucket_name}.")


def publish_message_to_pubsub(message):
    # Configurações do Pub/Sub
    # TODO(developer)
    project_id = "etlpontapontagcp"
    topic_id = "monitoring-modify-landing"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    for n in range(1, 10):
        data_str = f"Message number {n}"
        # Data must be a bytestring
        data = data_str.encode("utf-8")
        # Add two attributes, origin and username, to the message
        future = publisher.publish(
            topic_path, data, origin="python-sample", username="gcp"
        )
        print(future.result())

    print(f"Published messages with custom attributes to {topic_path}.")