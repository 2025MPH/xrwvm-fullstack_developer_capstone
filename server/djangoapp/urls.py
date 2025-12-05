from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.generic import TemplateView

app_name = 'djangoapp'

urlpatterns = [
    # Login/logout
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_request, name='logout'),

    # Cars
    path('get_cars/', views.get_cars, name='getcars'),

    # Dealerships
    path('get_dealers/', views.get_dealerships, name='get_dealers'),  # trailing slash
    path('get_dealers/<str:state>/', views.get_dealerships, name='get_dealers_by_state'),
    path('dealer/<int:dealer_id>/', views.get_dealer_details, name='dealer_details'),
    path('reviews/dealer/<int:dealer_id>/', views.get_dealer_reviews, name='dealer_reviews'),

    # Add review
    path('add_review/', views.add_review, name='add_review'),

    # Route for React frontend to handle /dealers page
    path('dealers/', TemplateView.as_view(template_name="index.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
