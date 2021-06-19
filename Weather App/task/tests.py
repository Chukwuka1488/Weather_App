import asyncio

from hstest import FlaskTest, CheckResult, WrongAnswer
from hstest import dynamic_test
from hstest.dynamic.security.exit_handler import ExitHandler
from pyppeteer import launch


class FlaskProjectTest(FlaskTest):
    source = 'web.app'
    run_args = {
        "headless": False,
        "defaultViewport": None,
        "args": ['--start-maximized', '--disable-infobar'],
        "ignoreDefaultArgs": ['--enable-automation'],
    }

    async def launch_and_get_browser(self):
        try:
            return await launch(self.run_args)
        except Exception as error:
            raise WrongAnswer(str(error))

    async def close_browser(self, browser):
        try:
            await browser.close()
        except Exception as ex:
            print(ex)

    async def test_response_async(self):
        browser = await self.launch_and_get_browser()
        page = await browser.newPage()
        try:
            await page.goto(self.get_url())
        except Exception:
            raise WrongAnswer(f"Can't access the main page with URL '{self.get_url()}'")
        await self.close_browser(browser)

    @dynamic_test(order=1)
    def test_response(self):
        ExitHandler.revert_exit()
        asyncio.get_event_loop().run_until_complete(self.test_response_async())
        return CheckResult.correct()

    async def test_main_page_structure_async(self):
        browser = await self.launch_and_get_browser()
        page = await browser.newPage()

        await page.goto(self.get_url())

        cards_div = await page.querySelector('div.cards')

        if cards_div is None:
            raise WrongAnswer("Can't find <div> block with class 'cards'")

        cards = await page.querySelectorAll('div.card')

        if len(cards) == 0:
            raise WrongAnswer("Can't find <div> blocks with class 'card'")

        if len(cards) != 3:
            raise WrongAnswer(f"Found {len(cards)} <div> blocks with class 'card', but should be 3!")

        for card in cards:
            degrees = await card.querySelector('div.degrees')
            if degrees is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'degrees'")
            state = await card.querySelector('div.state')
            if state is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'state'")
            city = await card.querySelector('div.city')
            if city is None:
                raise WrongAnswer(
                    "One of the <div> blocks with card class 'card' doesn't contain <div> block with class 'city'")

        input_field = await page.querySelector('input#input-city')

        if input_field is None:
            raise WrongAnswer("Can't find <input> element with id 'input-city'")

        button = await page.querySelector('button.submit-button')

        if button is None:
            raise WrongAnswer("Can't find <button> element with class 'submit-button'")

        await self.close_browser(browser)

        return CheckResult.correct()

    @dynamic_test(order=2)
    def test_main_page_structure(self):
        asyncio.get_event_loop().run_until_complete(self.test_main_page_structure_async())
        return CheckResult.correct()


if __name__ == '__main__':
    FlaskProjectTest().run_tests()
