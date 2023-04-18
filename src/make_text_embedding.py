######################
#                    #
######################



# Import LIBRARIES
import torch


# Define FUNCTIONS

# -- --
def get_text_embedding(inputString, Model):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.long
    tokenizer = Model._tokenizer

    # standard start-of-text & end-of-text token
    sot_token = tokenizer.encoder["<|startoftext|>"]
    eot_token = tokenizer.encoder["<|endoftext|>"]
    string_tokens = tokenizer.encode(inputString)
    all_tokens = [[sot_token] + string_tokens + [eot_token]]

    text_features = torch.zeros(len(all_tokens), Model.config.context_length, dtype=dtype, device=device,)
    text_features[0, : len(all_tokens[0])] = torch.tensor(all_tokens)
    embedding = Model._model.encode_text(text_features).to(device)
    return embedding.tolist() 
