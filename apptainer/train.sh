ls -l
cd /mnt/code
python train.py --data-path /mnt/datasets/cubicasa/ --n-epoch 1 --batch-size 80 --log-path /mnt/output/job_results/
