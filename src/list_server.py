from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Variable dictionaries to save the data
todo_lists = {}     # {list_id: {"name": <name>}}
todo_entries = {}   # {entry_id: {"name": <name>, "description": <description>, "user_id": <user_id>, "list_id": <list_id>}}


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





# Controller

#Get all lists
@app.route("/todo-list", methods=["GET"])
def get_lists():
    return jsonify(build_lists()), 200

#Add new list
@app.route("/todo-list", methods=["POST"])
def add_list():
    body = request.get_json
    if not body or "name" not in body:
        return "", 400
    list_id = str(uuid.uuid5)
    #TODO continue here


if __name__ == "__main__":
    app.run(port=5000)