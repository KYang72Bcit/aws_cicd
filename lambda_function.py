import json
import os
import psycopg2
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager", 
        region_name=region_name
        )
    
    try: 
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    else:
        return json.loads(response["SecretString"])

def lambda_handler(event, context):
    data = event

    if not isinstance(data, dict):
        if data:
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Invalid JSON input"})
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No data provided"})
            }
    secret_name = "rds!db-8523b0d9-9f6a-4efb-a68b-70f8a0d2959d"
    region_name = "us-east-2"
    secret = get_secret(secret_name, region_name)
    print("secret: ", secret)
        
    # db_host = secret['host']
    # db_port = secret['port']
    db_host = "test-db.ctouxquopdyk.us-east-2.rds.amazonaws.com"
    db_port = "5432"
    db_user = secret['username']
    db_password = secret['password']
    
    connection_string = f"host={db_host} port={db_port} user={db_user} password={db_password}"
    print("connection_string: ", connection_string)

    # try: 
    #     with psycopg2.connect(connection_string) as conn: 
    #         return {
    #             "statusCode": 200,
    #             "body": json.dumps({"message": "Successfully connected to the database"})
    #         }
    # except Exception as e:
    #     return {
    #         "statusCode": 500,
    #         "body": json.dumps({"message": f"Error connecting to the database: {str(e)}"})
    #     }
    
    try:
        with psycopg2.connect(connection_string) as conn:
            with conn.cursor() as cur:
                query = "INSERT INTO devices (device_id, device_name, device_description, status) VALUES (%s, %s, %s, %s)"
                cur.execute(query, (data['device_id'], data['device_name'], data['device_description'], data['status']))
            conn.commit()
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Successfully inserted a new device"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error inserting data: {str(e)}"})
        }
    
