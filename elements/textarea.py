import allure
from playwright.sync_api import Locator, expect
from ui_coverage_tool import ActionType

from elements.base_element import BaseElement
from tools.logger import get_logger

logger = get_logger("TEXTAREA")


class Textarea(BaseElement):
    @property
    def type_of(self) -> str:
        return "textarea"

    def get_locator(self, nth: int = 0, **kwargs) -> Locator:
        return super().get_locator(nth, **kwargs).locator('textarea').first

    def get_raw_locator(self, nth: int = 0, **kwargs) -> str:
        return f"({super().get_raw_locator(nth, **kwargs)}//textarea)[1]"

    def fill(self, value: str, nth: int = 0, **kwargs):
        step = f'Fill {self.type_of} "{self.name}" to value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth, **kwargs)
            logger.info(step)
            locator.fill(value)

        self.track_coverage(ActionType.FILL, nth, **kwargs)

    def check_have_value(self, value: str, nth: int = 0, **kwargs):
        step = f'Checking that {self.type_of} "{self.name}" has a value "{value}"'

        with allure.step(step):
            locator = self.get_locator(nth, **kwargs)
            logger.info(step)
            expect(locator).to_have_value(value)

        self.track_coverage(ActionType.VALUE, nth, **kwargs)
