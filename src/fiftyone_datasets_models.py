#####################################################
# CLIP - SEARCH ENGINE - FIFTYONE DATASETS & MODELS #
#####################################################


# - IMPORTS -

# -- General Libraries --
import fiftyone.zoo as foz


# - FUNCTIONS - 

# -- FiftyOne Datasets --

# --- Get Zoo Datasets ---
def getZoo_datasets(tags="image", source=None):
    """Obtain the available datasets in the FiftyOne Dataset Zoo.
    Args:
        tags (str or list of str, optional): only include datasets that have the specific tag or list of tags (exemple: ["image", "detection]). Defaults to ["image"].
        source (str or list of str, optional): only include datasets available via the given source or list of sources [exemple: "torch"]. Defaults to None.
    """
    return foz.list_zoo_datasets(tags, source=source)  # List of available ZOO datasets based on tags and source    

# --- Load Zoo Dataset ---
def loadZoo_dataset(datasetName, datasetSplits=None, datasetPersistent=True):
    """Load the dataset based on the splits and among the available datasets in the FiftyOne Dataset Zoo.
    Args:
        datasetName (str): the name of the Fiftyone Dataset Zoo to load.
        datasetSplits (_type_, optional): the split or a list of splits to load based on the available split from the dataset. Defaults to None.
        datasetPersistent (boolean, optional): Whether the dataset persist in the database after a session is terminated. Defaults to True.
    """    
    if isinstance(datasetSplits, str):  # Turn string into list to satistify the load_zoo_dataset() function
        datasetSplits = [datasetSplits]
    try:
        datasetInf = foz.load_zoo_dataset(name=datasetName, splits=datasetSplits)
    except:
        try:
            datasetInf = foz.load_zoo_dataset(name=datasetName)
        except:
            print('Dataset not found in the Fiftyone Dataset Zoo.')
            return         
    datasetInf.persistent = datasetPersistent
    return datasetInf 


# -- FiftyOne Models --

# --- Get Zoo Models ---
def getZoo_models():
    """Obtain the available models in the FiftyOne Model Zoo."""  
    return foz.list_zoo_models()  # List of available ZOO models

# -- Load Zoo Model --
def loadZoo_model(modelName="clip-vit-base32-torch"):
    """Load the model based on the available models in the FiftyOne Model Zoo.
    Args:
        modelName (str, optional): the name of the Fiftyone Model Zoo to load. Defaults to "clip-vit-base32-torch".
    """    
    try:
        return foz.load_zoo_model(name=modelName)
    except:
        print('Model not found in the Fiftyone Model Zoo.')
        return


# -- Construct Data Information --
def constructDictInf(datasetInf):
    """Construct a dictionnary of ID, EMBEDDING and IMAGE_PATH from the loaded dataset content.
    Args:
        datasetInf (fiftyone.core.dataset.Dataset): Loaded dataset.
    """    
    # Using fiftyone we have the following FILEPATH SYNTAX > CustomPath/fiftyone/DatasetName/SplitName/data/ImageName
    IMAGE_PATH =  datasetInf.values("filepath")
    if 'coco-2017' in datasetInf.name: # Verify if the dataset is from COCO 2017 
        IMAGE_PATH = list(map(lambda Im_local_path : f"http://images.cocodataset.org/{Im_local_path.split('/')[-3].replace('validation', 'val')}2017/{Im_local_path.split('/')[-1]}", datasetInf.values("filepath")))
    return dict({
        "ID":  datasetInf.values("id"),
        "EMBEDDING": list(map(lambda embedding : embedding.tolist(), datasetInf.values("embedding"))),
        "IMAGE_PATH": IMAGE_PATH
    })