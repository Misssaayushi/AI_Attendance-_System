import pytest

from app.exceptions import ExcelTemplateValidationException
from app.services import excel_service


def test_generate_monthly_workbook_template_rejects_invalid_month():
    with pytest.raises(ExcelTemplateValidationException):
        excel_service.generate_monthly_workbook_template(year=2026, month=13)


def test_generate_monthly_workbook_template_rejects_invalid_year():
    with pytest.raises(ExcelTemplateValidationException):
        excel_service.generate_monthly_workbook_template(year=1800, month=5)


def test_iter_in_batches_splits_list_correctly():
    items = list(range(7))
    batches = list(excel_service._iter_in_batches(items, batch_size=3))
    assert batches == [[0, 1, 2], [3, 4, 5], [6]]
