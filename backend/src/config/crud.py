from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from config import model, schema, security

#-------------------CREATE USER--------------------------
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(model.Users).filter(model.Users.username == username)
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schema.UserCreate):
    hashed_password = security.get_password_hash(user.password)

    # Create the new database model object
    db_user = model.Users(
        username=user.username,
        password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

#--------------------TASK CREATE -----------------------------


async def create_task(db: AsyncSession, task: schema.TaskCreate, owner_id: int):
    # Create the database model object
    db_task = model.Tasks(
        title=task.title,
        description=task.description,
        owner_id=owner_id # Id passed into the function
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

# List tasks by owner

async def get_tasks_by_owner(db: AsyncSession, owner_id: int):
    result = await db.execute(
        select(model.Tasks).filter(model.Tasks.owner_id==owner_id)
    )
    return result.scalars().all()

async def get_task_by_id_and_owner(db: AsyncSession, task_id: int, owner_id: int):
    """
    Fetches a single task by its ID, ensuring it belongs to the correct owner.
    """
    result = await db.execute(
        select(model.Tasks)
        .filter(model.Tasks.id == task_id)
        .filter(model.Tasks.owner_id == owner_id)
    )
    # .scalar_one_or_none() is the best way to get one item or None
    return result.scalar_one_or_none()


# Delete a task

async def delete_task(db: AsyncSession, task_id: int, owner_id: int):
    
    # 1. Fetch the task and verify ownership in one step
    db_task = await get_task_by_id_and_owner(db, task_id=task_id, owner_id=owner_id)

    if db_task is None:
        return None

    await db.delete(db_task)
    await db.commit()
    return db_task


# update a task
async def update_task(db: AsyncSession, task_id: int, owner_id: int, task_data: schema.TaskUpdate):

    db_task = await get_task_by_id_and_owner(db, task_id=task_id, owner_id=owner_id)

    if db_task is None:
        return None
    
    update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_task, key, value)

    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task