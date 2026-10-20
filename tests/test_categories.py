from datetime import date

from app.categories import age_category, est_junior


def test_age_category_boundaries():
    season = date(2030, 6, 1)

    assert age_category(date(2015, 12, 31), on=season) == "U16"
    assert age_category(date(2014, 1, 1), on=season) == "U18"
    assert age_category(date(2013, 12, 31), on=season) == "U18"
    assert age_category(date(2012, 1, 1), on=season) == "U20"
    assert age_category(date(2011, 12, 31), on=season) == "U20"
    assert age_category(date(2010, 1, 1), on=season) == "SENIOR"
    assert age_category(date(1996, 12, 31), on=season) == "SENIOR"
    assert age_category(date(1995, 1, 1), on=season) == "MASTER"


def test_est_junior_boundaries():
    season = date(2030, 6, 1)

    assert not est_junior(date(2015, 12, 31), on=season)  # U16
    assert est_junior(date(2014, 1, 1), on=season)  # U18
    assert est_junior(date(2011, 12, 31), on=season)  # U20
    assert not est_junior(date(2010, 1, 1), on=season)  # SENIOR
    assert not est_junior(date(1995, 1, 1), on=season)  # MASTER
