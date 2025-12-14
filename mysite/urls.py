from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from games import views as games_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
    path("posts/", include("blog.urls")),
    path("communities/", include("communities.urls")),
    path("games/", include("games.urls")),
    path("recommend/", include("recommend.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("api/games", games_views.games_api_view, name="api_games"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
