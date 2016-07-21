import pytest

from context import utils


class TestParseWordlist:
    def test_wordlist(self):
        assert utils.parse_wordlist('a,b,  c,,, d  ') == ['a', 'b', 'c', 'd']

class TestParseAssociations:
    def test_oneline(self):
        assert utils.parse_associations('a -> b') == [('a','b')]

    def test_morelines(self):
        assert utils.parse_associations('a -> b\nc -> d\n') == [('a', 'b'), ('c', 'd')]

    def test_no_association(self):
        with pytest.raises(Exception) as ex:
            utils.parse_associations('a')
        assert str(ex.value) == "Invalid number of members"

    def test_too_many_associations(self):
        with pytest.raises(Exception) as ex:
            utils.parse_associations('a -> b -> c')
        assert str(ex.value) == "Invalid number of members"

    def test_empty_right(self):
        with pytest.raises(Exception) as ex:
            utils.parse_associations('a ->')
        assert str(ex.value) == "Empty member"

    def test_empty_left(self):
        with pytest.raises(Exception) as ex:
            utils.parse_associations('-> a')
        assert str(ex.value) == "Empty member"

class TestParseTiming:
    def test_digit(self):
        assert utils.parse_timing('10', 0) == 10

    def test_add(self):
        assert utils.parse_timing('+10', 10) == 20

    def test_no_add(self):
        assert utils.parse_timing('10', 10) == 10

    def test_hour_minute_second(self):
        assert utils.parse_timing('1h2m3s', 0) == 3723

    def test_hour_minute(self):
        assert utils.parse_timing('1h2m', 0) == 3720

    def test_hour_second(self):
        assert utils.parse_timing('1h3s', 0) == 3603

    def test_hour(self):
        assert utils.parse_timing('1h', 0) == 3600

    def test_minute_second(self):
        assert utils.parse_timing('2m3s', 0) == 123

    def test_minute(self):
        assert utils.parse_timing('2m', 0) == 120

    def test_second(self):
        assert utils.parse_timing('3s', 0) == 3

    def test_no_last_second(self):
        assert utils.parse_timing('1h2m3', 0) == 3723

    def test_no_last_minute(self):
        assert utils.parse_timing('1h2', 0) == 3720

    def test_wrong_order(self):
        with pytest.raises(Exception) as ex:
            utils.parse_timing("1s3m5h", 0)
        assert str(ex.value) == "Unknown unit or wrong unit order"

    def test_no_smaller_than_second(self):
        with pytest.raises(Exception) as ex:
            utils.parse_timing("5s3", 0)
        assert str(ex.value) == "No unit smaller than second"

