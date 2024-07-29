import asyncio
import random

from nnsight import LanguageModel

from sae_auto_interp.explainers import SimpleExplainer, ExplainerInput
from sae_auto_interp.clients import get_client, execute_model
from sae_auto_interp.utils import load_tokenized_data
from sae_auto_interp.features import FeatureRecord
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--layers", type=str, default="12,14")
args = argparser.parse_args()
layers = [int(layer) for layer in args.layers.split(",") if layer.isdigit()]


model = LanguageModel("meta-llama/Meta-Llama-3-8B", device_map="cpu", dispatch=True)
tokens = load_tokenized_data(model.tokenizer,dataset_split="train",seq_len=256)

raw_features_path = "raw_features_llama_v1"
random.seed(22)
split_top_200_20_all_20_explainer_inputs = []


for layer in layers:
    module_name = f".model.layers.{layer}"

    records = FeatureRecord.from_tensor(
        tokens,
        module_name,
        selected_features=list(range(0,500)),
        raw_dir = raw_features_path,
        min_examples=200,
        max_examples=10000
    )

    for record in records:

        examples = record.examples
        for example in examples:
            normalized_activations = (example.activations / record.max_activation)*10
            example.normalized_activations = normalized_activations.round()
        top_200 = examples[:200]
        random_20 = random.sample(examples, 20)
        random_top_200_20 = random.sample(top_200, 20)
        split_top_200_20_all_20 = random_top_200_20 + random_20

        
        split_top_200_20_all_20_explainer_inputs.append(ExplainerInput(
            train_examples=split_top_200_20_all_20,
            record=record
        ))
       



client = get_client("local", "casperhansen/llama-3-70b-instruct-awq", base_url="http://localhost:8001/v1")

explainer = SimpleExplainer(client, tokenizer=model.tokenizer,cot=False,logits=False,activations=True)
explainer_out_dir = "saved_explanations/llama_v1"

asyncio.run(
    execute_model(
        explainer, 
        split_top_200_20_all_20_explainer_inputs,
        output_dir=explainer_out_dir,
        record_time=True
    )
)