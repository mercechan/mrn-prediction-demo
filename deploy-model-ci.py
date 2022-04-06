from azureml.core.model import InferenceConfig
from azureml.core.environment import Environment, CondaDependencies
from azureml.core.webservice import AciWebservice


# TODO: load registered model from azure registry

env = Environment.from_pip_requirements(name="mrnruntime_env", file_path='./requirements.txt')
env.register(workspace=ws)

inference_config = InferenceConfig(environment=env, source_directory='.', entry_script='./scoring_script.py')

deployment_config = AciWebservice.deploy_configuration(
    cpu_cores=1, memory_gb=1, auth_enabled=True
)

service = Model.deploy(
    ws,
    "myservice",
    [model],
    inference_config,
    deployment_config,
    overwrite=True,
)
service.wait_for_deployment(show_output=True)
