import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SLACK_BOT_TOKEN = "xoxb-1508568038180-1598251342835-KPgaUkYfXIQOHAJLBTw05Opy"
    SLACK_SIGNING_SECRET = "eae9ced30f0739139f8340e96e146b68"
    WS_URL = "https://saas.whitesourcesoftware.com"
    WS_API_URL = WS_URL + "/api/v1.3"
    WS_USER_KEY = "2fa240d4df9e49fe8a52fd2865b01a4bdaead5f26cf84f27852963adfcb8eddb"
    WS_ORG_TOKEN = "16830c25fcd543a289089bb076db4babeeaa874b9e6d49fb8a4ccbf3d222d808"
    CHANNEL_PREFIX = "ws_"
    REPORTS = {'fetch_lib_vulnerabilities'}


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
