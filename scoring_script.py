import os
import logging
import json
import numpy
import joblib
import sklearn
import pandas as pd
import importlib.util

def init():
    """
    This function is called when the container is initialized/started, typically after create/update of the deployment.
    You can write the logic here to perform init operations like caching the model in memory
    """
    global model
    package_name = 'tokenwiser'
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f'Installing package: {package_name}')
        logging.info("Installing package: ",package_name)
        import os
        os.system(f"pip install tokenwiser")

    from tokenwiser.pipeline import make_partial_pipeline    
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder (./azureml-models/$MODEL_NAME/$VERSION)
    model_path = os.path.join(
        os.getenv("AZUREML_MODEL_DIR"), "mrn_multiNB_model.pkl"
    )
    # deserialize the model file back into a sklearn model
    model = joblib.load(model_path)
    logging.info("Init complete")


def run(raw_data):
    """
    This function is called for every invocation of the endpoint to perform the actual scoring/prediction.
    In the example we extract the data from the json input and call the scikit-learn model's predict()
    method and return the result back
    """
    logging.info("Request received")
    logging.info("Printing out raw data: ",raw_data)
    data = json.loads(raw_data)

    is_strict_mode = data["strict"]
    logging.info("is_strict_mode has value of: ",is_strict_mode)
    dataframe1 = pd.DataFrame.from_dict(data["members"])
    logging.info("dataframe1 has shape of: ",dataframe1.shape)
    logging.info("printing the first 5 rows of data:")
    logging.info(dataframe1.head(5))

    dataframe1.columns= dataframe1.columns.str.upper()

    # build full_name column
    dataframe1['FULL_NAME'] = dataframe1['FIRST_NAME'].fillna('').str.cat(dataframe1['MIDDLE_NAME'].fillna(''), sep=' ').str.cat(dataframe1['LAST_NAME'].fillna(''), sep=' ').str.cat(dataframe1['SUFFIX'].fillna(''), sep=' ').str.replace('  ',' ')
    # deduplicate
    dataframe1.drop_duplicates(subset=['FULL_NAME', 'BIRTH_DATE_TEXT', 'HOME_PHONE','ADDRESS_LINE1'], keep='last', inplace=True)
    logging.info("dataframe1 shape after de-dup: ")
    logging.info(dataframe1.shape)
    dataframe1['CONTENT'] = dataframe1['FULL_NAME'].str.cat(dataframe1['BIRTH_DATE_TEXT'].fillna(''), sep=' ').str.cat(dataframe1['HOME_PHONE'].astype(str), sep=' ').str.cat(dataframe1['ADDRESS_LINE1'].fillna(''), sep=' ').str.replace('  ',' ')
    X_test = dataframe1['CONTENT'].values

    logging.info("After extracting CONTENT into array:")
    logging.info(X_test)

    tmpl = (map(lambda x: x.lower(), X_test))
    example = list(tmpl)
    logging.info("After converting all to lower case data:")
    logging.info(example)  

    if is_strict_mode:
        logging.info("executing with is_strict_mode is true")
        proba_to_filter =  0.01
    else:
        logging.info("executing with is_strict_mode is false")
        proba_to_filter = 0.0008

    model_probas = model.predict_proba(example)
    test_num = len(model_probas)
    logging.info("number of predictions returned by model: ",test_num)

    predictions = []
    for i in range(0, test_num):
        counter = 0
        for x in model.classes_:
            proba  = round(model_probas[i][counter],5)            
            if proba > proba_to_filter:
                pred={}
                pred["member data"] = X_test[i]
                pred["mrn"] = x
                pred["probability"] = str(proba)
                predictions.append(pred)
                msg = "For test data {}, {}'s probability is: {}".format(X_test[i], x, str(proba))
                logging.info(msg)
            counter +=1

    logging.info("Request processed")
    result = json.dumps(predictions, indent=4)
    logging.info("jsonified result:")
    logging.info(result)
    return result

