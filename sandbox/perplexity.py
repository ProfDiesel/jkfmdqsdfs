# https://huggingface.co/docs/transformers/perplexity
# https://huggingface.co/spaces/evaluate-measurement/perplexity/blob/main/perplexity.py
# https://medium.com/@shubhamsd100/understanding-perplexity-in-language-models-a-detailed-exploration-2108b6ab85af

# tokenizer.add_tokens()
# puis https://github.com/huggingface/notebooks/blob/main/examples/language_modeling.ipynb

# pip install bitsandbytes accelerate
# pip install --no-deps --force-reinstall 'https://github.com/bitsandbytes-foundation/bitsandbytes/releases/download/continuous-release_multi-backend-refactor/bitsandbytes-0.44.1.dev0-py3-none-manylinux_2_24_x86_64.whl'
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

MESSAGES = ["my delta cutter is down", "I can't send hedge orders", "to 1000000000000", "Where is the best pizza in town ?"]

DEVICE = 'cpu'
MAX_LENGTH = 20 # in model generation config

#quantization_config = BitsAndBytesConfig(load_in_4bit=True)
quantization_config = None
checkpoint = "HuggingFaceTB/SmolLM-135M"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint, quantization_config=quantization_config)

def tokenized(messages):
    for message in messages:
        encoddings = tokenizer(message, return_tensors="pt")
        yield encoddings.input_ids[:, -MAX_LENGTH + 1:].to(DEVICE)

def generate(inputs):
    outputs = model.generate(inputs)
    for output in outputs:
        print(tokenizer.decode(output))

ENCODINGS = list(tokenized(MESSAGES))
#generate(ENCODINGS[0])

def perplexity(base, next):
    with torch.no_grad():
        input_ids = torch.cat((base, next), 1)
        target_ids = input_ids.clone()
        target_ids[:, :-base.size(1)] = -100
        outputs = model(input_ids, labels=target_ids)
        print(outputs.loss)

perplexity(ENCODINGS[0], ENCODINGS[1])
perplexity(ENCODINGS[0], ENCODINGS[2])
perplexity(ENCODINGS[0], ENCODINGS[3])
    

# word_probabilities = [0.2, 0.15, 0.3, 0.1, 0.25]
# log_probabilities = np.log2(word_probabilities)
# average_negative_log_probability = -np.mean(log_probabilities)
# perplexity = 2 ** average_negative_log_probability
# 
# inputs = tokenizer(text, return_tensors="pt")
# outputs = model(**inputs, labels=inputs["input_ids"])