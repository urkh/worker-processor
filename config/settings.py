import environ
import sentry_sdk

BASE_DIR = environ.Path(__file__) - 1

env = environ.Env()
env.read_env(BASE_DIR('.env'))

ENVIRONMENT = env('ENVIRONMENT')

RABBIT_URL = env.str('RABBIT_URL')
DB_NAME = env.str('DB_NAME')
DB_USER = env.str('DB_USER')
DB_PASSWORD = env.str('DB_PASSWORD')
DB_HOST = env.str('DB_HOST')
DB_PORT = env.str('DB_PORT')

RESPONSE_QUEUE = env.str('RESPONSE_QUEUE')


if ENVIRONMENT in ['prd']:
    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=ENVIRONMENT,
    )
