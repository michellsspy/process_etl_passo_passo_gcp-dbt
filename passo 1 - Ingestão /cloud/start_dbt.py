import base64
import requests
import os
import json

# Configurações do DBT Cloud
DBT_CLOUD_API_BASE_URL = "https://cloud.getdbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/"
DBT_CLOUD_API_TOKEN = os.environ.get('DBT_CLOUD_API_TOKEN')  # Carregar o token de ambiente
ACCOUNT_ID = os.environ.get('ACCOUNT_ID')  # ID da sua conta no DBT Cloud
JOB_ID = os.environ.get('JOB_ID')  # ID do job que você quer acionar

def trigger_dbt(event, context):
    """Função Cloud Function acionada por uma mensagem do Pub/Sub para iniciar um job no DBT Cloud"""
    
    # Decode the Pub/Sub message
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    
    # Parse the message (opcional: usar informações da mensagem para personalizar o job)
    message_data = json.loads(pubsub_message)
    
    # Construir o URL da API
    url = DBT_CLOUD_API_BASE_URL.format(account_id=ACCOUNT_ID, job_id=JOB_ID)
    
    # Definir headers para a requisição
    headers = {
        "Authorization": f"Token {DBT_CLOUD_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Fazer a requisição para iniciar o job no DBT Cloud
    try:
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Job {JOB_ID} iniciado com sucesso no DBT Cloud.")
        else:
            print(f"Falha ao iniciar o job. Status Code: {response.status_code}, Resposta: {response.text}")
    
    except Exception as e:
        print(f"Erro ao tentar iniciar o job no DBT Cloud: {str(e)}")

