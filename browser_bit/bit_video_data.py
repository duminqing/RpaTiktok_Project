import asyncio
import time

from .bit_api import *


async def video_data(playwright, **kwargs):
    browser_id = kwargs.get("pad_code")
    res = openBrowser(browser_id)
    ws = res["data"]["ws"]
    print(f"Browser {browser_id} - ws address ==>>> {ws}")

    chromium = playwright.chromium
    browser = await chromium.connect_over_cdp(ws)
    default_context = browser.contexts[0]
    page = await default_context.new_page()
    tiktok_account = kwargs.get("tiktok_account")
    # 监听API请求
    page.on("response", lambda response: handle_api_response(response, tiktok_account))

    try:
        # 打开目标TikTok页面
        await page.goto(f"https://www.{tiktok_account}", timeout=60000)
        print("Successfully navigated to the TikTok profile")
        # 可能需要等待页面加载完成
        await page.wait_for_load_state("networkidle")
        # 这里可以添加滚动逻辑来触发更多视频加载
        await scroll_and_collect_videos(page)
    except Exception as e:
        print(f"Error during navigation: {e}")
    # 保持浏览器开启一段时间以便捕获API响应
    await asyncio.sleep(30)  # 可根据需要调整时间
    print(f"Browser {browser_id} - end")
    print(f"Browser {browser_id} - close page and browser")

    time.sleep(2)
    closeBrowser(browser_id)


async def scroll_and_collect_videos(page):
    for i in range(5):  # 滚动5次
        # 滚动到底部
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        # 等待新内容加载
        await page.wait_for_timeout(3000)
        # 检查是否有更多内容加载
        current_height = await page.evaluate("document.body.scrollHeight")
        await page.wait_for_timeout(1000)
    print("Scrolling completed, waiting for API responses")


async def handle_api_response(response, tiktok_account):
    """处理API响应的回调函数"""
    if "https://www.tiktok.com/api/post/item_list/" in response.url:
        try:
            # 获取响应数据
            data = await response.json()
            print(f"Captured API response from {response.url}:")
            data_str = str(data)
            if len(data_str) > 500:
                print(f"Response data (first 500 chars): {data_str[:500]}...")
            else:
                print(f"Response data: {data_str}")
            # 在这里可以处理获取到的数据
            process_video_data(data, tiktok_account)
        except Exception as e:
            print(f"Error processing API response: {e}")


def process_video_data(data, tiktok_account):
    """处理获取到的视频数据"""
    # 实现具体的数据处理逻辑
    if "itemList" in data:
        all_data = []
        videos = data["itemList"]
        print(f"Found {len(videos)} videos")
        for video in videos:
            my = {}
            video_id = video.get("id")
            # 获取统计数据
            stats = video.get("stats", {})
            collect_count = stats.get("collectCount", 0)
            comment_count = stats.get("commentCount", 0)
            digg_count = stats.get("diggCount", 0)
            play_count = stats.get("playCount", 0)
            share_count = stats.get("shareCount", 0)
            # 打印详细信息
            my["tiktokAccount"] = tiktok_account
            my["postId"] = video_id
            my["collects"] = collect_count
            my["comments"] = comment_count
            my["diggs"] = digg_count
            my["plays"] = play_count
            my["shares"] = share_count
            all_data.append(my)
        # 保存数据
