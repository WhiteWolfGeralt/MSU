import codecs
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Set, Dict, Callable, Any, TypeVar, Optional, Tuple, Union, NamedTuple
from enum import Enum
import logging

import numpy as np
from sklearn.metrics import f1_score, recall_score, precision_score
from torch.utils.data import Dataset
from transformers import (
    EvalPrediction,
)
from transformers.tokenization_utils_base import EncodingFast
from torch import LongTensor, BoolTensor, Tensor
import torch
from torch.nn.utils.rnn import pad_sequence
from torch.nn.functional import pad


logger = logging.getLogger(__name__)

_Tensor = TypeVar('_Tensor', bound=Tensor)

context_length = 128

class DatasetType(str, Enum):
    TRAIN = 'train'
    DEV = 'dev'
    TEST = 'test'

@dataclass
class Example:
    text_id: int
    example_start: int
    input_ids: LongTensor  # shape: (LENGTH)
    start_offset: LongTensor
    end_offset: LongTensor
    target_label_ids: Optional[LongTensor]  # shape: (LENGTH, LENGTH)
    source_text: str


@dataclass
class BatchedExamples:
    text_ids: Tuple[int, ...]
    example_starts: Tuple[int, ...]
    input_ids: LongTensor  # shape: (BATCH_SIZE, LENGTH)
    start_offset: LongTensor
    end_offset: LongTensor
    padding_mask: BoolTensor  # shape: (BATCH_SIZE, LENGTH)


class TypedSpan(NamedTuple):
    start: int
    end: int
    type: str


def pad_images(images: List[_Tensor], *, padding_value: Any = 0.0, padding_length: Optional[int] = None) -> _Tensor:
    """Pad images to equal length (maximum height and width)."""
    max_height, max_width = padding_length, padding_length
    if padding_length is None:
        shapes = torch.tensor(list(map(lambda t: t.shape, images)), dtype=torch.long).transpose(0, 1)
        max_height, max_width = shapes[-2].max(), shapes[-1].max()

    ignore_dims = len(images[0].shape) - 2

    image_batch = [
        # The needed padding is the difference between the
        # max width/height and the image's actual width/height.
        pad(img, [*([0, 0] * ignore_dims), 0, max_width - img.shape[-1], 0, max_height - img.shape[-2]], value=padding_value)
        for img in images
    ]
    return torch.stack(image_batch)

def collect_categories(annotation_files: Iterable[Path]) -> Set[str]:
    all_annotations = list(map(read_annotation, annotation_files))

    all_categories: Set[str] = set()
    for document_annotations in all_annotations:
        all_categories.update(map(lambda span: span.type, document_annotations))

    return all_categories

def read_annotation(annotation_file: Path) -> Set[TypedSpan]:
    collected_annotations: Set[TypedSpan] = set()
    with codecs.open(annotation_file, 'r', 'utf-8') as f:
        for line in f:
            if line.startswith('T'):
                _, span_info, value = line.strip().split('\t')

                if ';' not in span_info:  # skip multispan
                    category, start, end = span_info.split(' ')
                    collected_annotations.add(TypedSpan(int(start), int(end), category))

    return collected_annotations

def read_text(text_file: Path) -> str:
    with codecs.open(text_file, 'r', 'utf-8') as f:
        return f.read()

_K = TypeVar('_K')
_V = TypeVar('_V')

def invert(d: Dict[_K, _V]) -> Dict[_V, _K]:
    return {v: k for k, v in d.items()}

