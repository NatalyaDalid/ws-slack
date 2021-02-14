import logging
import sys

import constants
from web import WS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


if __name__ == '__main__':
    c = WS(api_url=constants.wss_api_url, user_key=constants.user_key1, token=constants.org_token1, token_type="organization")
    tmp = c.get_vitals("product")
    tmp = c.get_all_tokens()
    tmp = c.get_alerts(report=True, token='a7d7184726f5447b889a418f810b66b46d048bf854214146bef1d318e545311a')
        # with open('c:/tmp/tmp.xlsx', 'wb') as f:
        #     f.write(tmp)
    tmp = c.get_alerts()
    tmp = c.get_alerts(token='a7d7184726f5447b889a418f810b66b46d048bf854214146bef1d318e545311a')
    # print(tmp)
