from pydantic import BaseModel


class PersonPostRequest(BaseModel):
    name: str
    age: int | None = None
    address: str | None = None
    work: str | None = None


class PersonResponse(BaseModel):
    id: int
    name: str
    age: int | None = None
    address: str | None = None
    work: str | None = None


class ErrorResponse(BaseModel):
    message: str


class ValidationErrorResponse(BaseModel):
    message: str
    errors: dict[str, str]