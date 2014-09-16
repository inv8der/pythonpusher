from django.conf import settings

if settings.DEBUG:
    # Development environment
    app_id = '88726'
    app_key = '1751ee3d48c493fa8347'
    app_secret = 'e332918120e6efe62095'
else:
    # Production enviroment (Heroku app)
    app_id = '88725'
    app_key    = '3dc3533a2828e91bd034'
    app_secret = '4fd4201ee58cba4d5ba3'