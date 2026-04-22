from sourced.config import load_user_name, save_user_name, config_path


def test_config_path_uses_home(tmp_home):
    assert config_path() == tmp_home / ".claude" / "sourced.config"


def test_load_returns_none_when_missing(tmp_home):
    assert load_user_name() is None


def test_save_then_load_roundtrip(tmp_home):
    save_user_name("Alice")
    assert load_user_name() == "Alice"


def test_load_handles_install_sh_bare_value(tmp_home):
    """install.sh writes `SOURCED_USER=Alice` for plain ASCII names (printf %q)."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER=Alice\n")
    assert load_user_name() == "Alice"


def test_load_handles_install_sh_backslash_escape(tmp_home):
    """install.sh writes `SOURCED_USER=Bob\\ Smith` for names with spaces (printf %q)."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER=Bob\\ Smith\n")
    assert load_user_name() == "Bob Smith"


def test_load_handles_install_sh_apostrophe_escape(tmp_home):
    """install.sh writes `SOURCED_USER=O\\'Brien` for names with quotes (printf %q)."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER=O\\'Brien\n")
    assert load_user_name() == "O'Brien"


def test_load_handles_single_quoted_value(tmp_home):
    """shlex.quote() output uses single-quoting; must round-trip."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER='Bob Smith'\n")
    assert load_user_name() == "Bob Smith"


def test_load_strips_trailing_whitespace(tmp_home):
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER=Alice   \n")
    assert load_user_name() == "Alice"


def test_load_treats_empty_value_as_missing(tmp_home):
    """`SOURCED_USER=` and `SOURCED_USER=""` should both return None."""
    cfg = tmp_home / ".claude" / "sourced.config"
    cfg.parent.mkdir(parents=True)
    cfg.write_text("SOURCED_USER=\n")
    assert load_user_name() is None


def test_save_roundtrip_with_spaces(tmp_home):
    save_user_name("Bob Smith")
    assert load_user_name() == "Bob Smith"


def test_save_roundtrip_with_apostrophe(tmp_home):
    save_user_name("O'Brien")
    assert load_user_name() == "O'Brien"


def test_save_creates_parent_dir(tmp_home):
    """~/.claude/ may not exist on a totally fresh machine."""
    save_user_name("Alice")
    assert (tmp_home / ".claude" / "sourced.config").exists()


def test_save_uses_sourced_user_key(tmp_home):
    """File must start with `SOURCED_USER=` for install.sh-source compat."""
    save_user_name("Alice")
    content = (tmp_home / ".claude" / "sourced.config").read_text()
    assert content.startswith("SOURCED_USER=")
    assert content.endswith("\n")
