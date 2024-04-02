import asyncio

from src.news_fetcher.video_finder import VideoFinder
from src.news_fetcher.video_loader import VideoLoader
from src.utils import mongo_client, sources_collection


if __name__ == "__main__":
    vf = VideoFinder()
    videos = vf.get_videos()
    print(f"{len(videos)} videos found")

    vl = VideoLoader(videos)
    data = asyncio.run(vl.load())

    # for chunk in data:
    #     sources_collection.insert_chunk(chunk)


