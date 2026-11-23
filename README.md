# 🌾 PaddyCare – AI-Powered Paddy Disease Detection & Farmer Support Platform

PaddyCare is an AI-powered paddy disease detection and farmer support platform designed to help identify common paddy leaf diseases through image-based classification. The system combines deep learning, visual explainability and farmer-oriented information services in one application.

Users can upload an image of a paddy leaf and receive a predicted disease classification with its confidence score. The application also incorporates Grad-CAM visual explanations to highlight the image regions that influenced the model's prediction.

Beyond disease detection, PaddyCare provides features for maintaining prediction history, connecting with the farming community, accessing agricultural information and viewing market-related information.

---

## 📌 Project Overview

Paddy cultivation is affected by several leaf diseases that can impact crop health and productivity. Identifying these diseases at an early stage can help farmers take timely action.

PaddyCare aims to make image-based disease identification more accessible through a simple web interface powered by a trained deep learning model.

The project focuses on three main aspects:

- **Disease Detection:** Classifying paddy leaf images using a trained convolutional neural network.
- **Explainable AI:** Using Grad-CAM to visualize the regions that contribute to the model's predictions.
- **Farmer Support:** Bringing useful agricultural information and community-oriented features into one platform.

## ✨ Key Features

### 1. AI-Based Paddy Disease Detection
- Upload a paddy leaf image for disease prediction.
- Uses a trained MobileNetV2 deep learning model.
- Displays the predicted disease and confidence score.
- Includes image-quality checks before prediction.

### 2. Grad-CAM Explainability
- Generates visual explanations for model predictions using Gradient-weighted Class Activation Mapping (Grad-CAM).
- Produces a heatmap highlighting image regions that contribute to the predicted class.
- Overlays the heatmap on the original leaf image.
- Helps users understand which visual regions influenced the model's decision.

Grad-CAM provides an interpretation of the model's prediction; it does not independently confirm the presence or severity of a disease.

### 3. Prediction History
- Maintains a record of previous predictions.
- Allows users to revisit their prediction history.

### 4. Farmer Community
- Provides a community-oriented space for users to connect and share information.
- Supports interaction through community posts.

### 5. Agricultural Information
- Provides agricultural information, including government schemes and useful resources.
- Includes market-related information and mandi price lookup functionality.

### 6. User Accounts
- Account creation and login.
- User account management.
- Personalized access to application features.

---

## 🧠 Deep Learning Model Development

An important part of this project was experimenting with and comparing two different transfer-learning architectures before selecting the final model.

Model training and experimentation were carried out using **Google Colab**.

### Dataset

The project uses paddy leaf images associated with the Paddy Doctor dataset.

The dataset was organized into training, validation and testing splits for model development and evaluation.

| Dataset Split | Number of Images |
|---|---:|
| Training | 3,462 |
| Validation | 742 |
| Testing | 742 |
| **Total** | **4,946** |

The classification task involves four categories:

| Class | Description |
|---|---|
| `bacterial_leaf_blight` | Bacterial Leaf Blight |
| `blast` | Rice Blast |
| `brown_spot` | Brown Spot |
| `normal` | Healthy / Normal Leaf |

### Model Architectures Evaluated

Two transfer-learning architectures were trained and evaluated:

**1. EfficientNetB0**

EfficientNetB0 was evaluated as one of the candidate architectures for paddy disease classification. Its performance was measured using test accuracy, loss, precision, recall and F1-score.

**2. MobileNetV2**

MobileNetV2 was trained and evaluated using the same four-class classification task. Its performance was compared against EfficientNetB0 to determine the more suitable model for the application.

### Model Comparison

The following results were obtained from the saved test-set evaluation reports.

| Evaluation Metric | MobileNetV2 | EfficientNetB0 |
|---|---:|---:|
| Test Accuracy | **89.89%** | 86.66% |
| Test Loss | **0.2745** | 0.4069 |
| Macro Precision | **0.8791** | 0.8662 |
| Macro Recall | **0.8747** | 0.8235 |
| Macro F1-Score | **0.8767** | 0.8410 |
| Weighted F1-Score | **0.8987** | 0.8651 |

### Final Model Selection

Based on the evaluation results, **MobileNetV2 was selected as the final model**.

It achieved a test accuracy of 89.89%, compared with 86.66% for EfficientNetB0. It also performed better across the other reported evaluation metrics.

The selected trained model is saved as:

`models/mobilenetv2_final.keras`

This model is integrated into the PaddyCare application for real-time image-based predictions.

---

## 📊 Training & Evaluation Results

The training experiments produced several evaluation artifacts for both architectures.

The training results archive is available here:

**[Download Training Results – ZIP](training-results.zip)**

The archive contains:

