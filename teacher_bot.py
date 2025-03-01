from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import subprocess

app = Flask(__name__)
CORS(app)

# CSV File Paths (Mimicking a Database)
USER_DATA_FILE = "user_data.csv"
STUDENT_PROGRESS_FILE = "student_progress.csv"

# Ensure CSV files exist
for file, columns in [
    (USER_DATA_FILE, ["Username", "Password", "DOB", "Role", "Linked_Student"]),
    (STUDENT_PROGRESS_FILE, ["Username", "Experiments_Completed", "Quiz_Scores", "Study_Hours", "Performance_Level"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

# ✅ Mimicking a Model using Pandas
class UserDatabase:
    @staticmethod
    def get_users():
        return pd.read_csv(USER_DATA_FILE)

    @staticmethod
    def save_users(df):
        df.to_csv(USER_DATA_FILE, index=False)

    @staticmethod
    def add_user(username, password, dob, role, linked_student):
        df = UserDatabase.get_users()
        if username in df["Username"].values:
            return False, "Username already exists!"
        
        new_user = pd.DataFrame([[username, password, dob, role, linked_student]], 
                                columns=["Username", "Password", "DOB", "Role", "Linked_Student"])
        df = pd.concat([df, new_user], ignore_index=True)
        UserDatabase.save_users(df)
        return True, "Registration successful!"

# ✅ User Registration
@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    username, password, dob, role = data["username"], data["password"], data["dob"], data["role"]
    linked_student = data.get("linked_student", "-")

    success, message = UserDatabase.add_user(username, password, dob, role, linked_student)
    if not success:
        return jsonify({"error": message}), 400
    return jsonify({"message": message})

# ✅ User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username, password, dob = data["username"], data["password"], data["dob"]

    df = UserDatabase.get_users()
    user = df[(df["Username"] == username) & (df["Password"] == password) & (df["DOB"] == dob)]

    if user.empty:
        return jsonify({"error": "Invalid credentials!"}), 401

    role = user["Role"].values[0]
    return jsonify({"message": "Login successful!", "role": role, "success": True})

# ✅ View Student Progress (Mimicking Database Queries)
@app.route('/view_progress', methods=['GET'])
def view_progress():
    username = request.args.get("username")
    role = request.args.get("role")

    df_progress = pd.read_csv(STUDENT_PROGRESS_FILE)
    df_users = UserDatabase.get_users()

    if role == "Student":
        progress = df_progress[df_progress["Username"] == username]
    elif role in ["Parent", "Teacher"]:
        linked_student = df_users[df_users["Username"] == username]["Linked_Student"].values[0]
        progress = df_progress[df_progress["Username"] == linked_student]
    else:
        return jsonify({"error": "Access Denied!"}), 403

    if progress.empty:
        return jsonify({"error": "No progress found."}), 404
    return progress.to_json(orient="records")

# ✅ Update Student Progress
@app.route('/update_progress', methods=['POST'])
def update_progress():
    data = request.json
    username = data["username"]
    experiments_completed = data.get("experimentsCompleted", 0)
    quiz_scores = data.get("quizScores", 0)
    study_hours = data.get("studyHours", 0)
    performance_level = data.get("performanceLevel", "Not Evaluated")

    df_progress = pd.read_csv(STUDENT_PROGRESS_FILE)

    if username in df_progress["Username"].values:
        df_progress.loc[df_progress["Username"] == username, ["Experiments_Completed", "Quiz_Scores", "Study_Hours", "Performance_Level"]] = \
            [experiments_completed, quiz_scores, study_hours, performance_level]
    else:
        new_progress = pd.DataFrame([[username, experiments_completed, quiz_scores, study_hours, performance_level]],
                                    columns=["Username", "Experiments_Completed", "Quiz_Scores", "Study_Hours", "Performance_Level"])
        df_progress = pd.concat([df_progress, new_progress], ignore_index=True)

    df_progress.to_csv(STUDENT_PROGRESS_FILE, index=False)
    return jsonify({"message": "Student progress updated successfully!"})

# ✅ Chatbot API
@app.route('/chatbot', methods=['POST'])
def chat_with_bot():
    data = request.json
    question = data.get("question", "").strip()
    
    # Forward the question to the Ollama API using subprocess
    def chat_with_ollama(prompt):
        try:
            result = subprocess.run(
                ["ollama", "run", "phi"],  # Use "run" instead of "chat"
                input=prompt,  # Directly send user input
                text=True,
                capture_output=True,
                encoding='utf-8'  # Ensure UTF-8 encoding
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr.strip()}"

        except Exception as e:
            return f"Error: {str(e)}"

    bot_response = chat_with_ollama(question)
    
    # Ensure the response has correct spacing
    formatted_response = " ".join(bot_response.split())
    
    return jsonify({"response": formatted_response})

# ✅ Run Flask App
if __name__ == "__main__":
    app.run(debug=True)