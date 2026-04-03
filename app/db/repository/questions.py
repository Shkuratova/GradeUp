from db.repository import BaseRepository
from db.models.skills import StageQuestion

class QuestionRepository(BaseRepository):
    model = StageQuestion

def question_repository_factory(session):
    return QuestionRepository(session)
