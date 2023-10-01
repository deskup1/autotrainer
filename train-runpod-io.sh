cd /workspace/kohya_ss
source ./venv/bin/activate
accelerate launch --num_cpu_threads_per_process=2 "./sdxl_train.py" --train_text_encoder --full_bf16 --pretrained_model_name_or_path="/workspace/autotrainer/model/base-model.safetensors" --in_json="/workspace/autotrainer/model/config/meta_lat.json" --train_data_dir="/workspace/autotrainer/images/dataset" --output_dir="/workspace/saxime" --logging_dir="/workspace/logs" --dataset_repeats=1 --learning_rate=4e-06 --enable_bucket --resolution="1024,1024" --min_bucket_reso=512 --max_bucket_reso=2048 --save_model_as=safetensors --output_name="model.safetensors" --no_half_vae --learning_rate="4e-06" --lr_scheduler="constant" --train_batch_size="4" --mixed_precision="bf16" --save_precision="fp16" --caption_extension=".txt" --cache_latents --optimizer_type="Adafactor" --optimizer_args scale_parameter=False relative_step=False warmup_init=False --max_data_loader_n_workers="0" --keep_tokens="3" --caption_dropout_every_n_epochs="1" --caption_dropout_rate="0.3" --bucket_reso_steps=64 --shuffle_caption --gradient_checkpointing --xformers --bucket_no_upscale --noise_offset=0.01 --sample_sampler=k_dpm_2_a --sample_prompts="/workspace/autotrainer/model/sample/prompt.txt" --sample_every_n_epochs="1"