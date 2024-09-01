import functions_framework
from google.cloud import storage

# Função disparada por um evento (Pub/Sub ou outro gatilho)
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    try:
        # Apenas cria uma mensagem de sucesso
        log_content = "Função executada com sucesso."

        # Printando o log
        print(log_content)

        # Salvando o log no GCS
        save_log_to_gcs(log_content)
        
    except Exception as e:
        print(f"Erro geral: {e}")

def save_log_to_gcs(content):
    # Configurações do bucket e nome do arquivo
    bucket_name = "bucket-raw-1526"
    destination_blob_name = "execucao_sucesso.txt"

    # Inicializando o cliente de storage
    storage_client = storage.Client(project="etlpontapontagcp")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Salvando o conteúdo no arquivo txt no GCS
    blob.upload_from_string(content)
    print(f"Arquivo {destination_blob_name} salvo no bucket {bucket_name}.")
