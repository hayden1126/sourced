from sourced.config import load_user_name, save_user_name, config_path


def test_config_path_uses_home(tmp_home):
    assert config_path() == tmp_home / ".claude" / "sourced.config"


def test_load_returns_none_when_missing(tmp_home):
    assert load_user_name() is None


def test_save_then_load_roundtrip(tmp_home):
    save_user_name("Alice")
    assert load_user_name() == "Alice"


def test_load_handles_quoted_value(tmp_home):
    """install.sh writes USER_NAME="Alice"; we must read that format."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('USER_NAME="Alice"\n')
    assert load_user_name() == "Alice"


def test_load_handles_unquoted_value(tmp_home):
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("USER_NAME=Alice\n")
    assert load_user_name() == "Alice"


def test_load_strips_trailing_whitespace(tmp_home):
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text('USER_NAME="Alice"   \n')
    assert load_user_name() == "Alice"


def test_save_creates_parent_dir(tmp_home):
    """~/.claude/ may not exist on a totally fresh machine."""
    save_user_name("Alice")
    assert (tmp_home / ".claude" / "sourced.config").exists()


def test_save_writes_install_sh_format(tmp_home):
    """Format must round-trip with install.sh's writer for tag rollback compat."""
    save_user_name("Alice")
    content = (tmp_home / ".claude" / "sourced.config").read_text()
    assert content.startswith('USER_NAME="Alice"')
