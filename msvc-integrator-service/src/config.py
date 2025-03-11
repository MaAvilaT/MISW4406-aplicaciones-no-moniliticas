import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()


class Config:
    # Aplicación
    PORT = int(os.environ.get('PORT', 8080))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

    # RabbitMQ
    RABBITMQ_HOST: str = os.environ.get('RABBITMQ_HOST', 'rabbitmq-service')
    RABBITMQ_PORT: int = int(os.environ.get('RABBITMQ_PORT', 5672))
    RABBITMQ_USER: str = os.environ.get('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD: str = os.environ.get('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_VHOST: str = os.environ.get('RABBITMQ_VHOST', '/')

    # Colas
    LAB_RESULT_QUEUE: str = os.environ.get('LAB_RESULT_QUEUE', 'MSVC_INTEGRATOR_process_lab_test_result')

    # Seguridad
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'development_secret_key')

    # Timeout de conexión
    CONNECTION_TIMEOUT: int = int(os.environ.get('CONNECTION_TIMEOUT', 30))

    AUTH_URL: str = os.environ.get('MSVC_AUTH_URL', 'localhost:9090')
