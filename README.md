# Law Firm Job Scraper

A Python-based automation tool that scrapes job listings from law firm career pages, tracks changes, stores data in Airtable, and sends email notifications for new and closed positions.

## Features

- 🔍 **Automated Job Scraping** – Scrapes job listings from law firm career pages using Apify actors
- 📊 **Airtable Integration** – Stores and manages job listings in an Airtable database
- 📧 **Email Notifications** – Sends daily summaries of new and closed job positions via SendGrid
- 🔄 **Diff Tracking** – Detects new, closed, and existing job postings
- ⏰ **Scheduled Execution** – Runs on a configurable schedule using APScheduler
- 🎯 **Keyword Filtering** – Filters jobs by role categories and keywords
- 🌍 **Location Filtering** – Filters jobs by country (default: United States)

## Supported ATS Platforms

| Platform   | Status | Apify Actor |
|------------|--------|-------------|
| Workday    | ✅ Supported | `kma98hS67qBkPC6ub` |
| Greenhouse | ✅ Supported | `jupri/greenhouse` |

## Architecture

```
law-firm-job-scraper/
├── src/
│   ├── main.py                 # Entry point & scheduler
│   ├── settings.py             # Configuration & environment settings
│   ├── constants.py            # Centralized constants (timezone, etc.)
│   ├── exceptions.py           # Custom exceptions
│   ├── factories.py            # Scraper factory with registry pattern
│   └── services/
│       ├── airtable/           # Airtable API service
│       │   ├── client.py       # Airtable API client
│       │   └── models/         # ORM models (JobListing, LawFirm, RoleCategory)
│       ├── email/              # Email service
│       │   ├── provider.py     # Abstract email provider
│       │   ├── service.py      # SendGrid implementation
│       │   └── templates/      # Email HTML templates
│       └── scrapers/           # Scraping service
│           ├── base.py         # Abstract base scraper
│           ├── filters.py      # Post-processing filters
│           ├── ats/            # ATS-specific implementations
│           │   ├── base.py           # Apify-based scraper base
│           │   ├── apify_provider.py # Apify client singleton
│           │   ├── workday.py        # Workday scraper
│           │   └── greenhouse.py     # Greenhouse scraper
│           └── schemas/        # Pydantic schemas for API responses
│               ├── workday.py
│               └── greenhouse.py
├── tests/
│   ├── conftest.py             # Shared pytest fixtures
│   ├── test_diff_check.py      # Main test file
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── data/                   # Test data (CSV files)
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- Airtable account with configured tables
- Apify account with API key
- SendGrid account for email notifications

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/law-firm-job-scraper.git
   cd law-firm-job-scraper
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root:
   ```env
   AIRTABLE_TOKEN=your_airtable_api_token
   APIFY_API_KEY=your_apify_api_key
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDER_EMAIL=sender@example.com
   RECEIVER_EMAIL=receiver@example.com
   ```

## Airtable Setup

The application requires the following Airtable tables:

### Law Firms Table
| Field Name   | Field Type       | Description                    |
|--------------|------------------|--------------------------------|
| Law Firm Name| Single line text | Name of the law firm           |
| Active       | Checkbox         | Whether to scrape this firm    |
| Careers URL  | URL              | Link to the careers page       |
| ATS Type     | Single select    | ATS platform (e.g., "Workday") |
| Schedule     | Single line text | Cron schedule (optional)       |
| Last Checked | Date             | Last scrape timestamp          |

### Job Listings Table
| Field Name    | Field Type        | Description                      |
|---------------|-------------------|----------------------------------|
| Job ID        | Single line text  | Unique job identifier            |
| Job Title     | Single line text  | Position title                   |
| Firm          | Single line text  | Law firm name                    |
| Location      | Single line text  | Job location                     |
| Country       | Single line text  | Country of the job               |
| Job URL       | URL               | Link to the job posting          |
| Status        | Single select     | NEW, OLD, or CLOSED              |
| Role Category | Multiple select   | Job categories                   |
| First Seen    | Date              | When the job was first detected  |
| Last Seen     | Date              | When the job was last detected   |
| Actioned      | Checkbox          | Whether the job has been reviewed|

### Role Categories Table
| Field Name   | Field Type       | Description                    |
|--------------|------------------|--------------------------------|
| ATS Keywords | Single line text | Comma-separated keywords       |

## Usage

### Run Once (Development)
```bash
make dev
# or
python src/main.py --once
```

### Run Scheduler (Production)
```bash
make run
# or
python src/main.py
```

### Docker

**Build the image:**
```bash
make build
# or
docker build . -t scraper-image
```

**Run the container:**
```bash
make run
# or
docker run scraper-image
```

### Run Tests
```bash
make test
# or
pytest -v
```

### Linting
```bash
make lint
```

## How It Works

1. **Fetch Configuration** – Retrieves active law firms and keywords from Airtable
2. **Scrape Jobs** – Uses Apify actors to scrape job listings from each firm's career page
3. **Diff Check** – Compares new jobs against previously stored jobs:
   - New jobs are marked as `NEW`
   - Existing jobs are marked as `OLD`
   - Missing jobs are marked as `CLOSED`
4. **Filter Jobs** – Applies filters based on status, keywords, and country
5. **Send Notifications** – Emails a summary of new and closed positions
6. **Update Database** – Upserts job listings to Airtable

## Configuration

| Environment Variable | Description                        | Required |
|---------------------|------------------------------------|----------|
| `AIRTABLE_TOKEN`    | Airtable personal access token     | Yes      |
| `APIFY_API_KEY`     | Apify API key                      | Yes      |
| `SENDGRID_API_KEY`  | SendGrid API key                   | Yes      |
| `SENDER_EMAIL`      | Email address for sending          | Yes      |
| `RECEIVER_EMAIL`    | Email address for receiving        | Yes      |
| `LAW_FIRM_DB_ID`    | Airtable base ID (has default)     | No       |
| `RUN_ONCE`          | Set to `1` to run once and exit    | No       |
| `ENV`               | Set to `test` for test environment | No       |

## Testing

The project includes comprehensive unit and integration tests organized as follows:

```
tests/
├── conftest.py                 # Shared pytest fixtures
├── test_diff_check.py          # Legacy tests for diff check, filters, email
├── unit/
│   ├── test_factory.py         # Factory pattern tests
│   ├── test_schemas.py         # Pydantic schema validation tests
│   ├── test_base_scraper.py    # Base scraper URL validation tests
│   ├── test_constants.py       # Constants verification
│   └── test_apify_provider.py  # Singleton client tests
├── integration/
│   └── test_workday_scraper.py # Full workflow tests with mocks
└── data/
    ├── old_workdayjobs.csv     # Test data
    └── new_workdayjobs.csv
