from abc import ABC, abstractmethod
from app.models.news import News

class NewsCollector(ABC):

    @abstractmethod
    def collect(self) -> list[News]:
        return []