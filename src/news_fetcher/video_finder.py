from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta

from src.utils import config

class VideoFinder:
    def __init__(self, channels=config['yt-channels'], time_d=2, max_videos=None):
        self.channels = channels
        self.time_delta = timedelta(days=time_d)
        self.youtube_client = build(
'youtube',
    'v3',
            developerKey=config['youtube-api']['api-key']
        )

        if max_videos is not None:
            self.max_videos_per_channel = int(max_videos / len(self.channels))
        else:
            self.max_videos_per_channel = 50

    def get_videos(self):
        urls = []
        for channel in self.channels:
            try:
                request = self.youtube_client.channels().list(
                    part='contentDetails',
                    id=channel
                )
                response = request.execute()

                playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                playlist_items_response = self.youtube_client.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=self.max_videos_per_channel
                ).execute()

                results = playlist_items_response['items']
                for video in results:
                    video_date = datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
                    time_d = datetime.utcnow() - video_date
                    if time_d < timedelta(days=2):
                        video_id = video['snippet']['resourceId']['videoId']
                        video = {
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "ts": video_date
                        }
                        urls.append(video)
            except Exception as e:
                print(f'Error fetching videos for channel id {channel}: {e}')
                continue

        return urls