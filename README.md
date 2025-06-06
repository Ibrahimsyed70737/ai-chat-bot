# AI Image Generator

This is a simple React application that allows users to generate images from text prompts using the Hugging Face Inference API. It provides a user-friendly interface to input a prompt, select the number of images, and choose an aspect ratio.

## ✨ Features

* **Text-to-Image Generation:** Convert textual descriptions into stunning images.
* **Multiple Image Output:** Generate up to 4 images per prompt.
* **Aspect Ratio Selection:** Choose between Square (1:1), Landscape (16:9), and Portrait (9:16) aspect ratios.
* **Dark Mode Toggle:** Switch between light and dark themes for a personalized viewing experience.
* **Random Prompt Suggestion:** Get inspiration with a click of a button.
* **Image Download:** Easily download generated images to your device.

## 🚀 Getting Started (For Beginners)

Follow these steps to get the project up and running on your local machine.

### 📋 Prerequisites

Before you begin, make sure you have the following installed:

* **Node.js & npm (or Yarn):** This is required to run the React application.
    * Download from: [https://nodejs.org/](https://nodejs.org/) (Node.js comes with npm).
    * Verify installation: Open your terminal or command prompt and type:
        ```bash
        node -v
        npm -v
        ```
        (If you prefer Yarn, you can install it via `npm install -g yarn` and verify with `yarn -v`)
* **Git:** This is used for cloning the repository.
    * Download from: [https://git-scm.com/downloads](https://git-scm.com/downloads)
    * Verify installation: Open your terminal or command prompt and type:
        ```bash
        git --version
        ```
* **Hugging Face Account & API Token:** You'll need a Hugging Face account and an API token to use their inference API for image generation.
    * Sign up/Login: [https://huggingface.co/](https://huggingface.co/)
    * **Get your API Token:**
        1.  Log in to your Hugging Face account.
        2.  Click on your **profile picture** (top right corner).
        3.  Select **"Access Tokens"**.
        4.  Click **"New token"**.
        5.  Give it a **Name** (e.g., `ImageGeneratorApp`).
        6.  For **"Role"**, select **"read"**.
        7.  Click **"Generate a token"**.
        8.  **IMPORTANT:** Copy the token immediately! You won't see it again. It usually starts with `hf_`.

### 📦 Installation

1.  **Clone the Repository:**
    Open your terminal or command prompt and run the following command to clone the project to your local machine:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    # Replace YOUR_USERNAME and YOUR_REPOSITORY_NAME with your actual GitHub username and repository name
    # For example: git clone [https://github.com/syedibrahim123/my-ai-image-generator.git](https://github.com/syedibrahim123/my-ai-image-generator.git)
    ```
2.  **Navigate to the Project Directory:**
    Change your current directory to the newly cloned project folder:
    ```bash
    cd YOUR_REPOSITORY_NAME
    # For example: cd my-ai-image-generator
    ```
3.  **Install Dependencies:**
    Install all the necessary Node.js packages:
    ```bash
    npm install
    # or if you use Yarn:
    # yarn install
    ```
4.  **Set up your Environment Variable (.env file):**
    This step is crucial for securely storing your Hugging Face API token.
    * In the root directory of your project (the `YOUR_REPOSITORY_NAME` folder), create a new file named exactly: `.env`
    * Open the `.env` file with a text editor (like Notepad, VS Code, Sublime Text, etc.) and add the following line. **Make sure to replace `YOUR_HUGGING_FACE_API_TOKEN` with the actual token you copied from Hugging Face.**
        ```
        REACT_APP_HUGGING_FACE_API_TOKEN=YOUR_HUGGING_FACE_API_TOKEN
        ```
        **Important:**
        * There should be no spaces around the `=` sign.
        * **Do NOT** commit this `.env` file to your GitHub repository. It's already listed in the `.gitignore` file to prevent accidental uploads.

### 🏃 Running the Application

After completing the installation and API key setup, you can run the application:

1.  **Start the Development Server:**
    In your terminal (still in the project root directory), run:
    ```bash
    npm start
    # or if you use Yarn:
    # yarn start
    ```
2.  **Open in Browser:**
    Your browser should automatically open a new tab at `http://localhost:3000` (or another port if 3000 is in use). If not, open your browser and go to that address manually.

You should now see the AI Image Generator interface.

## ⚠️ Troubleshooting Common Issues

* **"Authentication/Permission error (Status: 403)"**:
    * **Invalid Token:** Your Hugging Face API token is incorrect or expired. Go back to HuggingFace.co -> Access Tokens, create a new token, copy it carefully, and update your `.env` file. Remember to save the `.env` file.
    * **Incorrect Permissions:** Ensure your Hugging Face API token has at least the **"Make calls to Inference Providers"** permission enabled under the "Inference" section.
    * **Server Restart:** After updating your `.env` file, you **must restart your development server** (Ctrl+C in the terminal, then `npm start` again) for the changes to take effect.

* **"Model loading error (Status: 503)"**:
    * The Hugging Face model might be busy loading or experiencing high traffic. Wait a few moments and try generating again. Sometimes, the first request to a model can take longer as it "warms up".

* **"Rate limit exceeded (Status: 429)"**:
    * You've sent too many requests in a short period. Hugging Face's free tier has rate limits. Wait for a few minutes and try again. For higher usage, consider their paid plans.

* **"Error: Hugging Face API token is not configured"**:
    * This means `process.env.REACT_APP_HUGGING_FACE_API_TOKEN` is `undefined` or an empty string. Double-check that you created the `.env` file correctly in the project root, that the variable name is exactly `REACT_APP_HUGGING_FACE_API_TOKEN`, and that you've restarted your development server.

## 🤝 Contributing

If you'd like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request.

## 📄 License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).
