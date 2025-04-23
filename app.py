from flask import Flask, request, jsonify, render_template, send_from_directory
from datetime import datetime
import json
import os
from uuid import uuid4

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))


TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

@app.route('/JS/<path:path>')
def serve_js(path):
    return send_from_directory('JS', path)

@app.route('/CSS/<path:path>')
def serve_css(path):
    return send_from_directory('CSS', path)

@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
   
    completed = request.args.get('completed')
    if completed in ['true', 'false']:
        tasks = [t for t in tasks if t['completed'] == (completed == 'true')]
    
    due_date = request.args.get('due_date')
    if due_date:
        try:
            datetime.strptime(due_date, '%Y-%m-%d')
            tasks = [t for t in tasks if t.get('due_date') == due_date]
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    priority = request.args.get('priority')
    if priority in ['low', 'medium', 'high']:
        tasks = [t for t in tasks if t.get('priority') == priority]
    
    return jsonify(tasks)

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    new_task = {
        'id': str(uuid4()),
        'title': data['title'],
        'description': data.get('description', ''), 
        'due_date': data.get('due_date'),  
        'priority': data.get('priority', 'medium'),
        'completed': False,
        'theme': 'standard',
        'created_at': datetime.now().isoformat()
    }
    
    tasks = load_tasks()
    tasks.append(new_task)
    save_tasks(tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'due_date' in data:
        task['due_date'] = data['due_date']
    if 'priority' in data and data['priority'] in ['low', 'medium', 'high']:
        task['priority'] = data['priority']
    if 'completed' in data:
        task['completed'] = bool(data['completed'])
    
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify({'message': 'Task deleted'}), 200


@app.route('/api/tasks/<task_id>/complete', methods=['PUT'])
def mark_complete(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task['completed'] = True
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/<task_id>/incomplete', methods=['PUT'])
def mark_incomplete(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task['completed'] = False
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/<task_id>/priority', methods=['PUT'])
def update_task_priority(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    new_priority = data.get('priority')
    
    if new_priority not in ['low', 'medium', 'high']:
        return jsonify({'error': 'Priority must be "low", "medium", or "high"'}), 400
    
    task['priority'] = new_priority
    save_tasks(tasks)
    return jsonify(task)

@app.route('/api/tasks/<task_id>/theme', methods=['PUT'])
def update_theme(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    if 'theme' not in data or data['theme'] not in ['standard', 'light', 'darker']:
        return jsonify({'error': 'Invalid theme'}), 400
    
    task['theme'] = data['theme']
    save_tasks(tasks)
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True)