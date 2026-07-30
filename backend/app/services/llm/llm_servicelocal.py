from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.config import settings

_model = None
_tokenizer = None


def _load_model() -> None:
    #Lazy_initialization
    global _model, _tokenizer
    

    if _model is None:
        
        _tokenizer = AutoTokenizer.from_pretrained(settings.HF_MODEL)
        
        _model = AutoModelForCausalLM.from_pretrained(
            settings.HF_MODEL,
            
            dtype=torch.float32,
        )
        
        _model.eval()


def generate_response(messages: list[dict]) -> str:
    """
    Generates a response from the locally hosted fine-tuned Qwen model.
    """
    try:
        _load_model()
        
        inputs = _tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(_model.device)
        
        with torch.inference_mode():
            outputs = _model.generate(
                **inputs,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P,
                do_sample=True,
                eos_token_id=_tokenizer.eos_token_id,
                pad_token_id=_tokenizer.eos_token_id,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]

        response = _tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        return response.strip()

    except Exception as e:
        raise RuntimeError(f"Local LLM inference failed: {e}")