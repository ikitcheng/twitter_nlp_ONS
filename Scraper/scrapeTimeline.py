import yaml
import requests


def scrape_user_timeline(user, N):
    """
    Scrape the latest N posts from user timeline.
    Inputs: user (string)
            N (int)

    Output: tweet objects (https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object)
    """

    # twitter api endpoint
    url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

    params = dict(
        screen_name=user,
        count=N)
    
    with open('config.yaml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    token = cfg['bearerToken']
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url=url, params=params, headers=headers)
    data = resp.json()
    return data