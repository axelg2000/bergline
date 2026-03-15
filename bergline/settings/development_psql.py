from bergline.settings import *  # noqa: F401,F403

DATABASES = {
    "default": env.db("DATABASE_URL"),
}
