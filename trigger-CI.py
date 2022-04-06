import importlib.util
import azureml
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.pipeline.core import PublishedPipeline
from azureml.core import Workspace
import requests
