######################
#                    #
######################



# Import LIBRARIES
import os
import random
import fiftyone.zoo as foz


# Define FUNCTIONS

# -- --
def display_zoo_datasets(tags=None, source=None, display=False):
    """_summary_

    Args:
        tags (str or list of str, optional): only include datasets that have the specific tag or list of tags [exemple: "image"]. Defaults to None.
        source (str or list of str, optional): only include datasets available via the given source or list of sources [exemple: "torch"]. Defaults to None.
        display (boolean, optional): whether we want to display the avaible datasets or no. Default to False. 

    Returns:
        List: the available datasets in the FiftyOne Dataset Zoo. 
    """
        
    zoo_datasets = foz.list_zoo_datasets(tags, source=source)  # Get the list of available ZOO datasets
    if not display:
        return zoo_datasets
    
    ls_zoo_datasets = []
    for char_ in set(list(map(lambda avlb_data : avlb_data[0], zoo_datasets))): # Ascending Sort of the datasets 
        ls_zoo_datasets.append(list(filter(lambda avlb_data : avlb_data[0] == char_, zoo_datasets)))
    print("\n".join(list(map(lambda ls_data_per_char : " - ".join(list(map(lambda data_per_char : f'"{data_per_char}"', ls_data_per_char))), sorted(ls_zoo_datasets, key=lambda ele : ele[0][0], reverse=False)))))
    return zoo_datasets


# -- --
def display_zoo_models(display=False):
    """_summary_

    Args:
        display (boolean, optional): whether we want to display the avaible models or no. Default to False. 

    Returns:
        List: the available models in the FiftyOne Model Zoo. 
    """
        
    zoo_models = foz.list_zoo_models()  # Get the list of available ZOO models
    if not display:
        return zoo_models
    
    ls_zoo_models = []
    for char_ in set(list(map(lambda avlb_data : avlb_data[0], zoo_models))): # Ascending Sort of the models 
        ls_zoo_models.append(list(filter(lambda avlb_data : avlb_data[0] == char_, zoo_models)))
    print("\n".join(list(map(lambda ls_data_per_char : " - ".join(list(map(lambda data_per_char : f'"{data_per_char}"', ls_data_per_char))), sorted(ls_zoo_models, key=lambda ele : ele[0][0], reverse=False)))))
    return zoo_models


# -- --
def verifySplit(split=None):
    """_summary_

    Args:
        split (str, list of str): provide a supported split or list of splits. 

    Returns:
        list: a list of available split(s).
    """    
    
    availableSplits = ['train', 'test', 'validation']
    if isinstance(split, str):
        if split.lower() not in availableSplits:
            return None
        return [split]
    if isinstance(split, list):
        split = list(map(lambda splt_val : splt_val.lower(), split))
        lsSplits = list(filter(lambda splt_val : splt_val in availableSplits, split))
        if not lsSplits:
            return None
        return lsSplits 
    return None

  
    
    
    
# -- --
def load_zoo_dataset(datasetName=None, split=None):
    if (datasetName is None) or (datasetName not in display_zoo_datasets()):
        datasetName = random.choice(display_zoo_datasets())
    return foz.load_zoo_dataset(name=datasetName, splits=verifySplit(split))



# -- --
def load_zoo_model(modelName="clip-vit-base32-torch", displayInf=False):
    if (modelName is None) or (modelName not in display_zoo_models()):
        print('Select an Avaible Models among the following:\n')
        display_zoo_models(display=True)
        return None

    zoo_model = foz.load_zoo_model(name=modelName)
   
    if displayInf:
        print("***** Model description *****")
        print(zoo_model.description)

        print("\n***** Tags *****")
        print(zoo_model.tags)

        print("\n***** Requirements *****")
        print(zoo_model.requirements)
    
    print(f"Model Loaded: '{modelName}'")
    return zoo_model


# -- --
def construct_data_coco(datasetCoco, cocoDataYear, cocoSplit):
    coco_URL = "http://images.cocodataset.org"
    cocoSplitURLs = {
        'TRAIN': os.path.join(coco_URL, f'train{cocoDataYear}'),
        'TEST':  os.path.join(coco_URL, f'test{cocoDataYear}'),
        'VALIDATION':  os.path.join(coco_URL, f'val{cocoDataYear}'),
    }
    dictCoco = {
        "ID":  datasetCoco.values("id"),
        "EMBEDDING": list(map(lambda embedding : embedding.tolist(), datasetCoco.values("embedding"))),
        "IMAGE_URL": list(map(lambda Im_local_path : os.path.join(cocoSplitURLs[cocoSplit[0].upper()], Im_local_path.split("\\")[-1]).replace('\\', '/'), datasetCoco.values("filepath")))
    }
    return dictCoco


if __name__ == "__main__":
    dataset = load_zoo_dataset("coco-2017", "validation")   
    print()
    zoo_model = load_zoo_model()