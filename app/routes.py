from flask import Blueprint, jsonify, make_response, request, abort
from app import db
from app.models.task import Task

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

def validate_task(task_id):
    try:
        task_id = int(task_id)
    except:
        abort(make_response({"message": "task invalid"}, 400))

    task = Task.query.get(task_id)

    if not task:
        abort(make_response({"message": "task not found"}, 404))
        
    return task

@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    if "title" not in request_body or "description" not in request_body:
        return make_response({"details": "Invalid data"}), 400
    else: 
        new_task = Task(title=request_body["title"],
                    description=request_body["description"])
        db.session.add(new_task)
        db.session.commit()

        return {
                "task": {
                    "id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "is_complete": new_task.is_complete
                }
            },201

@tasks_bp.route("", methods=["GET"])
def read_all_tasks():
    tasks = Task.query
    if "sort" in request.args:
        dir = request.args["sort"] 
        if dir == "asc":
            tasks = tasks.order_by(Task.title)
        elif dir == "desc":
            tasks = tasks.order_by(Task.title.desc())
        else:
            return jsonify({"message": f"invalid sort order '{dir}'"}), 400
    tasks = tasks.all()
    tasks_response = []
    for task in tasks:
        tasks_response.append(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            }
        )
    return jsonify(tasks_response)

@tasks_bp.route("/<task_id>", methods=["GET"])
def read_one_task(task_id):
    task = validate_task(task_id)
    return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            }
        }

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    task = validate_task(task_id)

    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return {
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete
            }
        }

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return make_response({"details": f"Task {task.id} \"{task.title}\" successfully deleted"})
