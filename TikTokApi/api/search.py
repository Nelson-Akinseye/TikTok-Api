from __future__ import annotations
from urllib.parse import urlencode
from typing import TYPE_CHECKING, AsyncIterator
from .user import User
from ..exceptions import InvalidResponseException
from playwright.async_api import async_playwright

if TYPE_CHECKING:
    from ..tiktok import TikTokApi


class Search:
    """Contains static methods about searching TikTok for a phrase."""

    parent: TikTokApi

    @staticmethod
    async def users(search_term, count=10, cursor=0, **kwargs) -> AsyncIterator[User]:
        """
        Searches for users.

        Note: Your ms_token needs to have done a search before for this to work.

        Args:
            search_term (str): The phrase you want to search for.
            count (int): The amount of users you want returned.

        Returns:
            async iterator/generator: Yields TikTokApi.user objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for user in api.search.users('david teather'):
                    # do something
        """
        async for user in Search.search_type(
            search_term, "user", count=count, cursor=cursor, **kwargs
        ):
            yield user

    @staticmethod
    async def vids(search_term, count=100, cursor=0, **kwargs) -> AsyncIterator[Video]:
        """
        Searches for users.

        Note: Your ms_token needs to have done a search before for this to work.

        Args:
            search_term (str): The phrase you want to search for.
            count (int): The amount of users you want returned.

        Returns:
            async iterator/generator: Yields TikTokApi.user objects.

        Raises:
            InvalidResponseException: If TikTok returns an invalid response, or one we don't understand.

        Example Usage:
            .. code-block:: python

                async for user in api.search.users('david teather'):
                    # do something
        """
        async for video in Search.search_type(
            search_term, "item", count=count, cursor=cursor, **kwargs
        ):
            yield video

    @staticmethod
    async def search_type(
        search_term, obj_type, count=100, cursor=0, **kwargs
    ) -> AsyncIterator:
   
        found = 0
        search_id = ""
        while found <= count:
            params = {
                "keyword": search_term,
                "cursor": cursor,
                "from_page": "search",
                "offset": cursor,
                "device_platform": "web_pc",
                "region": "US",
                "tz_name": "America/Indianapolis",
                "screen_height": 1050,
                "screen_width": 1680,
                "cookie_enabled": "true",
                "data_collection_enabled": "false",
                "user_is_login": "false",
                "webcast_language": "en",
                "web_search_code": """{"tiktok":{"client_params_x":{"search_engine":{"ies_mt_video_live_video_card_use_libra":1,"mt_search_general_video_live_card":1}},"search_server":{}}}""",
            }

            if search_id != "":
                params["search_id"] = search_id
               
            
      
            resp = await Search.parent.make_request(
                url=f"https://www.tiktok.com/api/search/general/full/",
                #url=f"https://www.tiktok.com/api/search/{obj_type}/full/",
                params=params,
                headers=kwargs.get("headers"),
                session_index=kwargs.get("session_index"),
            )  

            if resp is None:
                raise InvalidResponseException(
                    resp, "TikTok returned an invalid response."
                )
          
           
            if obj_type == "user":
                for user in resp.get("user_list", []):
                    sec_uid = user.get("user_info").get("sec_uid")
                    uid = user.get("user_info").get("user_id")
                    username = user.get("user_info").get("unique_id")
                    yield Search.parent.user(
                        sec_uid=sec_uid, user_id=uid, username=username
                    )
                
            elif obj_type == "item":

                for x in resp.get("data", []):

                    if x.get("type") != 1:
                        continue

                    video = x.get("item")

                    if video is None:
                        continue

                    yield Search.parent.video(data=video)
                    found += 1
             
            if not resp.get("has_more", False):
                return

            cursor = resp.get("cursor")
            search_id = resp.get("rid", "")
          
