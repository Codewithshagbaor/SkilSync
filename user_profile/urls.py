from .views import ConnectWalletView, ProfileView, JobPreferencesView, UserSocialProfileAnalyticsView,UserJobMatcherView

from django.urls import path

urlpatterns = [
    path("connect/", ConnectWalletView.as_view(), name="connect_wallet"),
    # path("get-nonce/", GetNonceView.as_view(), name="get_nonce"),
    path("disconnect/", ConnectWalletView.as_view(), name="disconnect_wallet"),
    path("wallet-status/", ConnectWalletView.as_view(), name="wallet_status"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("update-profile/", ProfileView.as_view(), name="update_profile"),
    path("job-preferences/", JobPreferencesView.as_view(), name="job_preferences"),
    path("update-job-preferences/", JobPreferencesView.as_view(), name="update_job_preferences"),
    path("social-profile-analytics/<str:provider>/", UserSocialProfileAnalyticsView.as_view(), name="social_profile_analytics"),
    path("job-matcher/", UserJobMatcherView.as_view(), name="job_matcher"),
]