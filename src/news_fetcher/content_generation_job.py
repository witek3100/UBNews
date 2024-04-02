
from src.news_fetcher.video_finder import VideoFinder
from src.news_fetcher.video_loader import VideoLoader
from src.utils import mongo_client


vf = VideoFinder()
videos = vf.get_videos()

vl = VideoLoader([{'url': 'https://www.youtube.com/watch?v=pn-dD5BzPLY', 'ts': '2020-05-27T14'}])
data = vl.load()