class Config:
    '''This is a class for the configuration settings'''
    SECRET_KEY = '5f850afc4593b246cf6b30f4c081fb06'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'root'
    MAIL_PASSWORD = ''
