from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from db import get_db_connection

app = FastAPI(title="Task Manager API")


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    conn = get_db_connection()
    now = datetime.now().isoformat()

    cursor = conn.execute(
        """
        INSERT INTO tasks (title, description, completed, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (task.title, task.description, False, now, now)
    )

    task_id = cursor.lastrowid
    conn.commit()

    new_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()
    return dict(new_task)



@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks():
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    conn = get_db_connection()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()
    conn.close()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return dict(task)

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated_task: TaskCreate):
    conn = get_db_connection()
    now = datetime.now().isoformat()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, updated_at = ?
        WHERE id = ?
        """,
        (updated_task.title, updated_task.description, now, task_id)
    )
    conn.commit()

    updated = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()
    return dict(updated)

@app.delete("/tasks/{task_id}", response_model=TaskResponse)
def delete_task(task_id: int):
    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )
    conn.commit()
    conn.close()

    return dict(task)

@app.patch("/tasks/{task_id}/completed", response_model=TaskResponse)
def mark_task_completed(task_id: int):
    conn = get_db_connection()
    now = datetime.now().isoformat()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.execute(
        """
        UPDATE tasks
        SET completed = ?, updated_at = ?
        WHERE id = ?
        """,
        (True, now, task_id)
    )
    conn.commit()

    updated = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    conn.close()
    return dict(updated)

@app.get("/tasks/completed", response_model=list[TaskResponse])
def get_completed_tasks():
    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE completed = 1"
    ).fetchall()
    conn.close()
    return [dict(task) for task in tasks]