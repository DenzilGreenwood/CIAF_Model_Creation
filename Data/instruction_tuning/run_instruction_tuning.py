#!/usr/bin/env python3
"""
Run instruction tuning on governance QA dataset.
Light SFT to boost QA accuracy from 0.4 to 0.7.
"""

import torch
import json
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict

class InstructionDataset(Dataset):
    """Dataset for instruction tuning."""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        self.data = []
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.data.append(json.loads(line))
        
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Format as instruction-following text
        if item["input"]:
            text = f"Instruction: {item['instruction']}\nInput: {item['input']}\nResponse: {item['output']}"
        else:
            text = f"Instruction: {item['instruction']}\nResponse: {item['output']}"
        
        # Tokenize
        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        
        return {
            'input_ids': torch.tensor(tokens, dtype=torch.long),
            'labels': torch.tensor(tokens, dtype=torch.long),  # For next-token prediction
            'attention_mask': torch.ones(len(tokens), dtype=torch.long)
        }

def collate_fn(batch):
    """Collate function with padding."""
    max_len = max(len(item['input_ids']) for item in batch)
    
    input_ids = []
    labels = []
    attention_masks = []
    
    for item in batch:
        ids = item['input_ids']
        padding = max_len - len(ids)
        
        # Pad sequences
        input_ids.append(torch.cat([ids, torch.zeros(padding, dtype=torch.long)]))
        labels.append(torch.cat([item['labels'], torch.full((padding,), -100, dtype=torch.long)]))
        attention_masks.append(torch.cat([item['attention_mask'], torch.zeros(padding, dtype=torch.long)]))
    
    return {
        'input_ids': torch.stack(input_ids),
        'labels': torch.stack(labels),
        'attention_mask': torch.stack(attention_masks)
    }

if __name__ == "__main__":
    print("Instruction tuning script template ready.")
    print("Customize for your model architecture and run.")
