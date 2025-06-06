from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import uuid
import requests
import google.generativeai as genai
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file at the very beginning
load_dotenv()

app = Flask(__name__)
# Get secret key from environment variable
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_super_secret_key_change_this_in_prod') # Fallback for dev if .env not loaded

# --- MongoDB Setup ---
# Get MongoDB URI from environment variable
MONGO_URI = os.environ.get('MONGO_URI', "mongodb://localhost:27017/") # Fallback to local
client = MongoClient(MONGO_URI)
db = client.ai_chat_portal # Your database name

users_collection = db.users
chat_histories_collection = db.chat_histories

# Ensure unique index for username
users_collection.create_index('username', unique=True)

# --- Gemini setup ---
# Get Gemini API key from environment variable
genai.configure(api_key=os.environ.get('GEMINI_API_KEY', "YOUR_FALLBACK_GEMINI_API_KEY_HERE")) # Fallback for dev if .env not loaded
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# --- Helper Functions (Tools) ---
def get_weather(city):
    """
    Fetches current weather data for a given city using OpenWeatherMap API.
    Returns a formatted string with temperature and description, or an error message.
    """
    # Get OpenWeather API key from environment variable
    api_key = os.environ.get('OPENWEATHER_API_KEY', "YOUR_FALLBACK_OPENWEATHER_API_KEY_HERE") # Fallback for dev if .env not loaded
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"appid": api_key, "q": city, "units": "metric"}
    try:
        res = requests.get(base_url, params=params)
        res.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = res.json()

        if data.get("cod") != 200:
            return f"<b>Error:</b> Could not retrieve weather for '{city}'. {data.get('message', 'City not found.')}"

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"<b>Weather in {city.title()}:</b> {temp}°C, {desc.capitalize()}."
    except requests.exceptions.RequestException as e:
        return f"<b>Error:</b> Failed to connect to weather service: {e}"
    except Exception as e:
        return f"<b>Error:</b> An unexpected error occurred: {e}"

def google_search(query):
    """
    Generates a Google search URL for a given query.
    Returns an HTML link that opens in a new tab.
    """
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return f"<b>Google Search:</b> <a href='{url}' target='_blank'>{query}</a>"

def ask_ai(message):
    """
    Sends a message to the Gemini AI model and returns its response.
    Includes basic error handling for AI generation.
    """
    try:
        response = model.generate_content(message)
        # Check if candidates and content exist before accessing text
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            return response.candidates[0].content.parts[0].text
        else:
            return "<b>AI Error:</b> No valid response received from AI."
    except Exception as e:
        return f"<b>AI Error:</b> Failed to generate content: {e}"

# --- Routes ---

@app.route("/", methods=["GET"])
def index():
    """
    Handles the main page load (index.html).
    """
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    """
    Handles user login.
    GET: Renders the login form.
    POST: Processes login credentials.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = str(user["_id"]) # Store ObjectId as string
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("chat_page"))
        else:
            flash("Invalid username or password.", "error")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    """
    Handles user registration.
    GET: Renders the signup form.
    POST: Processes new user registration.
    """
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return render_template("signup.html")

        if users_collection.find_one({"email": email}):
            flash("Email already registered. Please use a different one or log in.", "error")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)
        
        try:
            user_data = {
                "email": email,
                "username": username,
                "password_hash": hashed_password,
            }
            users_collection.insert_one(user_data)
            # Initialize empty chat sessions for the user after successful registration
            chat_histories_collection.insert_one({"user_id": str(user_data["_id"]), "sessions": {}})
            
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login_page"))
        except Exception as e:
            flash(f"An error occurred during registration: {e}", "error")
            return render_template("signup.html")
    return render_template("signup.html")

@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session.
    """
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/chat", methods=["GET"]) # Changed back to /chat
def chat_page():
    """
    Handles the chat page load, manages chat sessions, and renders chat.html.
    Requires user to be logged in.
    """
    if "user_id" not in session:
        flash("Please log in to access the chat.", "warning")
        return redirect(url_for("login_page"))

    user_id = session["user_id"]
    # Ensure user_id is a valid ObjectId for MongoDB query
    try:
        user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        flash(f"Invalid user ID format: {e}", "error")
        session.pop("user_id", None)
        session.pop("username", None)
        return redirect(url_for("login_page"))

    if not user_doc:
        flash("User not found. Please log in again.", "error")
        session.pop("user_id", None)
        session.pop("username", None)
        return redirect(url_for("login_page"))

    # Load chat sessions for the current user from chat_histories_collection
    user_chat_sessions_doc = chat_histories_collection.find_one({"user_id": user_id})
    if not user_chat_sessions_doc:
        # If no chat history document exists, create one (should ideally happen during signup)
        user_chat_sessions_doc = {"user_id": user_id, "sessions": {}}
        chat_histories_collection.insert_one(user_chat_sessions_doc)

    chat_sessions_data = user_chat_sessions_doc["sessions"]

    # Determine current session ID
    sid = request.args.get("session")
    new_chat_requested = request.args.get("new") == "1"

    if new_chat_requested or not sid or sid not in chat_sessions_data:
        sid = str(uuid.uuid4())
        chat_sessions_data[sid] = {"title": "New Chat", "messages": []}
        # Update MongoDB with the new session
        chat_histories_collection.update_one(
            {"user_id": user_id},
            {"$set": {"sessions": chat_sessions_data}}
        )

    session["current_chat_sid"] = sid # Store current session ID in Flask session

    return render_template("chat.html", sessions=chat_sessions_data, current=sid, username=session["username"])


@app.route("/send_message", methods=["POST"]) # Renamed the POST endpoint for clarity
def send_message_post():
    """
    Handles incoming chat messages, processes them based on the selected action,
    and returns the AI's or tool's response.
    Requires user to be logged in.
    """
    if "user_id" not in session:
        return jsonify(response="Please log in to send messages."), 401 # Unauthorized

    user_id = session["user_id"]
    user_input = request.form.get("command", "").strip()
    action = request.form.get("action")
    sid = session.get("current_chat_sid") # Get current session ID from Flask session

    if not user_input or not sid:
        return jsonify(response="Please enter a command or select a chat session."), 400

    # Retrieve user's chat sessions from MongoDB
    user_chat_doc = chat_histories_collection.find_one({"user_id": user_id})
    if not user_chat_doc or sid not in user_chat_doc.get("sessions", {}): # Use .get() for safety
        return jsonify(response="Chat session not found or invalid."), 404

    current_chat_session = user_chat_doc["sessions"][sid]

    # Set chat title if it's a new chat and the first message
    if current_chat_session["title"] == "New Chat" and not current_chat_session["messages"]:
        current_chat_session["title"] = user_input[:20] # Take first 20 chars as title

    current_chat_session["messages"].append({"sender": "user", "message": user_input})

    reply = ""
    if action == "get_weather":
        reply = get_weather(user_input)
    elif action == "search_google":
        reply = google_search(user_input)
    elif action == "ask_ai":
        reply = ask_ai(user_input)
    else:
        reply = "<b>Error:</b> Invalid action selected."

    current_chat_session["messages"].append({"sender": "bot", "message": reply})

    # Update the chat session in MongoDB
    chat_histories_collection.update_one(
        {"user_id": user_id},
        {"$set": {f"sessions.{sid}": current_chat_session}},
        upsert=True # Ensure the document is created if it somehow didn't exist
    )

    return jsonify(response=reply)

if __name__ == "__main__":
    # Ensure the 'templates' folder exists in the same directory as app.py
    # and chat.html, login.html, signup.html are inside it.
    # For production, consider using a WSGI server like Gunicorn.
    app.run(debug=True)
