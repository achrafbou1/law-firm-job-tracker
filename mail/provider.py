from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class EmailProvider(ABC):
    username: str
    password: str

    @abstractmethod
    def send_jobs_email(
            self,
            to: str,
            body: str
    ) -> None:
        raise NotImplementedError
