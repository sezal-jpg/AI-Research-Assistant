from pydantic import BaseModel
class QuestionRequest(BaseModel):
    question:str
    selected_pdf:str