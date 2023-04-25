#####################################################
# CLIP - SEARCH ENGINE - FIFTYONE DATASETS & MODELS #
#####################################################


# - IMPORTS -

# -- General Libraries --
import itertools
import pinecone


# - FUNCTIONS - 

# -- Get PINECONE Indexes --
def getPineconeIndexes(PINECONE_KEY='', pineconeEnv=''):
    """Obtain the existing indexes from a Pinecone User Information.
    Args:
        PINECONE_KEY (str, optional): Represents the PINECONE private KEY. Defaults to None.
        pineconeEnv (str, optional): Represents the PINECONE Environment related to the KEY. Defaults to None.
    """   
    pinecone.init(api_key=PINECONE_KEY, environment=pineconeEnv)
    try:
        return pinecone.list_indexes()
    except:
        return False


# -- Create a PINECONE Index --
def createPineconeIndex(PINECONE_KEY='', PINECONE_ENV='', pineconeIndexName="clip-search-engine", p_dimension=512, p_metric="cosine", p_pod_type="p1"):
    """Create the Pinecone Index based on the users informations and Index Parameters.
    Args:
        PINECONE_KEY (str, optional): Represents the PINECONE private KEY. Defaults to ''.
        pineconeEnv (str, optional): Represents the PINECONE Environment related to the KEY. Defaults to ''.
        pineconeIndexName (str, optional): Represents the PINECONE Name given by the User. Defaults to "clip-search-engine".
        p_dimension (int, optional): Represents the Image Dimensions. Defaults to 512.
        p_metric (str, optional): Represents the Metric use for measuring similarity. Defaults to "cosine".
        p_pod_type (str, optional): Represents the Pod Type. Defaults to "p1".
    """    
    pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
    try:
        pinecone.create_index(name=pineconeIndexName, dimension=p_dimension, metric=p_metric, pod_type=p_pod_type)
        return True
    except pinecone.core.client.exceptions.ApiException as e:
        return e
    except Exception:
        return Exception

# -- Delete a PINECONE Index --
def deletePineconeIndex(PINECONE_KEY='', PINECONE_ENV='', pineconeIndexName="clip-search-engine"):
    """Delete the Pinecone Index based on the Index Name.
    Args:
        PINECONE_KEY (str, optional): Represents the PINECONE private KEY. Defaults to ''.
        pineconeEnv (str, optional): Represents the PINECONE Environment related to the KEY. Defaults to ''.
        pineconeIndexName (str, optional): Represents the PINECONE Name given by the User. Defaults to "clip-search-engine".
    """   
    pinecone.init(api_key=PINECONE_KEY, environment=PINECONE_ENV)
    try:
        pinecone.delete_index(pineconeIndexName)
        return True
    except pinecone.core.client.exceptions.ApiException as e:
        return e
    except Exception:
        return Exception

# -- Upsert Data into PINECONE --
def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size.
    Args:
        iterable (_type_): the Pinecone vector to be upserted.
        batch_size (int, optional): the size for a chunk. Defaults to 100.
    """    
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
        
def upsert_Data(pineconeIndex, dictData):
    """Upsert data into Pinecone Index.
    Args:
        pineconeIndex (_type_): Represents the Pinecone Index.
        dictData (_type_): Represents the Data to be upserted.
    """    
    # Generates (id, vector) pairs
    data_to_upsert = list(zip(dictData["IMAGE_PATH"], dictData["EMBEDDING"]))
    
    # Upsert data with 100 vectors per upsert request
    for ids_vectors_chunk in chunks(data_to_upsert, batch_size=100):
        pineconeIndex.upsert(ids_vectors_chunk)  # Assuming `index` defined elsewhere
    return True


# -- Query PINECONE from Text --
def queryPinecone(pineconeIndex, textVector, topK=10, include_values=False):
    """Output the top K results from a Pinecone Index based on text request.
    Args:
        pineconeIndex (_type_): Represents the Pinecone Index.
        textVector (_type_): Represents the vectorize Text.
        topK (int, optional): Represents the K results to output. Defaults to 10.
        include_values (bool, optional): Whether the results should include values information. Defaults to False.
    """    
    return pineconeIndex.query(vector=textVector, top_k=topK,  include_values=include_values)
