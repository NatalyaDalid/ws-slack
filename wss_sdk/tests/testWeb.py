import unittest
from web.web import WSS

env = "saas-eu"
wss_api_url = f"https://{env}.whitesourcesoftware.com/api/v1.3"
user_key1 = "f30e540b46334b88942a24ac80d59693eb6a4ab52c354bc0a37a43ba284b603e"
org_token1 = "6172a79058e5452fa7a5856f78cd82d7a74b20b8064840ef826aae807b43254e"
prod_token1 = "a7d7184726f5447b889a418f810b66b46d048bf854214146bef1d318e545311a"
proj_token1 = "687de7108b634af6870a3d48612b895314dd641456994f91ac17db79fbc7525c"

c = WSS(api_url=wss_api_url, user_key=user_key1, token=org_token1, token_type="organization")


class TestWeb(unittest.TestCase):
    def test_create_body(self):
        res = c.create_body("api_call")
        self.assertIsInstance(res, dict)


if __name__ == '__main__':
    unittest.main()
