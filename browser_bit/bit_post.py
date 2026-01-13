import time
from .bit_api import *
from playwright.async_api import async_playwright

async def check_upload_status(page, timeout=300000):
    """
    循环检查上传状态
    - status-ready, status-checking: 继续循环
    - status-warn, status-error: 返回False
    - status-success: 返回True
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        # 查找所有状态元素
        status_elements = await page.query_selector_all('div[data-show="true"]')

        for element in status_elements:
            class_list = await element.get_attribute("class")
            if class_list:
                # 检查状态类型
                if "status-success" in class_list:
                    print("状态检查通过 - status-success")
                    return True
                elif "status-error" in class_list or "status-warn" in class_list:
                    print(f"状态检查失败 - {class_list}")
                    return False
                elif "status-ready" in class_list or "status-checking" in class_list:
                    break

        # 等待一段时间后重试
        await page.wait_for_timeout(2000)

    print("状态检查超时")
    return False

async def post(**kwargs):
    device_id = kwargs.get("device_id")
    browser_id = kwargs.get("device_code")
    video_path = kwargs.get("video_path")
    copy_content = kwargs.get("video_copy")
    
    async with async_playwright() as playwright:
        res = openBrowser(browser_id)
        ws = res['data']['ws']
        print(f"Browser {browser_id} - ws address ==>>> {ws}")

        chromium = playwright.chromium
        browser = await chromium.connect_over_cdp(ws)
        default_context = browser.contexts[0]
        print(f'Browser {browser_id} - new page and goto tiktok creator_center')
        try:
            page = await default_context.new_page()
            await page.goto('https://www.tiktok.com/tiktokstudio/upload?from=creator_center', timeout=60000)
            print("打开页面")
            await page.wait_for_timeout(5000)
            element = await page.query_selector(".local-draft-content")
            if element:
                print("存在草稿")
                # 查找class=local-draft-button-group的元素
                button_group = await page.query_selector(".local-draft-button-group")
                if button_group:
                    # 获取按钮组下的所有div按钮
                    buttons = await button_group.query_selector_all("button")

                    # 检查是否恰好有2个按钮
                    if len(buttons) == 2:
                        # 点击第一个按钮
                        first_button = buttons[0]
                        await first_button.click()
                        print("丢弃草稿")

                        await page.wait_for_selector("div.TUXModal.common-modal", timeout=5000)
                        print("丢弃草稿对话框已出现")
                        # 点击Discard按钮
                        discard_button = await page.query_selector(".TUXButton--primary")
                        await discard_button.click()
                        print("已点击Discard按钮")
                        await page.wait_for_timeout(5000)

            await page.set_input_files('input[type="file"]', video_path, timeout=60000)
            print("上传文件")
            await page.wait_for_selector('[contenteditable="true"]', timeout=60000)
            print("出现编辑框")
            await page.wait_for_selector('button[aria-label="Replace"]', timeout=60000)
            print("上传完成")
            caption_editor = await page.query_selector('[contenteditable="true"]')
            print("编辑框已找到")
            if caption_editor:
                await caption_editor.click()
                await caption_editor.fill(copy_content)
            print("开始滚动到底部")

            post_button = await page.query_selector('button[data-e2e="post_video_button"]')
            if post_button:
                await post_button.scroll_into_view_if_needed()
                print("已滚动到发布按钮")
            else:
                await page.evaluate("document.querySelector('body').scrollIntoView(false)")

            # 检查状态
            print("检查开关状态")
            switches = await page.query_selector_all('input.Switch__input[type="checkbox"]')
            for switch in switches[-2:]:
                class_attr = await switch.get_attribute("class")
                is_checked = "Switch__input--checked-true" in class_attr
                if not is_checked:
                    print("Switch未开启，正在尝试开启")
                    # 点击切换状态
                    # 替换原来的 await switch.click()
                    await switch.evaluate_handle("element => element.click()")
                    # 等待1秒让状态更新（也可改用等待元素属性变化，更精准）
                    await page.wait_for_timeout(500)

                    # 验证状态是否切换成功
                    new_class_attr = await switch.get_attribute("class")
                    new_is_checked = "Switch__input--checked-true" in new_class_attr
                    if new_is_checked:
                        print("Switch已成功开启")
                    else:
                        print("警告：Switch开启失败，可能需要重新点击")
                        # 重试点击（可选）
                        await switch.evaluate_handle("element => element.click()")
                        await page.wait_for_timeout(500)

            if await check_upload_status(page):
                if post_button:
                    # 确保按钮可见并点击
                    await post_button.click()
                    print("Post button clicked")
                    print(
                        f"等待发布完成{browser_id},视频路径【{video_path}】,视频文案【{copy_content}】"
                    )
            else:
                print("发布失败")
        except Exception as e:
            print(f"发布失败: {e}")
        finally:
            # 关闭浏览器上下文中所有页面
            time.sleep(10)
            if default_context:
                pages = default_context.pages.copy()  # 复制页面列表，因为关闭页面会修改原列表
                for p in pages:
                    if not p.is_closed():
                        await p.close()
            closeBrowser(browser_id)