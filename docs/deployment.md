# Gourmet AI: Deployment Guide

This guide will walk you through deploying Gourmet AI to production using **Vercel** for the React frontend and **Render** for the FastAPI backend.

Because this project uses a large Hugging Face dataset, deploying the backend as a cloud web service (Render) ensures it has the necessary compute environment to run the `data_processor.py` build step.

---

## 🚀 Part 1: Deploying the Backend (Render)

Render is perfect for Python FastAPI applications and can execute custom shell scripts during the build phase.

### Prerequisites
1. Ensure you have pushed all your latest code to your GitHub repository (including `render.yaml` and `backend/build.sh`).
2. Create an account at [Render.com](https://render.com) and link your GitHub account.

### Steps
1. In your Render Dashboard, click **New +** and select **Blueprint**.
2. Connect your GitHub repository (`Flukeshotz/Gourmet-AI`).
3. Render will automatically detect the `render.yaml` file in the root of your project.
4. Render will prompt you for any required Environment Variables marked as `sync: false`.
    * Set `GROQ_API_KEY` to your real Groq API key.
5. Click **Apply**.
6. Render will begin building your backend. You can watch the logs as it installs Python dependencies and runs `backend/build.sh` to download the Zomato dataset.
7. Once deployment is successful, Render will provide you with a live URL (e.g., `https://gourmet-ai-backend.onrender.com`).
8. **Copy this URL**, you will need it for the frontend!

---

## 🎨 Part 2: Deploying the Frontend (Vercel)

Vercel provides the fastest and most seamless deployment for Vite/React applications.

### Prerequisites
1. Create an account at [Vercel.com](https://vercel.com) and link your GitHub account.

### Steps
1. In your Vercel Dashboard, click **Add New... -> Project**.
2. Import your GitHub repository (`Flukeshotz/Gourmet-AI`).
3. In the **Configure Project** screen, make the following adjustments:
    * **Framework Preset:** Vite
    * **Root Directory:** Click Edit and select `frontend` (Important!)
4. Open the **Environment Variables** section and add the following key-value pair:
    * **Name:** `VITE_API_URL`
    * **Value:** The Render URL you copied in Part 1 + `/api` (e.g., `https://gourmet-ai-backend.onrender.com/api`)
5. Click **Deploy**.
6. Vercel will build and deploy your React app. Within a minute or two, you will receive your live `*.vercel.app` URL.

---

## 🎉 Verification

1. Open your live Vercel frontend URL.
2. Ensure you can see the UI.
3. Perform a search. The first search might take an extra 30-50 seconds if your Render free-tier backend went to sleep and needs to "cold start". Subsequent searches will be lightning fast!

**Congratulations! Your Multi-Agent AI Recommendation system is now live on the internet!**
