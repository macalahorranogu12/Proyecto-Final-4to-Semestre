import boto3
import os
from datetime import timedelta

# Configuración S3
S3_BUCKET = "proyectomultimedia"
S3_REGION = "us-east-1"  # Ajustar según tu región
S3_PREFIX = "uploads/"

# Cliente S3
s3_client = boto3.client('s3', region_name=S3_REGION)


def generate_presigned_url(filename: str, content_type: str, expiration: int = 3600) -> dict:
    """
    Genera una presigned URL para subir un archivo a S3 (PUT).
    
    Args:
        filename: Nombre del archivo
        content_type: Tipo MIME del archivo
        expiration: Tiempo de expiración en segundos (default: 1 hora)
    
    Returns:
        dict con 'url' (presigned URL) y 'key' (clave S3)
    """
    # Generar clave única con prefijo uploads/
    key = f"{S3_PREFIX}{filename}"
    
    try:
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=expiration
        )
        return {
            'url': url,
            'key': key
        }
    except Exception as e:
        raise Exception(f"Error generando presigned URL: {str(e)}")


def generate_presigned_get_url(key: str, expiration: int = 3600) -> str:
    """
    Genera una presigned URL para obtener un archivo de S3 (GET).
    
    Args:
        key: Clave S3 del archivo
        expiration: Tiempo de expiración en segundos (default: 1 hora)
    
    Returns:
        Presigned URL para descargar el archivo
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': key
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        raise Exception(f"Error generando presigned GET URL: {str(e)}")
