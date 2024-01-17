from django.urls import path
from .import views


urlpatterns=[
  path('register/',views.register,name='register'),
  path('login/',views.login,name='login'),
  path('logout/',views.logout,name='logout'),
  path('home1', views.home1, name='home1'),
  path('register/otp/<str:uid>/', views.otpVerify, name='otp'),
  path('resend_otp',views.resend_otp,name="resend_otp"),
  path('login/otp_login/<str:uid>/', views.otpVerify_login, name='otp_login'),
  path('resend_otp_login',views.resend_otp_login,name="resend_otp_login"),
  path('dashboard/',views.dashboard,name='dashboard'),
  path('login_admin',views.login_admin,name="login_admin"),
  path('dashboard_admin',views.dashboard_admin,name="dashboard_admin"),
  path('logout_admin',views.logout_admin,name="logout_admin"),
  path('forgot_password',views.forgot_passwrod,name="forgot_password"),
  path('users_list',views.users_list,name="users_list"),
  path('toggle_user_status/<int:user_id>/',views.toggle_user_status,name="toggle_user_status"),
  path('category_list/',views.category_list,name="category_list"),
  path('category_add',views.category_add,name="category_add"),
  path('category_update/<int:category_id>', views.category_update, name="category_update"),
  path('category_delete/<int:id>/', views.category_delete, name="category_delete"),
  path('product_list', views.product_list, name="product_list"),
  path('product_add', views.product_add, name="product_add"),
  path('product_update/<int:product_id>', views.product_update, name="product_update"),
  path('product_delete/<slug:id>', views.product_delete, name="product_delete"),
  path('variant_list', views.variant_list, name="variant_list"),
  path('variant_add', views.variant_add, name='variant_add'),
  path('variant_update/<int:variant_id>', views.variant_update, name="variant_update"),
  path('variant_delete/<int:variant_id>', views.variant_delete, name="variant_delete"),


]


