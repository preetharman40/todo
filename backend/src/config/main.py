from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from config.database import create_db_tables, get_session
from config import schema, crud, security, dependencies

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating Database and Tables...")
    await create_db_tables()
    yield
    print("ShutDown: Closing Database Connection")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Todo API is running"}

@app.post("/register", response_model=schema.User)
async def register_user(user_data: schema.UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Create a new user account
    """
    db_user = await crud.get_user_by_username(db=db, username=user_data.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    new_user = await crud.create_user(db=db, user=user_data)
    return new_user

@app.post("/login", response_model=schema.Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """
    User login function
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


    db_user = await crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user or not security.verify_password(plain_password=form_data.password, hashed_password=db_user.password):

        raise credentials_exception
    
    access_token = security.create_access_token(data={"sub":db_user.username})

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/tasks", response_model=list[schema.Task])
async def list_tasks(current_user: schema.User = Depends(dependencies.get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Fetches all taks for the currently logged-in user
    """
    owner_id = current_user.id
    tasks = await crud.get_tasks_by_owner(db=db, owner_id=owner_id)
    
    return tasks

@app.post("/tasks", response_model=schema.Task)
async def create_task(task: schema.TaskCreate ,current_user: schema.User = Depends(dependencies.get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Create new task for logged in user
    """

    owner_id = current_user.id
    create_task = await crud.create_task(db=db, task=task, owner_id=owner_id)

    return create_task
    
@app.put("/tasks/{task_id}", response_model=schema.Task)
async def update_task(task_id: int, task_data: schema.TaskUpdate, current_user: schema.User = Depends(dependencies.get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Update a task of a logged in user
    """
    owner_id = current_user.id
    updated_task = await crud.update_task(db=db, task_id=task_id, owner_id=owner_id, task_data=task_data)

    if updated_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to update it"
        )

    return updated_task

@app.delete("/tasks/{task_id}", response_model=schema.Task)
async def delete_task(task_id: int, current_user: schema.User = Depends(dependencies.get_current_user), db: AsyncSession = Depends(get_session)):
    """
    Delete task belongs to logged in user
    """

    owner_id = current_user.id
    deleted_task = await crud.delete_task(db=db, task_id=task_id, owner_id=owner_id)

    if deleted_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you do not have permission to delete it"
        )

    return deleted_task
