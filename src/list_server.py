from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Variable dictionaries to save the data
todo_lists = {}     # {list_id: {"name": <name>}}
todo_entries = {}   # {entry_id: {"name": <name>, "description": <description>, "list_id": <list_id>}}


#Build the return object for a list
def build_list(list_id):
    return {"id": list_id, **todo_lists[list_id]}

#Build the return object for all lists
def build_lists():
    return [build_list(list_id) for list_id in todo_lists]

#Build the return object for an entry
def build_entry(entry_id):
    return {"id": entry_id, **todo_entries[entry_id]}

#Build the return object for all entries of a specific list
def build_entries(list_id):
    return [build_entry(entry_id) for entry_id in todo_entries if todo_entries[entry_id]["list_id"] == list_id]


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# Controller

#Get all lists
@app.route("/todo-list", methods=["GET"])
def get_lists():
    return jsonify(build_lists()), 200

#Add new list
@app.route("/todo-list", methods=["POST"])
def add_list():
    body = request.get_json()
    if not body or "name" not in body:
        return "", 400
    #Save list to object
    list_id = str(uuid.uuid4())
    todo_lists[list_id] = {
        "name": body["name"]
    }

    return jsonify(build_list(list_id)), 201

#Get a single list with all entries
@app.route("/todo-list/<list_id>", methods=["GET"])
def get_list(list_id):
    if list_id not in todo_lists:
        return "", 404

    return jsonify( build_entries(list_id)), 200

#Delete a list and all entries
@app.route("/todo-list/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    if list_id not in todo_lists:
        return "", 404
    del todo_lists[list_id]
    entries_to_delete = []
    for key in todo_entries.keys():
        if todo_entries[key]["list_id"] == list_id:
            del todo_entries[key]
    return "", 204

#Add a new item to a list
@app.route("/todo-list/<list_id>", methods=["POST"])
def add_entry_to_list(list_id):
    if list_id not in todo_lists:
        return "", 404
    
    body = request.get_json()
    if not body:
        return "", 400

    required_fields = ["name", "description"]
    if any(field not in body for field in required_fields):
        return "", 400

    entry_id = str(uuid.uuid4())
    todo_entries[entry_id] = {
        "name": body["name"],
        "description": body["description"],
        "list_id": list_id
    }

    return jsonify(build_entry(entry_id)), 201


@app.route("/todo-list/entry/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    if entry_id not in todo_entries.keys():
        return "", 404
    del todo_entries[entry_id]
    return "", 204

if __name__ == "__main__":
    app.run(port=5000)