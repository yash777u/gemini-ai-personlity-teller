# 🚀 How to Deploy to Streamlit Cloud

Follow these steps to deploy your **Big Five Personality Assessment** app for free!

## 1. Prepare Your Repository
- Create a new **public** repository on [GitHub](https://github.com/new).
- Upload the following files from your local directory:
  - `flashcard_ui.py` (Main app)
  - `scoring.py` (Scoring logic)
  - `ai_results.py` (AI logic & radar chart)
  - `question.txt` (Personality questions)
  - `requirements.txt` (Dependencies)
- **⚠️ IMPORTANT**: Do NOT upload your `.env` file to GitHub. It's for local use only.

## 2. Deploy on Streamlit Cloud
- Go to [Streamlit Cloud](https://share.streamlit.io/) and log in with your GitHub account.
- Click **"New app"**.
- Select your repository and the main file (`flashcard_ui.py`).

## 3. Configure Your API Key (Secrets)
Since you won't be uploading your `.env` file to GitHub, you need to add your API key to Streamlit's "Secrets":
1. On the deployment page, click **"Advanced settings..."** before deploying.
2. In the **Secrets** section, paste the following:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```
3. Click **"Save"** and then **"Deploy!"**.

## 4. That's it!
Your app will be live in a few minutes. You can share the provided URL with anyone to let them take the assessment!

---
**Tip**: If you ever update your code on GitHub, Streamlit Cloud will automatically rebuild and update your live app! 🔄
