######################
#                    #
######################



# Import LIBRARIES
import sys, os
sys.path.append(os.path.dirname(__file__))
import itertools
import pinecone


# Define FUNCTIONS

# -- --
def display_existing_indexes(PINECONE_KEY="", pineconeEnv="us-central1-gcp", display=False):
    pinecone.init(api_key=PINECONE_KEY, environment=pineconeEnv)
    ls_pinecone_indexes = pinecone.list_indexes()
    if display:
        print("\n".join(ls_pinecone_indexes))
    return ls_pinecone_indexes


# -- --
def display_description_index(pineconeIndexName=None):
    if pineconeIndexName in display_existing_indexes():
        print(pinecone.describe_index("pinecone-index"))
    

# -- --
def create_pinecone_index(pineconeIndexName="clip-search-engine", p_dimension=512, p_metric="cosine", p_pod_type="p1"):
    if pineconeIndexName not in display_existing_indexes():
        pinecone.create_index(name=pineconeIndexName, dimension=p_dimension, metric=p_metric, pod_type=p_pod_type)
        print(f'Pinecone Index > {pineconeIndexName} created!')
        return True
    print(f'Pinecone Index > {pineconeIndexName} already exists!')
    
# -- --
def load_pinecone_index(pineconeIndexName):
    if pineconeIndexName in display_existing_indexes():
        return pinecone.Index(pineconeIndexName)


# -- --
def chunks(iterable, batch_size=100):
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))
        
# -- --
def upsert_Data_Coco(pineconeIndex, dictData):
    # Generates (id, vector) pairs
    data_to_upsert = list(zip(dictData["IMAGE_URL"], dictData["EMBEDDING"]))

    # Upsert data with 100 vectors per upsert request
    for ids_vectors_chunk in chunks(data_to_upsert, batch_size=100):
        pineconeIndex.upsert(ids_vectors_chunk)  # Assuming `index` defined elsewhere
        
    return pineconeIndex



# -- --
def query_pinecone(pineconeIndex, textVector, topK=10, include_values=False):
    return pineconeIndex.query(vector=textVector, top_k=topK,  include_values=include_values)



if __name__ == "__main__":
    index = "clip-search-engine"
    create_pinecone_index()