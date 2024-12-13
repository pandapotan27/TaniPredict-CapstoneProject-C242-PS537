# TaniPredict-CapstoneProject-C242-PS537

Tutorial Deploying Models In Cloud Run

Create Buckets
Upload file models .h5 and json
Create Firestore, start Collection
Create a firewall to allow ports to run

Since the Firestore Collection has been created to store predictions, 
a cloud storage is created to store models and metadata and then deploy 
using Cloud Run

Deploying Models in Cloud Run

Clone the repository from local to Google Cloud cloud sheel

Install the required libraries

Create a venv folder, install in the terminal 

python3 -m venv venv_folder_name

Run the command

gcloud services enable run.googleapis.com

docker build -t gcr.io/models-tomato-chili/tanipredict:v1 .

docker push gcr.io/models-tomato-chili/tanipredict:v1

gcloud run deploy tanipredict-service \

--image gcr.io/models-tomato-chili/tanipredict:v1 \
--region asia-southeast2 \
--platform managed \
--allow-unauthenticated \
--memory 1Gi

Test Endpoint in POSTMAN 

Test Tomato & Chili

Input image and plant name 
![image](https://github.com/user-attachments/assets/87d653e9-e89b-4992-944c-3b4e01d79d24)

Response successfully
{
    "confidenceScore": 0.9998701810836792,
    "createdAt": "2024-12-13T13:27:49.675896",
    "id": "e7de2782-a1d2-4098-98a9-44cc53d813ac",
    "isAboveThreshold": true,
    "plant": "tomato",
    "result": "Bacterial Spot"
}


Give the endpoint to the mobile development team
