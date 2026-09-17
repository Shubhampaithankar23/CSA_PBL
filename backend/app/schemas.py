from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class StudentBase(BaseModel):
    student_id: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    course: str = Field(min_length=2, max_length=100)
    year: int = Field(ge=1, le=8)
    department: str = Field(min_length=2, max_length=100)


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
