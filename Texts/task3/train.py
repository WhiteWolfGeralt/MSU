import logging
import codecs
from pathlib import Path
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import NamedTuple, Iterable, List, Set, Dict, Callable, Any, TypeVar, Optional, Tuple, Union
from enum import Enum

import numpy as np
from sklearn.metrics import f1_score, recall_score, precision_score
from torch.utils.data import Dataset
from torch.utils.tensorboard import SummaryWriter
from transformers import (
    Trainer,
    HfArgumentParser,
    TrainingArguments,
    EvalPrediction,
    BertTokenizerFast,
    BertModel,
    BertForTokenClassification
)
from transformers.integrations import TensorBoardCallback
from transformers.modeling_utils import unwrap_model
from transformers.tokenization_utils_base import EncodingFast
from torch import LongTensor, BoolTensor, Tensor
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.nn.functional import pad, one_hot, softmax

from utils import (
    get_dataset_files,
    collect_categories,
    invert,
    collate_examples,
    context_length,
    DatasetType,
    NERDataset,
    read_nerel,
    compute_metrics
)

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.get("labels")
        # forward pass
        outputs = model(**inputs)
        logits = outputs.get("logits")
        # compute custom loss (suppose one has 3 labels with different weights)
        loss_fct = torch.nn.MSELoss()
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


if __name__ == '__main__':
    model_type = "cointegrated/rubert-tiny2"
    dataset_dir = Path("D:\\Projects\\nlp\\task3\\data")
    no_entity_category = 'NO_ENTITY'
    batch_size = 128

    _, annotation_files = get_dataset_files(dataset_dir, DatasetType.TRAIN)
    categories = collect_categories(annotation_files)
    categories.add(no_entity_category)
    category_id_mapping = dict(enumerate(sorted(categories)))
    category_mapping = invert(category_id_mapping)
    no_entity_category_id = list(category_id_mapping.keys())[list(category_id_mapping.values()).index(no_entity_category)]

    tokenizer = BertTokenizerFast.from_pretrained(model_type)
    model = BertForTokenClassification.from_pretrained(model_type, num_labels=len(category_mapping.keys()))

    def tokenize(texts: List[str]) -> List[EncodingFast]:
        batch_encoding = tokenizer(texts, add_special_tokens=False, return_offsets_mapping=True, return_token_type_ids=False)
        return batch_encoding.encodings

    train_dataset = NERDataset(read_nerel(
        dataset_dir, DatasetType.TRAIN, tokenize, category_mapping, no_entity_category
    ))
    dev_dataset = NERDataset(read_nerel(
        dataset_dir, DatasetType.DEV, tokenize, category_mapping, no_entity_category
    ))

    training_args = TrainingArguments(
        output_dir="D:\\Projects\\nlp\\task3\\trained_model",
        learning_rate=0.8 * 1e-4,
        weight_decay=1e-5,
        #save_strategy="epoch",
        optim="adafactor",
        full_determinism=False,
        seed=42,
        #no_cuda=True,
        per_device_train_batch_size=batch_size,
        num_train_epochs=50,
        evaluation_strategy="steps",
        eval_steps=150,
    )

    pad_token_id = 0
    #model.load_state_dict(torch.load("trained_model/final_model_f1_77.pt"))
    #model = BertForTokenClassification.from_pretrained("trained_model/checkpoint-2000-f1_77", local_files_only=True)
    trainer = Trainer(
        model=model,
        args=training_args,
        #data_collator=partial(collate_examples, pad_length=context_length),
        data_collator=partial(collate_examples, padding_id=pad_token_id, pad_length=context_length),
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        compute_metrics=partial(
            compute_metrics,
            category_id_mapping=category_id_mapping,
            no_entity_category_id=no_entity_category_id,
            short_output=True
        ),
        callbacks=[TensorBoardCallback()]
    )
    trainer.train()

    # noinspection PyTypeChecker
    trained_model = unwrap_model(trainer.model_wrapped)
    #trained_model.cpu()
    torch.save(trained_model, Path(training_args.output_dir).joinpath("final_model.pt"))
    #trained_model.cuda()
    metrics = trainer.evaluate()


    def normalize(d: Dict[str, Any]) -> Dict[str, str]:
        return {k: str(v) for k, v in d.items()}

    print(metrics)
    print("eval_F1_macro:", metrics["eval_F1_macro"])
    print("eval_Recall_macro:", metrics["eval_Recall_macro"])
    print("eval_Precision_macro:", metrics["eval_Precision_macro"])
    tb_writer.add_hparams(hparam_dict={**normalize(training_args.__dict__)}, metric_dict=metrics)