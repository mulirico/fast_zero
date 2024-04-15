from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import TodoSchema, TodoPublic, TodoList, TodoUpdate, Message
from fast_zero.security import get_current_user


router = APIRouter()

router = APIRouter(prefix='/todos', tags=['todos'])

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TodoPublic)
def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session = Depends(get_session),
):
    db_todo: Todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(
    user: CurrentUser,
    session: Session = Depends(get_session),
    title: str = Query(None),
    description: str = Query(None),
    state: str = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))

    if description:
        query = query.filter(Todo.description.contains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {'todos': todos}


@router.patch('/{todo_id}', response_model=TodoPublic)
def patch_todo(
    todo_id: int, 
    user: CurrentUser,
    todo: TodoUpdate,
    session: Session = Depends(get_session),
):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(status_code=404, detail='Task not found.')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    todo_id: int,
    user: CurrentUser,
    session: Session = Depends(get_session),
):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(status_code=404, detail='Task not found.')
    
    session.delete(todo)
    session.commit()

    return {'message': 'Task has been deleted successfully.'}
