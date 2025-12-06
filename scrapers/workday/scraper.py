from scrapers.apify.base import ApifyScraper
from scrapers.workday.schemas import Input, Job


class WorkdayScraper(ApifyScraper):
    async def get_jobs(self) -> list[Job]:
        run_input = Input(startUrls=self.urls)
        run = await self.apify_client.actor('kma98hS67qBkPC6ub').call(
            run_input=run_input.model_dump()
        )
        items = (
            await self.apify_client.dataset(run['defaultDatasetId']).list_items()
        ).items
        return [Job.model_validate(item) for item in items]
