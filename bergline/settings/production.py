from bergline.settings import *  # noqa: F401,F403

DEBUG = False

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
