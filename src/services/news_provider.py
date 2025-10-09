# ... existing code in EventRegistryProvider class

    def fetch_raw_articles(self, start_date: datetime, end_date: datetime) -> list:
        """
        Fetches the raw, unmodified article data from Event Registry.

        Args:
            start_date: The start date for the article search.
            end_date: The end date for the article search.

        Returns:
            A list of dictionaries, where each dictionary is the raw article data.
        """
        q = QueryArticlesIter(
            conceptUri=self.er.getConceptUri("Bitcoin"),
            sourceUri=self.er.getConceptUri("Bitcoin"),
            dateStart=start_date.strftime("%Y-%m-%d"),
            dateEnd=end_date.strftime("%Y-%m-%d"),
            lang="eng",
            sortBy="date"
        )
        # Directly return the list of article data
        return list(q.execQuery(self.er, returnInfo=self.return_info))

# ... rest of the file
