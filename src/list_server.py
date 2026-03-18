from flask import Flask, request, jsonify

app = Flask(__name__)

# Variable dictionaries to save the data
todo_lists = {}     # {list_id: {"name": <name>}}
todo_entries = {}   # {entry_id: {"name": <name>, "description": <description>, "user_id": <user_id>, "list_id": <list_id>}}