```

### Running Tests

```bash
# Run all tests
make test
# or
uv run pytest tests/ -v

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Test Categories

| Category | Description |
|----------|-------------|
| **Unit Tests** | Test individual components in isolation (schemas, factory, base classes) |
| **Integration Tests** | Test component interactions with mocked external services (Apify, Airtable) |
| **Filter Tests** | Test job filtering by status, keywords, and country |
| **Email Tests** | Test email template rendering and SendGrid integration |
| **Diff Check Tests** | Test job status detection (NEW, OLD, CLOSED) |

## Dependencies

- **apify-client** – Apify API client for running actors
- **apscheduler** – Job scheduling
- **pyairtable** – Airtable ORM
- **pydantic** – Data validation
- **pydantic-settings** – Settings management
- **sendgrid** – Email delivery
- **tenacity** – Retry logic
- **loguru** – Logging

## Development

### Adding a New ATS Scraper

1. Create a new scraper file under `src/services/scrapers/ats/`
2. Create a schema file under `src/services/scrapers/schemas/` if needed
3. Implement a scraper class extending `ApifyScraper` or `BaseScraper`
4. Add the ATS type to `src/services/airtable/models/law_firm.py`
5. Register the scraper in `src/factories.py`

Example:
```python
# src/services/scrapers/ats/greenhouse.py
from src.services.scrapers.ats.base import ApifyScraper

class GreenhouseScraper(ApifyScraper):
    ACTOR_ID = 'your-actor-id'

    async def get_new_jobs(self) -> None:
        # Implementation
        pass

    def get_previous_jobs(self) -> None:
        # Implementation
        pass

    def diff_check(self) -> list[JobListing]:
        # Implementation
        pass
```

Then register it:
```python
# src/factories.py
SCRAPER_REGISTRY: dict[AtsType, Type[BaseScraper]] = {
    AtsType.WORKDAY: WorkdayScraper,
    AtsType.GREENHOUSE: GreenhouseScraper,  # Add new scraper
}
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-ats-support`)
3. Commit your changes (`git commit -am 'Add Greenhouse ATS support'`)
4. Push to the branch (`git push origin feature/new-ats-support`)
5. Create a Pull Request
