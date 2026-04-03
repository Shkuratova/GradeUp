from services.base import BaseService
from db.repository.questions import QuestionRepository, question_repository_factory

class QuestionService(BaseService):
    entity_name = "Вопрос"
    unique_field = "num"


question_service = QuestionService(question_repository_factory)
