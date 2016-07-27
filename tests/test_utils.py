import pytest

from collections import OrderedDict

from context import utils
from context import parser
from context import configuration


class TestParseConfig:
    invalid_conf = """
[CLuster
machines = fedoar

[fedora]
box = 

[Scnearios]
tasks = dothis

[dothat]
target = dedora
timgin
actions = ls
cd / && l
    """
    cluster_block = """
[Cluster]
machines = winxp, archlinux
    """
    cluster_invalid = """
[Cluster]
    """
    machines_block = """
[winxp]
box = IE8.XP.For.Vagrant
guest = windows
username = IEUser
password = Passw0rd!
ip = 192.168.51.5
shares = /tmp -> /host_tmp

[archlinux]
box = terrywang/archlinux
shares = /tmp -> /host_tmp
    """
    scenario_block = """
[Scenario]
tasks = check_disks, list_files, sleep
duration = 1m
    """
    scenario_invalid = """
[Scenario]
duration = 1m
    """
    tasks_block = """
[check_disks]
target = winxp
timing = 10s
actions = wmic logicaldisk get caption > disks.txt
artifacts = disks.txt

[list_files]
target = archlinux
timing = +10s
actions = ls -lah > file_list
files = .bashrc
        .bash_history -> history
artifacts = file_list -> archlinux_ls

[sleep]
target = archlinux
timing = +20s
actions = sleep 120
    """

    conf_machines = OrderedDict([
        ('winxp', {
            'username': 'IEUser',
            'shares': '/tmp -> /host_tmp',
            'password': 'Passw0rd!',
            'box': 'IE8.XP.For.Vagrant',
            'guest': 'windows',
            'ip': '192.168.51.5',
            }),
        ('archlinux', {
            'shares': '/tmp -> /host_tmp',
                'box': 'terrywang/archlinux',
                }),
            ])
    conf_forwards = {
            'winxp': {5985: 2000},
            'archlinux': {22: 2001},
            }
    conf_tasks = OrderedDict([
        ('check_disks', {
            'target': 'winxp',
                'artifacts': 'disks.txt',
                'actions': 'wmic logicaldisk get caption > disks.txt',
                'files': '',
                'timing': 10,
                }),
        ('list_files', {
            'target': 'archlinux',
            'artifacts': 'file_list -> archlinux_ls',
            'actions': 'ls -lah > file_list',
            'files': '.bashrc\n.bash_history -> history',
            'timing': 20,
            }),
        ('sleep', {
            'target': 'archlinux',
            'artifacts': '',
            'actions': 'sleep 120',
            'files': '', 'timing': 40,
            }),
        ])

    @staticmethod
    def write_config(tmpdir, conf):
        tmpfile = str(tmpdir.join("moirai.ini"))
        with open(tmpfile, 'w') as f:
            f.write(conf)
        return tmpfile

    def test_invalid_conf(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir, TestParseConfig.invalid_conf)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(Exception) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert ex

    def test_missing_cluster(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.machines_block +
                TestParseConfig.scenario_block +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_invalid_cluster(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_invalid +
                TestParseConfig.machines_block +
                TestParseConfig.scenario_block +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_missing_machines(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_block +
                TestParseConfig.scenario_block +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_missing_scenario(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_block +
                TestParseConfig.machines_block +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_invalid_scenario(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_block +
                TestParseConfig.machines_block +
                TestParseConfig.scenario_invalid +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_missing_tasks(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_block +
                TestParseConfig.machines_block +
                TestParseConfig.scenario_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        with pytest.raises(SystemExit) as ex:
            utils.parse_config(args, configuration.Configuration())
        assert str(ex.value) == "1"

    def test_valid_config(self, tmpdir):
        tmpfile = TestParseConfig.write_config(tmpdir,
                TestParseConfig.cluster_block +
                TestParseConfig.machines_block +
                TestParseConfig.scenario_block +
                TestParseConfig.tasks_block)
        parse = parser.create_parser()
        args = parse.parse_args(['-c', tmpfile, 'create'])
        config = utils.parse_config(args, configuration.Configuration())
        assert config.conf == TestParseConfig.conf_machines
        assert config.forwards == TestParseConfig.conf_forwards
        assert config.tasks == TestParseConfig.conf_tasks

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

class TestPrettyPrint:
    def test_pretty_print(self, capsys):
        utils.pretty_print("aa")
        out, _ = capsys.readouterr()
        assert out == " │ aa\n"

