import requests
from operator import itemgetter
from modules.user_agents import get_agent
# from user_agents import get_agent


def get_entries(current_entry):
    query = """
        query PublicPosts {
            getPublicPosts(page: 1) {
                posts {
                    id
                    type
                    source_name
                    timestamp
                    en_title
                    featured_image_url
                    en_readmore_link
                    primary_rating
                    en_description
                    verification_url
                }
            }
        }
    """

    data = requests.post('https://appendix-watchdog-api.herokuapp.com/graphql', headers=get_agent(), json={'query': query})

    # return if data isn't returned
    if (data.status_code != 200 or data.json()['data']['getPublicPosts']['posts'] == []):
        return

    # remove older entries
    entries = [entry for entry in data.json()['data']['getPublicPosts']['posts'] if int(entry['id']) > current_entry]

    return entries