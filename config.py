class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'db-cib.cwy4hbuwhvsr.us-east-1.rds.amazonaws.com'
    MYSQL_USER = 'admin'
    MYSQL_PASSWORD = 'database_cib'
    MYSQL_DB = 'db_cib'
    SECRET_KET = 'test'

config = {
    'development' : DevelopmentConfig
}