import os
import json

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

from person import Person
from models import PersonResponse, PersonPostRequest, ErrorResponse, ValidationErrorResponse

DB_CONNECTOR = os.environ.get("DB_CONNECTOR", "")
engine = create_engine(DB_CONNECTOR)

app = FastAPI()

@app.get(
    "/api/v1/persons",
    response_model=list[PersonResponse]
)
def get_persons_list():
    query = select(Person)
    with Session(engine) as session:
        persons = session.scalars(query).all()
    return persons

@app.get(
    "/api/v1/persons/{person_id}",
    response_model=PersonResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Not found Person for ID",
        }
    }
)
def get_persons_list(person_id: int):
    with Session(engine) as session:
        person = session.get(Person, person_id)
    if person is None:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Пользователь не найден"
                }
            )
    result = PersonResponse(
            id=person.id,
            name=person.name,
            age=person.age,
            address=person.address,
            work=person.work
        )
    return result

@app.post(
    "/api/v1/persons",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Created new Person",
            "headers": {
                "Location": {
                    "description": "Path to new Person",
                    "schema": {
                        "type": "string"
                    },
                }
            },
        },
        400: {
            "model": ValidationErrorResponse,
            "description": "Invalid data",
        },
    }
)
def create_person(body: PersonPostRequest):
    get_next_id = select(
        (func.coalesce(func.max(Person.id), 0) + 1)
    )
    with Session(engine) as session:
        next_id = session.scalar(get_next_id)

        new_person = Person(
            id=next_id,
            name=body.name,
            age=body.age,
            address=body.address,
            work=body.work
        )
        session.add(new_person)
        session.commit()
    return Response(
        status_code=status.HTTP_201_CREATED,
        headers={
            "Location": f"/api/v1/persons/{next_id}"
        }
    )

@app.patch(
    "/api/v1/persons/{person_id}",
    response_model=PersonResponse,
    responses={
        400: {
            "model": ValidationErrorResponse,
            "description": "Invalid data",
        },
        404: {
            "model": ErrorResponse,
            "description": "Not found Person for ID",
        },
    },
)
def update_person(person_id: int, body: PersonPostRequest):
    with Session(engine) as session:
        person = session.get(Person, person_id)

        if person is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "message": "Пользователь не найден"
                },
            )

        data = body.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(person, field, value)

        session.commit()
        session.refresh(person)

        return person

@app.delete(
    "/api/v1/persons/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_person(id: int):
    with Session(engine) as session:
        person = session.get(Person, id)

        if person is not None:
            session.delete(person)
            session.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = {}

    for error in exc.errors():
        location = error["loc"]

        field = ".".join(
            str(item)
            for item in location
            if item != "body"
        )

        errors[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "message": "Invalid data",
            "errors": errors,
        },
    )