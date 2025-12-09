from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path('account/', views.account_dashboard_view, name='account_dashboard'),

    # community subscription
    path(
        'toggle-subscription/<int:community_id>/',
        views.toggle_subscription,
        name='toggle_subscription'
    ),

    # author subscription
    path(
        'toggle-subscription/author/<int:author_id>/',
        views.toggle_subscription,
        name='toggle_subscription_author'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
