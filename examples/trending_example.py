from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", None)  # set your own ms_token


async def trending_videos():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "webkit"),
            headless=False

        )
        async for video in api.trending.videos(count=30):
           data = video.as_dict
           stats = data["stats"]

           print("Views:", stats["playCount"])
           print("Likes:", stats["diggCount"])
           print("Comments:", stats["commentCount"])
           print("Shares:", stats["shareCount"])
           print("ID:", video.id)

if __name__ == "__main__":
    asyncio.run(trending_videos())