def collate_examples(
        examples: Iterable[Example],
        *,
        padding_id: int = -100,
        pad_length: Optional[int] = None
) -> Dict[str, Union[BatchedExamples, Optional[LongTensor]]]:

    all_text_ids: List[int] = []
    all_example_starts: List[int] = []
    all_input_ids: List[LongTensor] = []
    all_padding_masks: List[BoolTensor] = []
    all_start_offsets: List[LongTensor] = []
    all_end_offsets: List[LongTensor] = []
    target_label_ids: Optional[List[LongTensor]] = None

    no_target_label_ids: Optional[bool] = None

    for example in examples:
        all_text_ids.append(example.text_id)
        all_example_starts.append(example.example_start)
        all_input_ids.append(example.input_ids)
        all_start_offsets.append(example.start_offset)
        all_end_offsets.append(example.end_offset)
        all_padding_masks.append(torch.ones_like(example.input_ids, dtype=torch.bool).bool())

        if no_target_label_ids is None:
            no_target_label_ids = (example.target_label_ids is None)
            if not no_target_label_ids:
                target_label_ids: List[LongTensor] = []

        if (example.target_label_ids is None) != no_target_label_ids:
            raise RuntimeError('Inconsistent examples at collate_examples!')

        if example.target_label_ids is not None:
            target_label_ids.append(example.target_label_ids)
    padded_input_ids = pad_sequence(all_input_ids, batch_first=True, padding_value=padding_id).long()
    padded_start_offsets = pad_sequence(all_start_offsets, batch_first=True, padding_value=0).long()
    padded_end_offsets = pad_sequence(all_end_offsets, batch_first=True, padding_value=-100).long()
    padded_padding_masks = pad_sequence(all_padding_masks, batch_first=True, padding_value=False).bool()

    padded_labels = pad_sequence(target_label_ids, batch_first=True, padding_value=-100).long() if not no_target_label_ids else None
    #padded_labels = pad_images(target_label_ids, padding_value=-100, padding_length=pad_length) if not no_target_label_ids else None

    return {
        'input_ids': padded_input_ids,
        'attention_mask': padded_padding_masks,
        #'position_ids': padded_start_offsets
        'labels': padded_labels
    }


def get_dataset_files(
        dataset_dir: Path,
        dataset_type: DatasetType,
        *,
        exclude_filenames: Set[str] = None
) -> Tuple[List[Path], List[Path]]:

    if exclude_filenames is None:
        exclude_filenames = set()

    dataset_dir = dataset_dir.joinpath(dataset_type.value)

    if not dataset_dir.exists():
        raise RuntimeError(f'Dataset directory {dataset_dir} does not exist!')

    if not dataset_dir.is_dir():
        raise RuntimeError(f'Provided path {dataset_dir} is not a directory!')

    def is_not_excluded(file: Path) -> bool:
        return file.with_suffix('').name not in exclude_filenames

    return sorted(filter(is_not_excluded, dataset_dir.glob('*.txt'))), sorted(filter(is_not_excluded, dataset_dir.glob('*.ann')))

def convert_to_examples(
        text_id: int,
        encoding: EncodingFast,
        category_mapping: Dict[str, int],
        no_entity_category: str,
        *,
        max_length: int = context_length,
        entities: Optional[Set[TypedSpan]] = None,
        source_str: str
) -> Iterable[Example]:
    """Encodes entities and splits encoded text into chunks."""

    sequence_length = len(encoding.ids)
    offset = torch.tensor(encoding.offsets, dtype=torch.long)

    target_label_ids: Optional[LongTensor] = None
    if entities is not None:
        token_start_mapping = {}
        token_end_mapping = {}
        for token_idx, (token_start, token_end) in enumerate(encoding.offsets):
            token_start_mapping[token_start] = token_idx
            token_end_mapping[token_end] = token_idx

        no_entity_category_id = category_mapping[no_entity_category]
        category_id_mapping = invert(category_mapping)

        text_length = len(encoding.ids)
        #target_label_ids = torch.full((text_length, text_length), fill_value=no_entity_category_id, dtype=torch.long).long()
        target_label_ids = torch.full((text_length, ), fill_value=no_entity_category_id, dtype=torch.long).long()
        for start, end, category in entities:
            try:
                token_start = token_start_mapping[start]
            except KeyError:
                if start + 1 in token_start_mapping:
                    logger.warning(f'changing {start} to {start + 1}')
                    token_start = token_start_mapping[start + 1]
                elif start - 1 in token_start_mapping:
                    logger.warning(f'changing {start} to {start - 1}')
                    token_start = token_start_mapping[start - 1]
                else:
                    logger.warning(f'Skipped entity {category} at ({start} {end})')
                    continue

            try:
                token_end = token_end_mapping[end]
            except KeyError:  # for some reason some ends are shifted by one
                if end + 1 in token_end_mapping:
                    logger.warning(f'changing {end} to {end + 1}')
                    token_end = token_end_mapping[end + 1]
                elif end - 1 in token_end_mapping:
                    logger.warning(f'changing {end} to {end - 1}')
                    token_end = token_end_mapping[end - 1]
                else:
                    logger.warning(f'Skipped entity {category} at ({start} {end})')
                    continue

            if target_label_ids[token_start] != no_entity_category_id:
            #if target_label_ids[token_start][token_end] != no_entity_category_id:
                #from_category = category_id_mapping[target_label_ids[token_start][token_end].item()]
                from_category = category_id_mapping[target_label_ids[token_start].item()]
                #logger.warning(f'Rewriting entity of category {from_category} with {category} at ({start} {end}) span')
                logger.warning(f'Nested entity of category {from_category} with {category} at ({start} {end}) span, ignored')
            else:
                for i in range(token_start, token_end + 1):
                    target_label_ids[i] = category_mapping[category]

            #target_label_ids[token_start][token_end] = category_mapping[category]

    # split encoding into max_length-token chunks

    chunk_start = 0
    while chunk_start < sequence_length:
        chunk_end = min(chunk_start + max_length, sequence_length)
        ex = Example(
            text_id,
            chunk_start,
            torch.tensor(encoding.ids[chunk_start:chunk_end], dtype=torch.long).long(),
            offset[chunk_start:chunk_end, 0],
            offset[chunk_start:chunk_end, 1],
            target_label_ids[chunk_start:chunk_end] if target_label_ids is not None else None,
            source_str
            #target_label_ids[chunk_start:chunk_end, chunk_start:chunk_end] if target_label_ids is not None else None
        )
        yield ex
        chunk_start = chunk_end

