# https://huggingface.co/blog/embedding-quantization
# https://sbert.net/docs/package_reference/quantization.html
# https://unum-cloud.github.io/usearch/sqlite/index.html#bit-vectors
from sentence_transformers.quantization import quantize_embeddings
embeddings = model.encode(["I am driving to the lake.", "It is a beautiful day."])
int8_embeddings = quantize_embeddings(
    embeddings,
    precision="int8",
    calibration_embeddings=calibration_embeddings,
)
