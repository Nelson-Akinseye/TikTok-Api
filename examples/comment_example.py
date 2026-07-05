from TikTokApi import TikTokApi
import asyncio
import os
video_id = 7644970264945528096
ms_token = os.environ.get("ms_token",None) # "lVb7l-a0ye9y3a74ilXDbxPQIp9JXrHEsinNMWa9SEU47vkk94vvZWBNRNfCzkh4qqtiAgD-fXYWA6arF1MYE9VvPI3Pt4J5M2BB01il8SUB_bfstct5OHGqDJQMfWl0lYZbP-vBZLp3Fg==")

async def get_comments():
    async with TikTokApi() as api:
        print("Token:", ms_token)
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser="firefox",
            headless=False
        )
        video = api.video(id=video_id)
        # count = 0
        count = 1
        try:
            async for comment in video.comments(300):
                
                data = comment.as_dict
                print(f"comment:{data["text"]}")
                print(count)
                count+=1

                # print(f"commentLikes:{data["digg_count"]}")
                # print(nn)
                
        except Exception as e:
            print("failed")
            print(e)

if __name__ == "__main__":
    asyncio.run(get_comments())
