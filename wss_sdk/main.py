import constants
from web import WSS

if __name__ == '__main__':
    c = WSS(api_url=constants.wss_api_url, user_key=constants.user_key1, token=constants.org_token1, token_type="organization")
    tmp = c.get_vitals("product")
    print(tmp)
