export VLLM_WORKER_MULTIPROC_METHOD=spawn; CUDA_VISIBLE_DEVICES=0,1 python caching_gemma/generate_explanations.py --module .model.layers.8 --train_type "top" --n_examples_train 40 --model gemma/131k --experiment_name top40 --n_quantiles 10 --n_random 100 --n_examples_test 10 --features 300 --example_ctx_len 32 --width 131072