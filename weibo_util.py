from weibo import Client
from config import WEIBO_API_KEY, WEIBO_API_SECRECT

REDIRECT_URI = 'https://localhost:8080/'
c = Client(WEIBO_API_KEY, WEIBO_API_SECRET, REDIRECT_URI)