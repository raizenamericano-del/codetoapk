from .auto_chat import AutoChatHandler
from .commands import CommandHandler
from .downloader import DownloaderHandler
from .music import MusicHandler
from .weather import WeatherHandler
from .reminder import ReminderHandler
from .sticker import StickerHandler
from .games import GamesHandler
from .admin import AdminHandler

__all__ = ['AutoChatHandler','CommandHandler','DownloaderHandler','MusicHandler',
           'WeatherHandler','ReminderHandler','StickerHandler','GamesHandler','AdminHandler']
