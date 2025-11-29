"""Tests for utility functions."""

from datetime import date

import pytest

from app.milestones import get_all_milestones, get_milestone_for_age
from app.utils import calculate_age_months, group_words_by_month, get_monthly_stats


class TestCalculateAgeMonths:
    """Tests for calculate_age_months function."""

    def test_same_date(self):
        """Age is 0 when birthdate equals reference date."""
        birthdate = date(2024, 1, 15)
        reference = date(2024, 1, 15)
        assert calculate_age_months(birthdate, reference) == 0

    def test_exact_months(self):
        """Age calculation for exact months."""
        birthdate = date(2024, 1, 15)
        reference = date(2024, 7, 15)
        assert calculate_age_months(birthdate, reference) == 6

    def test_before_birthday_day(self):
        """Age adjusts when reference day is before birthday day."""
        birthdate = date(2024, 1, 15)
        reference = date(2024, 7, 10)  # 5 days before the 15th
        assert calculate_age_months(birthdate, reference) == 5

    def test_after_birthday_day(self):
        """Age includes month when reference day is after birthday day."""
        birthdate = date(2024, 1, 15)
        reference = date(2024, 7, 20)  # 5 days after the 15th
        assert calculate_age_months(birthdate, reference) == 6

    def test_year_boundary(self):
        """Age calculation across year boundary."""
        birthdate = date(2023, 6, 15)
        reference = date(2024, 6, 15)
        assert calculate_age_months(birthdate, reference) == 12

    def test_multiple_years(self):
        """Age calculation for multiple years."""
        birthdate = date(2022, 3, 10)
        reference = date(2024, 9, 10)
        assert calculate_age_months(birthdate, reference) == 30

    def test_never_negative(self):
        """Age is never negative even for future birthdates."""
        birthdate = date(2025, 1, 15)
        reference = date(2024, 1, 15)
        assert calculate_age_months(birthdate, reference) == 0


class TestGetMilestoneForAge:
    """Tests for get_milestone_for_age function."""

    def test_under_12_months(self):
        """No milestone for babies under 12 months."""
        assert get_milestone_for_age(6) is None
        assert get_milestone_for_age(11) is None

    def test_12_months(self):
        """12 month milestone returned for 12-14 month range."""
        milestone = get_milestone_for_age(12)
        assert milestone is not None
        assert milestone["age_months"] == 12
        assert milestone["min_words"] == 1
        assert milestone["max_words"] == 3

    def test_15_months(self):
        """15 month milestone returned for 15-17 month range."""
        milestone = get_milestone_for_age(15)
        assert milestone is not None
        assert milestone["age_months"] == 15
        assert milestone["min_words"] == 3

    def test_18_months(self):
        """18 month milestone returned for 18-23 month range."""
        milestone = get_milestone_for_age(18)
        assert milestone is not None
        assert milestone["age_months"] == 18
        assert milestone["min_words"] == 10
        assert milestone["max_words"] == 50

    def test_24_months(self):
        """24 month milestone for 24-29 month range."""
        milestone = get_milestone_for_age(24)
        assert milestone is not None
        assert milestone["age_months"] == 24
        assert milestone["min_words"] == 50

    def test_30_months(self):
        """30 month milestone for 30-35 month range."""
        milestone = get_milestone_for_age(30)
        assert milestone is not None
        assert milestone["age_months"] == 30
        assert milestone["min_words"] == 200
        assert milestone["max_words"] is None

    def test_36_months(self):
        """36 month milestone for 36+ months."""
        milestone = get_milestone_for_age(36)
        assert milestone is not None
        assert milestone["age_months"] == 36
        assert milestone["min_words"] == 450

    def test_older_than_36_months(self):
        """36 month milestone still applies for older children."""
        milestone = get_milestone_for_age(48)
        assert milestone is not None
        assert milestone["age_months"] == 36

    def test_none_input(self):
        """Handles None input gracefully."""
        assert get_milestone_for_age(None) is None


class TestGetAllMilestones:
    """Tests for get_all_milestones function."""

    def test_returns_list(self):
        """Returns a list of milestones."""
        milestones = get_all_milestones()
        assert isinstance(milestones, list)
        assert len(milestones) == 6

    def test_milestone_structure(self):
        """Each milestone has required keys."""
        milestones = get_all_milestones()
        for milestone in milestones:
            assert "age_months" in milestone
            assert "min_words" in milestone
            assert "max_words" in milestone
            assert "label" in milestone

    def test_milestones_ordered(self):
        """Milestones are in ascending age order."""
        milestones = get_all_milestones()
        ages = [m["age_months"] for m in milestones]
        assert ages == sorted(ages)


class TestGroupWordsByMonth:
    """Tests for group_words_by_month function."""

    def test_groups_correctly(self, app, sample_words):
        """Words are grouped by month."""
        with app.app_context():
            grouped = group_words_by_month(sample_words)
            # Should have at least one group
            assert len(grouped) > 0
            # Keys should be (year, month) tuples
            for key in grouped.keys():
                assert isinstance(key, tuple)
                assert len(key) == 2

    def test_empty_list(self, app):
        """Handles empty word list."""
        with app.app_context():
            grouped = group_words_by_month([])
            assert grouped == {}


class TestGetMonthlyStats:
    """Tests for get_monthly_stats function."""

    def test_returns_list(self, app, seeded_db, sample_words):
        """Returns a list of monthly statistics."""
        with app.app_context():
            stats = get_monthly_stats()
            assert isinstance(stats, list)

    def test_stat_structure(self, app, seeded_db, sample_words):
        """Each stat entry has required keys."""
        with app.app_context():
            stats = get_monthly_stats()
            if stats:
                for stat in stats:
                    assert "year" in stat
                    assert "month" in stat
                    assert "month_name" in stat
                    assert "count" in stat
                    assert "running_total" in stat

    def test_running_total_increases(self, app, seeded_db, sample_words):
        """Running total increases or stays same across months."""
        with app.app_context():
            stats = get_monthly_stats()
            if len(stats) > 1:
                for i in range(1, len(stats)):
                    assert stats[i]["running_total"] >= stats[i - 1]["running_total"]

    def test_final_total_matches_count(self, app, seeded_db, sample_words):
        """Final running total equals total word count."""
        with app.app_context():
            from app.models import Word
            stats = get_monthly_stats()
            total_words = Word.query.count()
            if stats:
                assert stats[-1]["running_total"] == total_words

    def test_empty_when_no_words(self, app, seeded_db):
        """Returns empty list when no words exist."""
        with app.app_context():
            stats = get_monthly_stats()
            assert stats == []
