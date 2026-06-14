# 🩸 Hayaat AI | Emergency Civic Dispatch

Hayaat AI is a predictive, traffic-aware blood donor dispatch network and medical screening application. It acts as an intelligent, automated bridge connecting hospitals, blood banks, and verified volunteer donors during emergencies.

## 🚀 Features

- **Multi-Lingual Medical Screening Chatbot:** 
  An interactive conversational bot that screens potential donors for eligibility (weight limits, recent donations, and high-risk medical conditions) using English, Urdu, and Roman Urdu.
- **Traffic-Aware Dispatch Algorithm:** 
  Matches required blood types to available donors and simulates arrival times using dynamic traffic and distance factors.
- **Smart Donor Registry:** 
  A 7-column schema database `[Name, Blood Type, City, Area, Phone Number, Status, Badge]` with gamified badges (🥇 Hero, 💎 Legend) to track the active community.
- **Secure Data Handling:** 
  Users can securely opt-out by typing 'Unsubscribe' in the chat, which automatically scans the records and permanently drops their profile without leaving blank data rows. Includes an Admin Panel for manual overrides.
- **Predictive Analytics:** 
  A seasonal forecasting module to anticipate spikes in trauma or medical cases (e.g., Eid-ul-Fitr traffic, Monsoon Dengue waves) and proactively run blood drives.

## 🛠️ Tech Stack
- **Frontend / UI:** [Gradio](https://gradio.app/) (with custom high-contrast CSS overrides)
- **Backend / Data:** Python, Pandas

## 💻 Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/hayaat-ai.git
   cd hayaat-ai
   ```

2. **Install dependencies:**
   Make sure you have Python installed. Run the following command to install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   *The Gradio interface will launch locally, usually at `http://127.0.0.1:7860/`.*

## ☁️ Deployment (Hugging Face Spaces)
This application is fully containerized and ready to be deployed on Hugging Face Spaces using the Gradio SDK.
Simply upload the `app.py`, `donor_registry.csv`, and `requirements.txt` to your space and it will automatically build and launch!
