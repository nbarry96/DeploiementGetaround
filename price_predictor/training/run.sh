docker run -it \
  -p 5432:5432 \
  -v "$(pwd):/home/app" \
  -e APP_URI="YOUR_APP_URI" \
  -e AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY" \
  -e MLFLOW_TRACKING_DEBUG=true \
  getaround-mlflow-training python train.py \
  --regressor Ridge \
  --cv 3 \
  --alpha 0.2 0.5 1 2 3 \
  --executor_name "Nene_Ridge"

#getaround-mlflow-training python train.py \
#  --regressor Ridge \
#  --cv 3 \
#  --alpha 0.2 0.5 1 \
#  --executor_name "Nene_LR"
#LR
  #getaround-mlflow-training python train.py \
  #--executor_name "Nene" \
  
#RF
  #getaround-mlflow-training python train.py \
  #--regressor RF \
  #--cv 3 \
  #--max_depth 10 20 30 \
  #--min_samples_leaf 1 5 \
  #--min_samples_split 2 10 20 \
  #--n_estimators 50 100 150 \
  #--executor_name "Nene_RF" \




 
 #getaround-mlflow-training python train.py --regressor RF

 #getaround-mlflow-training python train.py
 
