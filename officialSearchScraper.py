from TikTokApi import TikTokApi
import asyncio
import os
import datetime
import csv

video_id = ""
ms_token = os.environ.get("ms_token", None) 
searchBar = input("Type Search Term or Phrase: ")
amountOfVideos = int(input("Type in Amount of Videos to Scrape: "))
amountofComments = int(input("Type in Amount of Comments from Each Video to Scrape (Minimum 20): "))

async def dopamineSearch():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "firefox"),
            headless=False
        )
        with open("dopamine.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "video_id",
                "video_url",
                "caption",
                "post_creation_date",
                "time_collected",
                "username",
                "display_name",
                "likes",
                "comments",
                "bookmarks",
                "shares",
                "views",
                "hashtags"
            ])
       
            async for vids in api.search.vids(searchBar,amountOfVideos):
                data = vids.as_dict
                video_id = data.get("id")
                writer.writerow([
                data.get("id"),
                f"https://www.tiktok.com/@{data.get('author', {}).get('uniqueId')}/video/{data.get('id')}",
                data.get("desc"),
                datetime.datetime.fromtimestamp(data.get("createTime")),
                datetime.datetime.now(),
                data.get("author", {}).get("uniqueId"),
                data.get("author", {}).get("nickname"),
                data.get("stats", {}).get("diggCount"),
                data.get("stats", {}).get("commentCount"),
                data.get("stats", {}).get("collectCount"),
                data.get("stats", {}).get("shareCount"),
                data.get("stats", {}).get("playCount"),
                "|".join(
                    tag.get("hashtagName")
                    for tag in data.get("textExtra", [])
                    if tag.get("hashtagName") )])

                with open("comments.csv", "a", newline="", encoding="utf-8") as file1:
                    writer1 = csv.writer(file1)
                    writer1.writerow([
                    "VIDEO ID"
                    "comment_text",
                    "comment_username",
                    "comment_creation_date",
                    "comment_likes"
                ])
                    async for comment in api.video(video_id).comments(amountofComments):
                        dataC = comment.as_dict
                        writer1.writerow([
                        video_id,
                        dataC.get("text"),
                        dataC.get("user", {}).get("unique_id"),
                        datetime.datetime.fromtimestamp(dataC.get("create_time")),
                        dataC.get("digg_count")
                    
                        ])
                

if __name__ == "__main__":
    asyncio.run(dopamineSearch())
