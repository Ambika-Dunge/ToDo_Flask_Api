#!/usr/bin/env python3
"""
To-Do List REST API with Flask + a simple, attractive UI.

Endpoints:
    POST   /tasks           -> Add a new task (fields: title, optional due_date)
    GET    /tasks           -> Get all tasks
    GET    /tasks/<id>      -> Get a single task by ID
    PUT    /tasks/<id>      -> Update task details (title, due_date, completed)
    DELETE /tasks/<id>      -> Delete a task

Data:
    - Stored in memory at runtime and persisted to a JSON file (tasks.json).
    - Each task has: id, title, completed, due_date (ISO "YYYY-MM-DD" or null),
      created_at, updated_at.
"""
from __future__ import annotations

from flask import Flask, jsonify, request, render_template, send_from_directory, abort
from datetime import datetime
import json
import os
from typing import List, Dict, Any, Optional

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")

# In-memory storage
tasks: List[Dict[str, Any]] = []
next_id: int = 1

def load_tasks_from_file() -> None:
    """Load tasks from the JSON file into memory, set next_id correctly."""
    global tasks, next_id
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    tasks = data
                else:
                    tasks = []
        except json.JSONDecodeError:
            tasks = []
    else:
        tasks = []
    # Set next_id to 1 + max existing id
    if tasks:
        next_id = max(t.get("id", 0) for t in tasks) + 1
    else:
        next_id = 1

def save_tasks_to_file() -> None:
    """Persist the in-memory list to a JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Validate and normalize date string (YYYY-MM-DD). Return None if no date."""
    if date_str in (None, "", "null"):
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD.")


# ----------------------
# Routes: UI
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------------
# Routes: API
# ----------------------
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        abort(400, description="Field 'title' is required and cannot be empty.")
    due_date = parse_date(data.get("due_date"))
    now = datetime.utcnow().isoformat() + "Z"

    global next_id
    task = {
        "id": next_id,
        "title": title,
        "completed": False,
        "due_date": due_date,
        "created_at": now,
        "updated_at": now,
    }
    next_id += 1
    tasks.append(task)
    save_tasks_to_file()
    return jsonify(task), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")
    return jsonify(task), 200

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id: int):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        abort(404, description="Task not found.")

    data = request.get_json(silent=True) or {}

    if "title" in data:
        new_title = (data.get("title") or "").strip()
        if not new_title:
            abort(400, description="Field 'title' cannot be empty.")
        task["title"] = new_title

    if "due_date" in data:
        task["due_date"] = parse_date(data.get("due_date"))

    if "completed" in data:
        completed = data.get("completed")
        if isinstance(completed, bool):
            task["completed"] = completed
        else:
            abort(400, description="Field 'completed' must be a boolean.")

    task["updated_at"] = datetime.utcnow().isoformat() + "Z"
    save_tasks_to_file()
    return jsonify(task), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id: int):
    global tasks
    idx = next((i for i, t in enumerate(tasks) if t["id"] == task_id), None)
    if idx is None:
        abort(404, description="Task not found.")
    tasks.pop(idx)
    save_tasks_to_file()
    return "", 204

# Error handlers for clean JSON responses
@app.errorhandler(400)
def bad_request(e):
    return jsonify(error="Bad Request", message=str(e.description)), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not Found", message=str(e.description)), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error="Method Not Allowed", message="Invalid HTTP method for this endpoint."), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify(error="Server Error", message="An unexpected error occurred."), 500

if __name__ == "__main__":
    # Make sure data file exists
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)
