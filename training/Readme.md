# Fine-Tuning Qwen2.5-1.5B for Hinglish AI Research Paper Explanation

This repository contains the complete fine-tuning pipeline used to train a lightweight Large Language Model capable of explaining AI/ML research papers in simple Hinglish (Roman Hindi + English).

The objective of this project is to bridge the gap between complex research papers and students by creating a domain-specific assistant that explains technical concepts in an easy-to-understand conversational style.

---

# Project Pipeline

```text
Research Papers
       │
       ▼
Extract Abstracts / Content
       │
       ▼
Gemini API
(Dataset Generation)
       │
       ▼
Instruction Dataset
(~800 Samples)
       │
       ▼
Data Cleaning & Formatting
(ChatML Format)
       │
       ▼
QLoRA Fine-Tuning
(Unsloth + Transformers)
       │
       ▼
LoRA Adapter
       │
       ▼
Merge Weights
       │
       ▼
Fine-Tuned Qwen2.5 Model
```

---

# Dataset Creation

Instead of manually writing instruction-response pairs, the dataset was generated automatically from AI/ML research papers.

### Workflow

1. Download AI/ML research papers.
2. Extract abstracts and relevant sections.
3. Use the Gemini API to generate instruction-response pairs.
4. Review and clean the generated outputs.
5. Convert the dataset into ChatML format compatible with Qwen2.5.

### Example Dataset Sample

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful AI professor."
    },
    {
      "role": "user",
      "content": "Explain FlashAttention."
    },
    {
      "role": "assistant",
      "content": "FlashAttention ek optimization technique hai..."
    }
  ]
}
```

---

# Data Formatting

The processed dataset was converted into the ChatML format expected by Qwen models.

Each training sample consists of:

- System Prompt
- User Instruction
- Assistant Response

---

# Model Training

The model was fine-tuned using QLoRA with Unsloth for memory-efficient training.

### Training Details

| Component | Details |
|-----------|---------|
| **Base Model** | Qwen2.5-1.5B-Instruct |
| **Fine-tuning Method** | QLoRA (LoRA adapters with 4-bit quantization) |
| **Training Framework** | Unsloth + Hugging Face Transformers + TRL + PEFT |
| **Dataset Size** | ~800 Custom Instruction-Response Pairs |
| **Maximum Sequence Length** | 2048 Tokens |
| **Quantization** | 4-bit QLoRA |
| **Output** | LoRA Adapter |

---

# Model Merging

After fine-tuning, the LoRA adapter was merged with the base model to create a standalone model for inference.

```python
model.push_to_hub_merged(
    "username/model-name",
    tokenizer,
    save_method="merged_16bit",
)
```

The merged model can be used directly without requiring PEFT adapters during inference.

---

# Inference

The merged model can be loaded directly using Hugging Face Transformers.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("your-model")
model = AutoModelForCausalLM.from_pretrained("your-model")
```

---

# Technologies Used

- Python
- PyTorch
- Unsloth
- Hugging Face Transformers
- PEFT
- TRL
- Google Colab(T4 free gpu)
- Gemini API

---

