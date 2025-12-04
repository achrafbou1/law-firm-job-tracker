from scrapers.apify import ApifyScraper


class WorkDay(ApifyScraper):
    def run(self):
        actor_client = self.apify_client.actor('gooyer.co/myworkdayjobs')
        input_data = {'hashtags': ['rainbow'], 'resultsLimit': 20}