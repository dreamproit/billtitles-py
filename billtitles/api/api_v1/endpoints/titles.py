import os
import django

if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ["DJANGO_SETTINGS_MODULE"] = "billtitles.billtitles.settings"

django.setup()

from billtitleindex.btiapp.endpoints.titles import router as titles_router

for route in titles_router.routes:
    if route.tags:
        route.tags = []
router = titles_router
