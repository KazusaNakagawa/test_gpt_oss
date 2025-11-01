from transformers import pipeline
import json
import torch



def chat(prompt: str):
    with open("./config/model.json", "r") as f:
        config = json.load(f)
    model_id = config["model_id"]

    messages = [
        {"role": "user", "content": prompt},
    ]
    pipe = pipeline(
        "text-generation",
        model=model_id,
        dtype="auto",
        device_map="auto",
    )

    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    return outputs[0]["generated_text"][-1]




# pipe = pipeline(
#     "text-generation",
#     model=model_id,
#     dtype="auto",
#     device_map="auto",
# )

# messages = [
#     {"role": config["role"], "content": config["content"]},
# ]

# outputs = pipe(
#     messages,
#     max_new_tokens=256,
# )
# print(outputs[0]["generated_text"][-1])
