import logging
import sys

import constants
from web import WS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


if __name__ == '__main__':
    c_org = WS(api_url=constants.wss_api_url, user_key=constants.user_key1, token=constants.org_token1, token_type="organization")
    c_prod = WS(api_url=constants.wss_api_url, user_key=constants.user_key1, token=constants.prod_token1, token_type="product")
    c_proj = WS(api_url=constants.wss_api_url, user_key=constants.user_key1, token=constants.proj_token1, token_type="project")
    # tmp = c.get_vitals("product")
    # tmp = c.get_all_tokens()
    # tmp = c.get_alerts(report=True, token='a7d7184726f5447b889a418f810b66b46d048bf854214146bef1d318e545311a')
    #     # with open('c:/tmp/tmp.xlsx', 'wb') as f:
    #     #     f.write(tmp)
    # tmp = c.get_alerts()
    # tmp = c.get_alerts(token='a7d7184726f5447b889a418f810b66b46d048bf854214146bef1d318e545311a')
    # tmp = c_prod.get_all_products()
    # tmp = c_prod.get_alerts()
    tmp = c_org.get_all_projects()
    # tmp = c_org.get_all_projects(token=constants.prod_token1)
    tmp = c_prod.get_all_projects()
    # tmp = c_proj.get_all_projects()

    print("Done")
