import argparse
import requests
import sys
import json


def parse_args():
    parser = argparse.ArgumentParser(description='Databricks setup: create external locations, volumes, and tables.')
    parser.add_argument('--storage-name', required=True, help='Azure Storage Account Name')
    parser.add_argument('--container-names', required=True, nargs='+', help='List of container names')
    parser.add_argument('--databricks-host', required=True, help='Databricks workspace host URL (e.g., https://adb-xxxx.x.azuredatabricks.net)')
    parser.add_argument('--client-id', required=True, help='Azure Service Principal Client ID')
    parser.add_argument('--client-secret', required=True, help='Azure Service Principal Client Secret')
    parser.add_argument('--tenant-id', required=True, help='Azure Tenant ID')
    return parser.parse_args()


def get_spn_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://management.azure.com/.default'
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to get SPN token: {response.text}")
        sys.exit(1)
    return response.json()['access_token']


def create_external_location(databricks_host, databricks_token, storage_name, container_name):
    url = f"{databricks_host}/api/2.1/unity-catalog/external-locations"
    payload = {
        "name": f"{storage_name}_{container_name}_location",
        "url": f"abfss://{container_name}@{storage_name}.dfs.core.windows.net/",
        "credential_name": f"{storage_name}_credential",
        "comment": "Created by automation script"
    }
    headers = {"Authorization": f"Bearer {databricks_token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in (200, 201):
        print(f"Failed to create external location for {container_name}: {response.text}")
    else:
        print(f"External location created for {container_name}")


def create_volume(databricks_host, databricks_token, storage_name, container_name):
    url = f"{databricks_host}/api/2.1/unity-catalog/volumes"
    payload = {
        "name": f"{storage_name}_{container_name}_volume",
        "catalog_name": "main",
        "schema_name": "default",
        "storage_location": f"abfss://{container_name}@{storage_name}.dfs.core.windows.net/"
    }
    headers = {"Authorization": f"Bearer {databricks_token}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in (200, 201):
        print(f"Failed to create volume for {container_name}: {response.text}")
    else:
        print(f"Volume created for {container_name}")


def create_table_structure(databricks_host, databricks_token, storage_name, container_name):
    print(f"[INFO] Table structure creation for {container_name} would be implemented here.")


def main():
    args = parse_args()
    spn_token = get_spn_token(args.tenant_id, args.client_id, args.client_secret)
    databricks_token = spn_token

    for container_name in args.container_names:
        create_external_location(args.databricks_host, databricks_token, args.storage_name, container_name)
        create_volume(args.databricks_host, databricks_token, args.storage_name, container_name)
        create_table_structure(args.databricks_host, databricks_token, args.storage_name, container_name)


if __name__ == "__main__":
    main() 