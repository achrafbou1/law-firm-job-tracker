from abc import abstractmethod, ABC


class EmailProvider(ABC):
    @abstractmethod
    def send_jobs_email(self, body: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_job_listings_summary(self, job_listings: list) -> str:
        raise NotImplementedError
