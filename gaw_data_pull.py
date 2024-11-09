import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def fetch_keyword_data(credentials_dict, customer_id, location_ids, language_id, page_url):
    """
    Fetch keyword ideas and return the results as a DataFrame.
    
    Args:
        credentials_dict (dict): Google Ads API credentials.
        customer_id (str): Customer ID of the test account.
        location_ids (list): List of location IDs.
        language_id (str): Language criterion ID.
        page_url (str): URL seed for generating keyword ideas.
    
    Returns:
        DataFrame: Contains keyword data including search volume and bid ranges.
    """
    try:
        client = GoogleAdsClient.load_from_dict(credentials_dict, version="v18")

        # KeywordPlanIdeaService
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

        # Create request
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = client.get_service("GoogleAdsService").language_constant_path(language_id)
        request.geo_target_constants.extend([
            client.get_service("GeoTargetConstantService").geo_target_constant_path(location_id)
            for location_id in location_ids
        ])
        request.url_seed.url = page_url

        # Fetch keyword ideas
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

        # Collect data
        data = []
        for idea in response:
            metrics = idea.keyword_idea_metrics
            data.append({
                "Keyword": idea.text,
                "Avg Monthly Searches": metrics.avg_monthly_searches,
                "Competition": metrics.competition.name,
                "Low Top of Page Bid (micros)": metrics.low_top_of_page_bid_micros,
                "High Top of Page Bid (micros)": metrics.high_top_of_page_bid_micros
            })

        # Convert to DataFrame
        return pd.DataFrame(data)

    except GoogleAdsException as ex:
        print(f"GoogleAdsException occurred: {ex}")
        return pd.DataFrame()  # Return an empty DataFrame on failure
