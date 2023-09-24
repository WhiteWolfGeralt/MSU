import torch
from transformers import AutoTokenizer, AutoModelForPreTraining

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")

model = AutoModelForPreTraining.from_pretrained("cointegrated/rubert-tiny2")

if __name__ == '__main__':
    pass