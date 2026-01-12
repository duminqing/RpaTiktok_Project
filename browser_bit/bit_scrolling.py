import random
import time
from .bit_api import *
from playwright.async_api import async_playwright

async def scrolling(**kwargs):
    search_queries = kwargs.get('memo').split(',')
    browser_id = kwargs.get('device_code')
    scrolling_time = int(kwargs.get('scrolling_time'))
    
    async with async_playwright() as playwright:
        res = openBrowser(browser_id)
        ws = res['data']['ws']
        print(f"Browser {browser_id} - ws address ==>>> {ws}")

        chromium = playwright.chromium
        browser = await chromium.connect_over_cdp(ws)
        default_context = browser.contexts[0]

        # 记录开始时间
        start_time = time.time()
        end_time = start_time + scrolling_time * 60

        # 循环使用不同的搜索词
        search_index = random.randint(0, len(search_queries) - 1)
        while time.time() < end_time:
            current_search = search_queries[search_index % len(search_queries)]

            print(f'Browser {browser_id} - new page and goto tiktok with query: {current_search}')
            page = await default_context.new_page()

            await page.goto(f'https://www.tiktok.com/search?q={current_search}', timeout=60000)

            time.sleep(10)
            elements = await page.query_selector_all('[id*="grid-item-container"]')
            if elements:
                await elements[random.randint(0, 7)].click()

            # 在当前搜索词下刷视频，直到没有视频或时间结束
            while time.time() < end_time:
                sleep_time = random.randint(1, 20)
                print(f'Browser {browser_id} - sleep {sleep_time} seconds')
                time.sleep(sleep_time)

                # 尝试点赞，捕获任何异常
                try:
                    if sleep_time > 15:
                        like_icon = await page.query_selector('span[data-e2e="browse-like-icon"] svg')
                        if like_icon:
                            # 获取fill属性值判断是否为灰色（未点赞状态）
                            fill_color = await like_icon.get_attribute('fill')
                            if fill_color == 'rgba(255, 255, 255, .9)':  # 灰色状态，可以点赞
                                print(f'Browser {browser_id} - click like')
                                await page.click('span[data-e2e="browse-like-icon"]')
                                time.sleep(2)
                            else:
                                print(f'Browser {browser_id} - already liked, skip')
                except Exception as e:
                    print(f'Browser {browser_id} - like operation failed: {str(e)}')
                    pass  # 直接跳过异常

                # 检查下一个按钮是否存在
                try:
                    arrow_button = await page.query_selector('button[data-e2e="arrow-right"]')
                    if not arrow_button:
                        print(
                            f'Browser {browser_id} - no more videos for query "{current_search}", switching to next query')
                        await page.close()
                        search_index += 1

                        break  # 没有视频了，跳出内层循环，使用下一个搜索词
                    await page.click('button[data-e2e="arrow-right"]')
                except Exception as e:
                    print(f'Browser {browser_id} - arrow button operation failed: {str(e)}')
                    await page.close()
                    search_index += 1
                    break  # 出现异常，跳出内层循环，使用下一个搜索词
                # 如果时间到了就退出
                if time.time() >= end_time:
                    break

        print(f'Browser {browser_id} - end')
        print(f'Browser {browser_id} - close page and browser')

        time.sleep(2)
        closeBrowser(browser_id)