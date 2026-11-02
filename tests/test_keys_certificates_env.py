"""
Keys, certificates, keystores and env files (#76).

Path-based only: panopticas never opens these files and makes no claim about
whether one holds a real secret. .pem and .der are tagged by encoding,
because the path can't say what they hold. Sources and decisions in
changes/2026-11-keys-certificates-env.md.
"""

import pytest

from panopticas import get_filename_metatypes, get_language
from panopticas.core import get_tags


@pytest.mark.parametrize("path,tags", [
    # Encodings: RFC 7468 allows any of nine labels in a .pem file.
    ("certs/server.pem", ["PEM", "security"]),
    ("tests/data/isrgrootx1.der", ["DER", "security", "binary"]),
    # Certificates and related objects
    ("certs/server.crt", ["certificate", "security"]),
    ("certs/server.cer", ["certificate", "security"]),
    ("certs/chain.p7b", ["certificate", "security"]),
    ("certs/chain.p7c", ["certificate", "security"]),
    ("certs/revoked.crl", ["certificate", "security"]),
    ("certs/server.csr", ["certificate", "security"]),
    # Keys
    ("certs/server.key", ["key", "security"]),
    ("deploy/id_rsa", ["key", "security", "SSH"]),
    ("id_ecdsa", ["key", "security", "SSH"]),
    ("id_ecdsa_sk", ["key", "security", "SSH"]),
    ("id_ed25519", ["key", "security", "SSH"]),
    ("id_ed25519_sk", ["key", "security", "SSH"]),
    ("id_mldsa44_ed25519", ["key", "security", "SSH"]),
    ("id_dsa", ["key", "security", "SSH"]),       # removed from OpenSSH
    # Public keys aren't secret.
    ("deploy/id_rsa.pub", ["key", "SSH"]),
    ("testkey_ed25519.pub", ["key"]),
    ("rsa-psw.key.pub", ["key"]),
    ("putty/server.ppk", ["key", "security", "PuTTY"]),
    # Keystores
    ("client.p12", ["keystore", "certificate", "key", "security", "binary"]),
    ("server.pfx", ["keystore", "certificate", "key", "security", "binary"]),
    ("android/app/upload.jks",
     ["keystore", "security", "binary", "Java"]),
    ("android/app/debug.keystore",
     ["keystore", "security", "binary", "Java"]),
    ("secrets/team.kdbx", ["keystore", "security", "binary", "KeePass"]),
])
def test_key_and_certificate_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path,tags", [
    (".env", ["dotenv", "config"]),
    ("app/.env", ["dotenv", "config"]),
    (".env.production", ["dotenv", "config"]),
    (".env.local", ["dotenv", "config"]),
    (".env.test.local", ["dotenv", "config"]),
    (".env.encrypted", ["dotenv", "config"]),     # Laravel
    # Templates: the last segment decides.
    (".env.example", ["dotenv", "config", "template"]),
    (".env.sample", ["dotenv", "config", "template"]),
    (".env.template", ["dotenv", "config", "template"]),
    (".env.local.example", ["dotenv", "config", "template"]),
    (".env.production.sample", ["dotenv", "config", "template"]),
    # dotenvx keeps decryption keys here.
    (".env.keys", ["dotenv", "key", "security"]),
])
def test_dotenv_files(path, tags):
    assert get_filename_metatypes(path) == tags


@pytest.mark.parametrize("path", [
    # Symfony's compiled cache is PHP, not dotenv.
    ".env.local.php",
    # direnv (#105), and other tools' *.env names
    ".envrc",
    "benchmarks.env",
    ".xcode.env",
    # Lookalikes
    "my.env.example",
    ".environment",
    "env.example",
])
def test_not_dotenv(path):
    assert "dotenv" not in get_filename_metatypes(path)


@pytest.mark.parametrize("path", [
    # OpenPGP armor: signatures, messages or keys.
    "dist/twine-4.0.2-py3-none-any.whl.asc",
    "signing-key.asc",
    # User-level SSH data, not secret
    "known_hosts",
    "authorized_keys",
    # Lookalikes of SSH key names
    "id_rsa.txt",
    "my_id_rsa",
])
def test_not_tagged_as_keys(path):
    tags = set(get_filename_metatypes(path))
    assert not {"key", "SSH", "security"} & tags


@pytest.mark.parametrize("path,filetype", [
    ("server.pem", "PEM"),
    ("server.crt", "X.509 Certificate"),
    ("server.cer", "X.509 Certificate"),
    ("isrgrootx1.der", "DER"),
    ("chain.p7b", "PKCS #7"),
    ("chain.p7c", "PKCS #7"),
    ("revoked.crl", "Certificate Revocation List"),
    ("server.csr", "Certificate Signing Request"),
    ("server.key", "Key"),
    ("id_rsa.pub", "Public Key"),
    ("id_ed25519", "SSH Private Key"),
    ("server.ppk", "PuTTY Private Key"),
    ("client.p12", "PKCS #12"),
    ("server.pfx", "PKCS #12"),
    ("upload.jks", "Java KeyStore"),
    ("debug.keystore", "Java KeyStore"),
    ("team.kdbx", "KeePass Database"),
    (".env", "dotenv"),
    (".env.local.example", "dotenv"),
    (".env.keys", "dotenv"),
    (".env.local.php", "PHP"),
])
def test_filetypes(path, filetype):
    assert get_language(path, skip_shebang=True) == filetype


def test_new_tags_in_vocabulary():
    assert {"certificate", "key", "keystore", "dotenv", "template", "PEM",
            "DER", "SSH", "PuTTY", "KeePass"} <= set(get_tags())
