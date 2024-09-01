import base64
import requests
import json
import os
from google.auth import default
from google.auth.transport.requests import Request
from datetime import datetime

# Configurações do Dataflow
DATAFLOW_API_URL = "https://dataflow.googleapis.com/v1b3/projects/{project_id}/locations/{region}/templates:launch"
PROJECT_ID = os.environ.get('PROJECT_ID')  # ID do seu projeto Google Cloud
REGION = os.environ.get('REGION')  # Região onde o template está armazenado
TEMPLATE_PATH = os.environ.get('TEMPLATE_PATH')  # Caminho do template no GCS

def get_access_token():
    """Gera um token de acesso para autenticação na API do Dataflow"""
    credentials, _ = default()
    credentials.refresh(Request())
    return credentials.token

def trigger_dataflow(event, context):
    """Função Cloud Function acionada por uma mensagem do Pub/Sub para iniciar um job no Dataflow"""
    
    # Decode the Pub/Sub message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    
    # Parse the message (opcional: usar informações da mensagem para personalizar o job)
    message_data = json.loads(pubsub_message)
    
    # Criar um nome de job único
    formatted_datetime = datetime.now().strftime("%Y-%m-%d--%H-%M")
    job_name = f"etl-dataflow-motors-word-{formatted_datetime}"
    
    # Construir o URL da API do Dataflow
    url = DATAFLOW_API_URL.format(project_id=PROJECT_ID, region=REGION)
    
    # Dados do job do Dataflow
    dataflow_payload = {
        "jobName": job_name,
        "gcsPath": TEMPLATE_PATH,
        "parameters": {
            "project": "motors-word-etl-process",
            "runner": "DataflowRunner",
            "streaming": "false",
            "job_name": job_name,
            "template_location": "gs://bkt-motors-word/templates/etl-dataflow-motors-word",
            "temp_location": "gs://bkt-motors-word/temp",
            "staging_location": "gs://bkt-motors-word/staging",
            "autoscaling_algorithm": "THROUGHPUT_BASED",
            "worker_machine_type": "n1-standard-4",
            "service_account_key_file": "./keys",
            "num_workers": "1",
            "max_num_workers": "3",
            "number_of_worker_harness_threads": "2",
            "disk_size_gb": "50",
            "region": "southamerica-east1",
            "zone": "southamerica-east1-c",
            "project_id": "motors-word-etl-process",
            "staging_bucket": "bkt-motors-word",
            "save_main_session": "false",
            "prebuild_sdk_container_engine": "cloud_build",
            "docker_registry_push_url": "southamerica-east1-docker.pkg.dev/motors-word-etl-process/etl-dataflow-motors-word/motors-dev",
            "sdk_container_image": "southamerica-east1-docker.pkg.dev/motors-word-etl-process/etl-dataflow-motors-word/motors-dev:latest",
            "sdk_location": "container",
            "requirements_file": "./requirements.txt",
            "metabase_file": "./metadata.json",
            "setup_file": "./setup.py",
            "service_account_email": "sa-motors-word-etl-process@motors-word-etl-process.iam.gserviceaccount.com"
        }
    }
    
    # Definir headers para a requisição
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
    
    # Fazer a requisição para iniciar o job no Dataflow
    try:
        response = requests.post(url, headers=headers, json=dataflow_payload)
        
        if response.status_code == 200:
            print(f"Job iniciado com sucesso no Dataflow. Resposta: {response.json()}")
        else:
            print(f"Falha ao iniciar o job. Status Code: {response.status_code}, Resposta: {response.text}")
    
    except Exception as e:
        print(f"Erro ao tentar iniciar o job no Dataflow: {str(e)}")
