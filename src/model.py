"""Loads Qwen2.5-Coder-1.5B-Instruct plus the LoRA adapter and generates commit messages."""
import contextlib

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from .prompt import build_messages, clean_output

BASE_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct"


class CommitMessageGenerator:
    def __init__(self, adapter_dir="adapter_v1", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=dtype).to(self.device)
        self.model = PeftModel.from_pretrained(base, adapter_dir)
        self.model.eval()

    def generate(self, diff, use_adapter=True):
        """Return a one-line commit message for a git diff.

        use_adapter=False switches the fine-tuning off, which gives the
        'prompted only' model used as a comparison in the report.
        """
        text = self.tokenizer.apply_chat_template(
            build_messages(diff), tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        adapter_ctx = contextlib.nullcontext() if use_adapter else self.model.disable_adapter()
        amp_ctx = (
            torch.autocast("cuda", dtype=torch.float16)
            if self.device == "cuda"
            else contextlib.nullcontext()
        )
        with torch.no_grad(), adapter_ctx, amp_ctx:
            output = self.model.generate(**inputs, max_new_tokens=40, do_sample=False)

        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        return clean_output(self.tokenizer.decode(new_tokens, skip_special_tokens=True))
