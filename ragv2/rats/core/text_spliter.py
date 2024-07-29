def find(text: str, start: int, end: int, tokens: list[str]):
    for token in tokens:
        index = text.find(token, start, end)
        if index != -1:
            end = index + 1
    return end

def split(text: str, chunk_length: int, overlap_length: int, stop_tokens: list[str]):
    current = 0
    while True:
        end = find(text, current + chunk_length, len(text), stop_tokens)
        yield text[current:end].strip()
        if end == len(text):
            break
        current = find(text, end - overlap_length, end, stop_tokens)


from pathlib import Path
text = Path('texte.txt').read_text()

for chunk in split(text, 512, 128, ['.']):
    print(chunk)
    print("-----")


from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
tokenizer = MistralTokenizer.from_model('open-mistral-7b')

import tiktoken
print(tiktoken.list_encoding_names())
encoder = tiktoken.get_encoding('o200k_base')
t = encoder.encode('deltacutter')
print(t)

from llama_index.core.evaluation import RelevancyEvaluator, ContextRelevancyEvaluator, CorrectnessEvaluator, FaithfulnessEvaluator