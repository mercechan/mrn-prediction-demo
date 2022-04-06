import importlib.util
import azureml
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.pipeline.core import PublishedPipeline
from azureml.core import Workspace
import requests

auth = ServicePrincipalAuthentication(
    tenant_id = "a50f7df6-10c0-4855-af6d-9202f3cf0c65", 
    service_principal_id = "889d0b36-7868-4e58-8578-c62c8d49208c", 
    service_principal_password = "W8-7Q~mJ28GD4wPWAhkCVq7D_aei2sOWxyi7e", 
    cloud='AzureCloud', 
    _enable_caching=True)

aad_token = auth.get_authentication_header()
print(f'aad_token: {aad_token}')