def read_nerel(
        dataset_dir: Path,
        dataset_type: DatasetType,
        tokenizer: Callable[[List[str]], List[EncodingFast]],
        category_mapping: Dict[str, int],
        no_entity_category: str,
        *,
        exclude_filenames: Set[str] = None
) -> Iterable[Example]:

    text_files, annotation_files = get_dataset_files(dataset_dir, dataset_type, exclude_filenames=exclude_filenames)

    all_annotations = list(map(read_annotation, annotation_files))
    all_texts = list(map(read_text, text_files))

    encodings = tokenizer(all_texts)
    for text_id, (encoding, entities, text) in enumerate(zip(encodings, all_annotations, all_texts)):
        yield from convert_to_examples(text_id, encoding, category_mapping, entities=entities, no_entity_category=no_entity_category, source_str=text)

@dataclass
class DatasetArguments:
    dataset_dir: Path = field(metadata={'help': 'NEREL dataset directory with train/dev/test subdirectories.'})


class NERDataset(Dataset[Example]):

    def __init__(self, examples: Iterable[Example]):
        self._examples = list(examples)

    def __getitem__(self, index) -> Example:
        return self._examples[index]

    def __len__(self):
        return len(self._examples)

def compute_metrics(
        evaluation_results: EvalPrediction,
        category_id_mapping: Dict[int, str],
        no_entity_category_id: int,
        short_output = False
) -> Dict[str, float]:

    predictions = np.argmax(evaluation_results.predictions, axis=-1)
    padding_mask = label_mask = (evaluation_results.label_ids != -100)

    #label_mask = np.triu(padding_mask)
    label_ids = evaluation_results.label_ids[label_mask]
    predictions = predictions[label_mask]

    unique_label_ids = set(np.unique(label_ids[label_ids != no_entity_category_id]))

    labels = sorted(category_id_mapping.keys())
    f1_category_scores = f1_score(label_ids, predictions, average=None, labels=labels, zero_division=0)
    recall_category_scores = recall_score(label_ids, predictions, average=None, labels=labels, zero_division=0)
    precision_category_scores = precision_score(label_ids, predictions, average=None, labels=labels, zero_division=0)

    results: Dict[str, float] = {}
    sum_f1 = 0
    sum_recall = 0
    sum_precision = 0
    for category_id, (f1, recall, precision) in enumerate(zip(f1_category_scores, recall_category_scores, precision_category_scores)):
        if category_id == no_entity_category_id:
            logger.info(f'O: {f1}, {recall}, {precision}')
            continue

        if category_id not in unique_label_ids:
            logger.info(f'Skipping {category_id_mapping[category_id]}: {f1}, {recall}, {precision}')

        category = category_id_mapping[category_id]
        if not short_output:
            results[f'F1_{category}'] = f1
            results[f'Recall_{category}'] = recall
            results[f'Precision_{category}'] = precision

        sum_f1 += f1
        sum_recall += recall
        sum_precision += precision

    num_categories = len(category_id_mapping) - 1

    results['F1_macro'] = sum_f1 / num_categories
    results['Recall_macro'] = sum_recall / num_categories
    results['Precision_macro'] = sum_precision / num_categories
    return results
