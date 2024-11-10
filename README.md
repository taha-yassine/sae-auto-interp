# Purpose of this branch

This branch accompanies our blogpost ("Generating text using natural language to simulate model's activations")[]

It contains stripped/modified versions of fuzzing and simulation code in the [nl_simulation/lib](nl_simulation/lib) folder. 

Code to generate the finetunning data and train the finetuned 8b model can be found in [nl_simulation/finetuning](nl_simulation/finetuning) folder. It assumes you have downloaded the [explanations](https://huggingface.co/datasets/EleutherAI/auto_interp_explanations/blob/main/Gemma/131k/res/model.layers.11_feature.json) and have the [cached activations]() 
It can be run with the following commands:
```
python make_data.py --explanation quantiles --top_k 5
python make_data.py --explanation top --top_k -1 --layer_train 11 --layer_test 11

python train.py --dataset quantiles_top5
```

Code to generate the data used in the interactive demo can be found in [nl_simulation/interactive](nl_simulation/interactive) folder.

The script to compute how many latents are correctly identified by the explanations can be found in [simulation_active.py](nl_simulation/interactive/simulation_active.py). It was run with the following commands:
```

python simulation_active.py --model_size 8b --explanation top --window_size 32 --num_sentences 2000 --start_sentence 0 
python simulation_active.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 
python simulation_active.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 --score fuzz 
python simulation_active.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 --score recall 
python simulation_active.py --model_size 8b-top_top5 --explanation top --window_size 32 --num_sentences 2000 --start_sentence 0 
python simulation_active.py --model_size 70b --explanation quantiles --window_size 32 --num_sentences 1000 --start_sentence 0 

```

Some of these comands assume you have finetuned the 8b model, and have access to the [scores](https://huggingface.co/datasets/EleutherAI/auto_interp_explanations/tree/main/scores/gemma/131k/res) of layer 11.


The script to compute the kl divergence if we "cheat" and only care if explanations can correctly identify active latents is in [kl_div_help.py](nl_simulation/interactive/kl_div_help.py). It was run with the following commands:
```
python kl_div_help.py --model_size 8b --explanation top --window_size 32 --num_sentences 2000 --start_sentence 0 
python kl_div_help.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 
python kl_div_help.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 --score fuzz 
python kl_div_help.py --model_size 8b --explanation quantiles --window_size 32 --num_sentences 2000 --start_sentence 0 --score recall 
python kl_div_help.py --model_size 8b-top_top5 --explanation top --window_size 32 --num_sentences 2000 --start_sentence 0 
python kl_div_help.py --model_size 70b --explanation quantiles --window_size 32 --num_sentences 1000 --start_sentence 0 

```
