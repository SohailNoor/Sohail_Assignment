import boto3

client = boto3.client('rds')
response = client.describe_db_instances(
    DBInstanceIdentifier='Sohail-db',
)

print(response)