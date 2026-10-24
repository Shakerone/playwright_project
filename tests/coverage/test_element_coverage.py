from collections import Counter

import pytest
from playwright.sync_api import Page, TimeoutError, expect
from ui_coverage_tool import ActionType, UICoverageTracker
from ui_coverage_tool.config import get_settings

import elements.base_element as base_element
from elements.base_element import BaseElement
from elements.button import Button
from elements.input import Input
from elements.textarea import Textarea


@pytest.fixture
def coverage_tracker(tmp_path, monkeypatch):
    settings = get_settings().model_copy(update={"results_dir": tmp_path / "results"})
    tracker = UICoverageTracker(app="ui-course", settings=settings)
    monkeypatch.setattr(base_element, "tracker", tracker)
    return tracker


def test_button_records_successful_actions(page: Page, coverage_tracker):
    page.set_content(
        '<button data-testid="button" id="enabled">Save</button>'
        '<button data-testid="button" id="disabled" disabled>Save</button>'
    )
    button = Button(page, "button", "Save")

    button.check_enabled()
    button.check_disabled(nth=1)
    button.check_visible()
    button.check_have_text("Save")
    button.click()

    records = coverage_tracker.storage.load().root
    assert Counter(record.action_type for record in records) == Counter(
        [ActionType.ENABLED, ActionType.DISABLED, ActionType.VISIBLE, ActionType.TEXT, ActionType.CLICK]
    )
    for record in records:
        expected_id = "disabled" if record.action_type == ActionType.DISABLED else "enabled"
        assert page.locator(f"xpath={record.selector}").get_attribute("id") == expected_id


def test_input_coverage_uses_requested_wrapper_index(page: Page, coverage_tracker):
    page.set_content(
        '<section><div data-testid="field-7"><input id="first"></div></section>'
        '<section><div data-testid="field-7"><input id="second"></div></section>'
    )
    field = Input(page, "field-{index}", "Field")

    field.fill("example", nth=1, index=7)
    field.check_have_value("example", nth=1, index=7)

    expect(page.locator("#first")).to_have_value("")
    records = coverage_tracker.storage.load().root
    assert {record.action_type for record in records} == {ActionType.FILL, ActionType.VALUE}
    assert len(records) == 2
    for record in records:
        assert page.locator(f"xpath={record.selector}").get_attribute("id") == "second"


def test_textarea_coverage_matches_first_descendant(page: Page, coverage_tracker):
    page.set_content(
        '<section data-testid="description-2"><textarea id="other"></textarea></section>'
        '<section data-testid="description-2">'
        '<div><textarea id="target"></textarea></div>'
        '<div><textarea id="extra"></textarea></div>'
        '</section>'
    )
    field = Textarea(page, "description-{index}", "Description")

    field.fill("description", nth=1, index=2)
    field.check_have_value("description", nth=1, index=2)

    expect(page.locator("#other")).to_have_value("")
    expect(page.locator("#extra")).to_have_value("")
    records = coverage_tracker.storage.load().root
    assert {record.action_type for record in records} == {ActionType.FILL, ActionType.VALUE}
    assert len(records) == 2
    for record in records:
        assert page.locator(f"xpath={record.selector}").get_attribute("id") == "target"


@pytest.mark.parametrize("nth", [0, 1, -1])
def test_raw_selector_matches_playwright_index_with_quotes(page: Page, nth):
    test_id = "field-with-\"double\"-and-'single'-quotes"
    page.evaluate(
        """testId => {
            for (let index = 0; index < 3; index++) {
                const section = document.createElement('section');
                const element = document.createElement('div');
                element.dataset.testid = testId;
                element.id = `element-${index}`;
                section.append(element);
                document.body.append(section);
            }
        }""",
        test_id,
    )
    element = BaseElement(page, test_id, "Quoted test ID")

    assert page.locator(f"xpath={element.get_raw_locator(nth)}").get_attribute("id") == (
        element.get_locator(nth).get_attribute("id")
    )


def test_failed_click_is_not_counted_as_coverage(page: Page, coverage_tracker):
    page.set_content('<button data-testid="disabled" disabled>Save</button>')
    page.set_default_timeout(100)

    with pytest.raises(TimeoutError):
        Button(page, "disabled", "Disabled").click()

    assert coverage_tracker.storage.load().root == []
