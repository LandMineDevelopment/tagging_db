import pytest
from click.testing import CliRunner
from tag import cli

class TestCLI:
class TestCLI:
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_add_command(self, runner, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        with runner.isolated_filesystem():
            test_file.write_text('content')
            result = runner.invoke(cli, ['--config', str(tmp_path / '.tagconfig'), 'add', str(test_file), 'work', 'project'])
            assert result.exit_code == 0
            assert "Added tags" in result.output
    
    def test_find_command(self, runner, tmp_path):
        test_file = tmp_path / 'test.txt'
        test_file.write_text('content')
        with runner.isolated_filesystem():
            test_file.write_text('content')
            runner.invoke(cli, ['add', str(test_file), 'work', 'project'])
            result = runner.invoke(cli, ['find', 'work'])
            assert result.exit_code == 0
            # Check output contains file path