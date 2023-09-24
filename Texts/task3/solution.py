import math
from typing import List, Iterable, Set, Tuple

import torch
from torch.nn.utils.rnn import pad_sequence
from transformers import BertTokenizerFast, BertForTokenClassification

pretrained_model_dir = "rubert-tiny2-2000-steps"

no_entity_category = 'NO_ENTITY'
category_id_mapping = {0: 'AGE', 1: 'AWARD', 2: 'CITY', 3: 'COUNTRY', 4: 'CRIME', 5: 'DATE', 6: 'DISEASE', 7: 'DISTRICT', 8: 'EVENT', 9: 'FACILITY', 10: 'FAMILY', 11: 'IDEOLOGY', 12: 'LANGUAGE', 13: 'LAW', 14: 'LOCATION', 15: 'MONEY', 16: 'NATIONALITY', 17: 'NO_ENTITY', 18: 'NUMBER', 19: 'ORDINAL', 20: 'ORGANIZATION', 21: 'PENALTY', 22: 'PERCENT', 23: 'PERSON', 24: 'PRODUCT', 25: 'PROFESSION', 26: 'RELIGION', 27: 'STATE_OR_PROVINCE', 28: 'TIME', 29: 'WORK_OF_ART'}
category_mapping = {'AGE': 0, 'AWARD': 1, 'CITY': 2, 'COUNTRY': 3, 'CRIME': 4, 'DATE': 5, 'DISEASE': 6, 'DISTRICT': 7, 'EVENT': 8, 'FACILITY': 9, 'FAMILY': 10, 'IDEOLOGY': 11, 'LANGUAGE': 12, 'LAW': 13, 'LOCATION': 14, 'MONEY': 15, 'NATIONALITY': 16, 'NO_ENTITY': 17, 'NUMBER': 18, 'ORDINAL': 19, 'ORGANIZATION': 20, 'PENALTY': 21, 'PERCENT': 22, 'PERSON': 23, 'PRODUCT': 24, 'PROFESSION': 25, 'RELIGION': 26, 'STATE_OR_PROVINCE': 27, 'TIME': 28, 'WORK_OF_ART': 29}
no_entity_category_id = list(category_id_mapping.keys())[list(category_id_mapping.values()).index(no_entity_category)]

tokenizer = BertTokenizerFast.from_pretrained(pretrained_model_dir)
model = BertForTokenClassification.from_pretrained(pretrained_model_dir, local_files_only=True)

class Solution:
    def predict(self, texts: List[str]) -> Iterable[Set[Tuple[int, int, str]]]:
        tokenized_texts = tokenizer(texts, return_offsets_mapping=True)

        start_offsets = []
        for offset_block in tokenized_texts.offset_mapping:
            start_offsets.append(torch.Tensor([offset[0] for offset in offset_block]))
        end_offsets = []
        for offset_block in tokenized_texts.offset_mapping:
            end_offsets.append(torch.Tensor([offset[1] for offset in offset_block]))

        padded_start_offset = pad_sequence(start_offsets, batch_first=True, padding_value=0).long()
        padded_end_offset = pad_sequence(end_offsets, batch_first=True, padding_value=0).long()
        tokenized_texts_tensors = [torch.Tensor(t) for t in tokenized_texts.input_ids]
        padded_input_ids = pad_sequence(tokenized_texts_tensors, batch_first=True, padding_value=0).long()

        max_len = 128
        output_ids_list = []
        for i in range(math.ceil(padded_input_ids.shape[1] / max_len)):
            batch = padded_input_ids[..., i * max_len: (i + 1) * max_len]
            output_ids_list.append(torch.argmax(model(batch).logits, dim=-1))
        padded_output_ids = torch.cat(output_ids_list, dim=1)

        output = []
        for i in range(len(padded_output_ids)):
            span_list = []
            cur_category = padded_output_ids[i][0]
            cur_start_offset = 0
            cur_end_offset = 0
            for j in range(len(start_offsets[i])):
                if cur_category != padded_output_ids[i][j] and (cur_end_offset != padded_start_offset[i][j] or cur_end_offset == 0):
                    if cur_category != no_entity_category_id:
                        if not (cur_start_offset == 0 and cur_end_offset == 0):
                            span_list.append((int(cur_start_offset), int(cur_end_offset), category_id_mapping[int(cur_category)]))
                    new_cur_category = padded_output_ids[i][j]
                    cur_category = new_cur_category if new_cur_category != 0 else no_entity_category_id
                    cur_start_offset = padded_start_offset[i][j]
                cur_end_offset = padded_end_offset[i][j]
            if cur_category != no_entity_category_id and not (cur_start_offset == 0 and cur_end_offset == 0):
                span_list.append((int(cur_start_offset), int(cur_end_offset), int(cur_category),
                                  category_id_mapping[int(cur_category)]))
            output.append(set(span_list))
        return output