| File | Description |
|---|---|
| `efficientnetb0_accuracy.png` | EfficientNetB0 accuracy graph |
| `efficientnetb0_loss.png` | EfficientNetB0 loss graph |
| `efficientnetb0_confusion_matrix.png` | EfficientNetB0 confusion matrix |
| `efficientnetb0_classification_report.csv` | EfficientNetB0 classification metrics |
| `efficientnetb0_history.csv` | EfficientNetB0 training history |
| `mobilenetv2_accuracy.png` | MobileNetV2 accuracy graph |
| `mobilenetv2_loss.png` | MobileNetV2 loss graph |
| `mobilenetv2_confusion_matrix.png` | MobileNetV2 confusion matrix |
| `mobilenetv2_classification_report.csv` | MobileNetV2 classification metrics |
| `mobilenetv2_history.csv` | MobileNetV2 training history |
| `model_comparison.csv` | Comparison of both architectures |
| `train_split.csv` | Training dataset split information |
| `validation_split.csv` | Validation dataset split information |
| `test_split.csv` | Testing dataset split information |

These artifacts document the model training experiments, evaluation results and the comparison used to select MobileNetV2.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Deep Learning | TensorFlow, Keras |
| Model Architectures | MobileNetV2, EfficientNetB0 |
| Explainable AI | Grad-CAM |
| Image Processing | Pillow, NumPy |
| Frontend / Web Application | Streamlit |
| Database | SQLite |
| Model Training Environment | Google Colab |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```text
PaddyCare/
│
├── data/
│   ├── app/
│   ├── local/
│   ├── processed/
│   ├── public/
│   └── splits/
│
├── models/
│   └── mobilenetv2_final.keras
│
├── notebooks/
│
├── results/
│
├── scripts/
│   └── test_mandi_api.py
│
├── src/
│   ├── data/
│   ├── evaluation/
│   ├── explain/
│   │   └── gradcam.py
│   ├── inference/
│   │   ├── predict.py
│   │   └── quality.py
│   ├── knowledge/
│   │   └── disease_info.py
│   └── training/
│
├── tests/
│   ├── test_db.py
│   └── test_mandi.py
│
├── webapp/
│   ├── app.py
│   ├── db.py
│   ├── theme.py
│   ├── services/
│   │   └── mandi.py
│   ├── views/
│   │   ├── account.py
│   │   ├── community.py
│   │   ├── history.py
│   │   ├── home.py
│   │   ├── info.py
│   │   ├── login.py
│   │   └── predict.py
│   └── data/
│
├── .streamlit/
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Installation & Setup

Follow these steps to run PaddyCare locally.

### Prerequisites

- Python 3.10 or a compatible version.
- Git.
- The trained MobileNetV2 model file.

### 1. Clone the Repository

```bash
git clone https://github.com/charishma-rai/PaddyCare.git
```

### 2. Navigate to the Project Directory

```bash
cd PaddyCare
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment:

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac / Linux:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify the Trained Model

Ensure that the trained model is present at:

```text
models/mobilenetv2_final.keras
```

### 6. Run the Application

From the project root directory:

```bash
streamlit run webapp/app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

Create an account or sign in to access the application.

---

## 🔑 Optional API Configuration

PaddyCare includes a mandi market information service that uses the data.gov.in API.

To enable live market price information:

1. Register on [data.gov.in](https://data.gov.in/).
2. Obtain an API key.
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
4. Add your API key:

```toml
DATA_GOV_API_KEY = "your_api_key_here"
```

Keep your actual API key private. Never commit `secrets.toml` to GitHub.

The rest of the application can be used without configuring this optional API key.

---

## 🧪 Testing

The project includes tests for database operations and mandi-related functionality.

Run the database tests:

```bash
python tests/test_db.py
```

Run the mandi service tests:

```bash
python tests/test_mandi.py
```

---

## 🚀 Future Improvements

Some potential areas for further development include:

- Expanding disease classification to support additional paddy diseases.
- Improving model generalization using more diverse field images.
- Further optimizing model performance for mobile and low-resource environments.
- Integrating a persistent cloud database for user accounts and prediction history.
- Enhancing multilingual support for farmers.
- Adding more verified agricultural resources and expert-reviewed recommendations.
- Exploring additional explainability techniques to complement Grad-CAM.

---

## ⚠️ Limitations

- Model predictions depend on image quality, lighting conditions and the similarity of uploaded images to the training data.
- Grad-CAM provides a visual explanation of model behaviour, not a medical-style confirmation of crop disease.
- Prediction accuracy on the test dataset does not guarantee identical performance on every real-world field image.
- The current application uses local SQLite storage, which requires a persistent storage solution for reliable long-term deployment.
- Agricultural recommendations and disease information should be verified with qualified agricultural experts.

---

## 👩‍💻 Project Information

**Project Name:** PaddyCare

**Project Type:** AI / Machine Learning / Deep Learning / Web Application

**Primary Model:** MobileNetV2

**Explainability Technique:** Grad-CAM

**Model Training Platform:** Google Colab

**Repository:** [GitHub – PaddyCare](https://github.com/charishma-rai/PaddyCare)

---

*PaddyCare aims to make AI-powered paddy disease identification more accessible by combining deep learning, explainable predictions and farmer-focused digital services in a single platform.*
