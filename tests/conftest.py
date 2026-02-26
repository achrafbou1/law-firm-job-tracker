"""Shared pytest fixtures for all tests."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, create_autospec

import pytest
from apify_client import ApifyClientAsync
from apify_client.clients.resource_clients import ActorClientAsync, DatasetClientAsync

from src.services.airtable.models.job_listing import JobListing


@pytest.fixture
def sample_job() -> JobListing:
    """Create a minimal JobListing for unit tests."""
    return JobListing(
        job_id='TEST-001',
        job_title='Associate',
        firm='Test Firm',
        url='https://example.com/jobs/1',
        location='New York',
        country='United States of America',
    )


@pytest.fixture
def make_job():
    """Factory fixture to create JobListing instances with custom values."""
    def _make_job(
        job_id: str,
        title: str = 'Test Job',
        country: str = 'United States of America',
        status: str | None = None
    ) -> JobListing:
        job = JobListing(
            job_id=job_id,
            job_title=title,
            firm='Test Firm',
            url=f'https://example.com/jobs/{job_id}',
            location='New York',
            country=country,
        )
        if status:
            job.status = status
        return job
    return _make_job


@pytest.fixture
def mock_apify_client():
    """Factory fixture that builds an autospecced ApifyClientAsync.

    Usage:
        client = mock_apify_client(items=[...])
        scraper.apify_client = client
    """
    def _build(items: list[dict]) -> ApifyClientAsync:
        client = create_autospec(ApifyClientAsync, instance=True)

        mock_actor = create_autospec(ActorClientAsync, instance=True)
        mock_actor.call = AsyncMock(return_value={'defaultDatasetId': 'ds-1'})
        client.actor.return_value = mock_actor

        mock_dataset = create_autospec(DatasetClientAsync, instance=True)
        mock_dataset.list_items = AsyncMock(
            return_value=SimpleNamespace(items=items)
        )
        client.dataset.return_value = mock_dataset

        return client

    return _build
