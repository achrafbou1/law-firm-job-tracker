from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Iterable


@dataclass
class EmailProvider(ABC):
    username: str
    password: str

    @abstractmethod
    def send(
        self,
        *,
        to: Iterable[str],
        subject: str,
        body: str
    ) -> None:
        pass
