# Keys, Certificates, Keystores and Env Files

For [#76](https://github.com/kospex/panopticas/issues/76).

**Status:** implemented 2026-11-02, as decided (see *Decisions* and
*Implemented*). Verified 2026-11-02.

Path-based only. Panopticas never opens these files and makes no claim
about whether one holds a real secret. It reports what the file is; kospex
decides what that means (detector, not policy).

## Current state

Every candidate below is `Unknown` with no tags today. Counts are from a
local kospex database (376 repositories), current files only:

| File | Files | Repos |
|---|---|---|
| `*.pem` | 432 | 16 |
| `*.crt` | 425 | 9 |
| `*.p12` | 437 | 2 |
| `*.crl` | 181 | 2 |
| `*.der` | 106 | 3 |
| `.env.*` | 103 | 8 |
| `*.key` | 48 | 11 |
| `*.pub` | 38 | 3 |
| `.env` | 22 | 7 |
| `*.asc` | 16 | 4 |
| `*.keystore` | 4 | 4 |
| `*.csr` | 3 | 1 |
| `.envrc` | 2 | 2 |
| `*.cer`, `*.pfx`, `*.jks`, `*.p7b`, `id_*` (SSH), `.netrc` | 1 each | 1 each |
| `*.ppk`, `*.kdbx`, `*.p8` | 0 | 0 |

What the names show (basenames only; no file was opened):

- **Most of the volume is test material.** The `.p12`, `.der`, `.crl` and
  many `.pem` files are cryptography-library test vectors
  (`name-2-pwd.p12`, `badssl-sct-none-hash.der`). Issue question 6
  anticipated this.
- **`.env.local.example` is the commonest env file** (55), ahead of
  `.env.example` (30). Templates have compound names: `.env.local.example`,
  `.env.production.sample`. Matching only `.env.example` would miss most of
  them.
- **`*.env` names aren't dotenv files.** `.xcode.env` (React Native's Xcode
  config) and `benchmarks.env` are other tools' conventions.
- **`.asc` is ASCII-armored OpenPGP of every kind.** The sample includes a
  release signature (`twine-4.0.2-py3-none-any.whl.asc`), messages and
  keys.
- **`.key` files are keys** in this sample (`server.key`, `client.key`). No
  Keynote presentation was seen.
- **`.pub` files are SSH and test public keys,** including the compound
  `*.key.pub`.
- **`debug.keystore`**, Android's debug signing keystore, is committed in 4
  repositories.

## Findings: certificates and keys

- **PEM (RFC 7468).** A textual encoding with a label per type:
  `CERTIFICATE`, `X509 CRL`, `CERTIFICATE REQUEST`, `PKCS7`, `CMS`,
  `PRIVATE KEY`, `ENCRYPTED PRIVATE KEY`, `ATTRIBUTE CERTIFICATE` and
  `PUBLIC KEY`. "Files MAY contain multiple textual encoding instances."
  The RFC doesn't say whether one file can mix types; in practice
  `server.pem` often holds a key and a certificate together. So `.pem` is a
  container, and only its contents say which: issue question 2.
- **`.pem` as an extension.** RFC 8555 (ACME) registers
  `application/pem-certificate-chain` with "File extension(s): .pem", for a
  file that "contains one or more certificates encoded with the PEM textual
  encoding".
- **`.crt` and `.cer`.** RFC 7468 §5.3: "the extension ".crt" SHOULD be
  used for the textual encoding of a certificate", and "many tools still
  default to encode certificates in this textual encoding with the
  extension ".cer"". RFC 2585 registers `application/pkix-cert` with
  "File extension(s): .CER" and `application/pkix-crl` with ".CRL"; over
  FTP and HTTP each `.cer` holds "exactly one certificate, encoded in DER
  format". So `.cer` may be text or binary.
- **`.der`.** DER is a binary encoding, not a type. Android's signing docs
  name "A public key certificate (`.der` or `.pem` files)". In the sample,
  `.der` files are certificates and SCTs.
- **PKCS #12 (`.p12`, `.pfx`).** RFC 7292 covers personal identity data
  "including private keys, certificates, miscellaneous secrets, and
  extensions". It names no extension. Microsoft's Certificate Installer
  page: ".PFX/.P12 – ... format files that include personal certificates
  with private keys", which support "one or more certificates and one or
  more private keys". Binary.
- **PKCS #7 (`.p7b`).** The same Microsoft page: ".P7B ... install multiple
  certificates", "Supports one or more certificates. No private keys."
- **SSH keys (OpenSSH `ssh-keygen`).** The default private key files under
  `~/.ssh` are `id_ecdsa`, `id_ecdsa_sk`, `id_ed25519`, `id_ed25519_sk`,
  `id_mldsa44_ed25519` and `id_rsa`. Of each one: "This file should not be
  readable by anyone but the user." Of the `.pub` files: "There is no need
  to keep the contents of this file secret." `id_dsa` isn't listed any
  more; DSA keys were removed from OpenSSH, but older repositories can still
  have one (keep the legacy name, as with chat modes).
- **PuTTY (`.ppk`).** PuTTYgen saves "in PuTTY's native format (`*.PPK`)";
  the passphrase "will be used to encrypt the key on disk", so the file
  holds the private key. No `.ppk` files in the sample.
- **Java keystores.** keytool's default keystore is "the file named
  `.keystore` in the user's home directory", a user-level path. The format
  is set by `-storetype` (PKCS12 by default since JDK 9, or the proprietary
  JKS), not by extension; `.jks` appears only in examples (`server.jks`).
  Android's signing docs: "Java Keystores (.jks or .keystore) are binary
  files that serve as repositories of certificates and private keys", and
  an upload keystore should be named "with the `.jks` extension". The debug
  keystore is created "in `$HOME/.android/debug.keystore`", which is
  user-level too, but committed copies exist.
- **OpenPGP (`.asc`).** RFC 9580's armor header lines are `BEGIN PGP
  MESSAGE`, `BEGIN PGP PUBLIC KEY BLOCK`, `BEGIN PGP PRIVATE KEY BLOCK` and
  `BEGIN PGP SIGNATURE`. The RFC names no extension. A `.asc` file can be
  any of the four, and signatures are the common case in repositories.
- **KeePass (`.kdbx`).** "KDBX is the KeePass 2.x database file format,
  which is used for storing user data (user names, passwords, URLs,
  etc.)." The page names no extension, though `.kdbx` is the format's name.
- **`.key` collision.** Apple Keynote uses `.key`. No Apple page stating it
  was found (only third-party format sites; see Leads). None appeared in
  the sample: issue question 3.

## Findings: env files

Tools disagree on whether `.env` is committed, which is why the tag can't
imply "secret":

| Tool | `.env` | Local overrides | Per-environment | Template |
|---|---|---|---|---|
| dotenv (Node) | "Should I commit my `.env` file?" "No." Committing is recommended once encrypted with dotenvx | via `--file` | "one `.env` file per environment", e.g. `.env.production` | not mentioned |
| Next.js | "You almost never want to commit these files" | `.env.local`, `.env.$(NODE_ENV).local`; "`.env*.local` are intended to be ignored" | `.env.development`, `.env.production`, `.env.test` ("should be included in your repository") | — |
| Vite | loaded in all cases | `.env.local`, `.env.[mode].local`: "local-only and can contain sensitive variables" | `.env.[mode]` | — |
| Docker Compose | "placed at the root of the project directory next to your `compose.yaml`"; other names via `--env-file` | — | — | — |
| Laravel | "should not be committed" | — | `.env.[APP_ENV]` | `.env.example`: keep "including and updating the `.env.example` file" with placeholder values. `.env.encrypted` "may be placed in source control safely" |
| Symfony (8.1) | "This file should be committed to your repository", defaults only | `.env.local`, `.env.<environment>.local`: "should not be committed" | `.env.<environment>`: "these files _are_ committed" | — |

- **Encrypted forms.** Laravel's `.env.encrypted` and dotenv's encrypted
  `.env.production` are meant to be committed. dotenv's README says
  encrypted production keys "are stored in `.env.keys`", so `.env.keys`
  holds decryption keys, not variables.
- **Symfony's `.env.local.php`** is a compiled PHP cache of all the env
  files. Its extension makes it `PHP`.
- **direnv's `.envrc`** is a different convention: "This file is bash code
  that is going to be loaded by direnv", found in "current and parent
  directories". One of its documented uses is to "Load secrets for
  deployment". direnv can also read a `.env` file.

## Proposal

### Tags

Generic and lowercase, like `binary`, `license`, `config`:

| Tag | Meaning | New? |
|---|---|---|
| `certificate` | holds certificates | new |
| `key` | a private or public key file | new |
| `keystore` | a container of keys and certificates, or of credentials | new |
| `dotenv` | a dotenv-format environment file | new (decision 1) |
| `PEM`, `DER` | the encoding, where the extension doesn't say what is encoded | new (decision 3) |
| `template` | a committed example of a file meant to be filled in | new |
| `SSH`, `PuTTY`, `KeePass` | the tool whose format it is, as `Java` is for keystores | new |
| `security` | security-relevant file | existing (Dependabot) |
| `binary`, `config` | as today | existing |

### Rules

| Files | Tags | Filetype |
|---|---|---|
| `*.pem` | `PEM`, `security` | PEM |
| `*.crt`, `*.cer` | `certificate`, `security` | X.509 Certificate |
| `*.der` | `DER`, `security`, `binary` | DER |
| `*.p7b`, `*.p7c` | `certificate`, `security` | PKCS #7 |
| `*.crl` | `certificate`, `security` | Certificate Revocation List |
| `*.csr` | `certificate`, `security` | Certificate Signing Request |
| `*.key` | `key`, `security` | Key |
| `id_rsa`, `id_ecdsa`, `id_ecdsa_sk`, `id_ed25519`, `id_ed25519_sk`, `id_mldsa44_ed25519`, legacy `id_dsa` | `key`, `security`, `SSH` | SSH Private Key |
| `*.pub` | `key` (no `security`) | Public Key |
| `*.ppk` | `key`, `security`, `PuTTY` | PuTTY Private Key |
| `*.p12`, `*.pfx` | `keystore`, `certificate`, `key`, `security`, `binary` | PKCS #12 |
| `*.jks`, `*.keystore` | `keystore`, `security`, `binary`, `Java` | Java KeyStore |
| `*.kdbx` | `keystore`, `security`, `binary`, `KeePass` | KeePass Database |
| `.env`, `.env.<name>` | `dotenv`, `config` | dotenv |
| `.env.local`, `.env.<name>.local` | `dotenv`, `config` (the same; see decision 4) | dotenv |
| `.env.example`, `.env.sample`, `.env.template`, and any `.env.<name>.example` / `.sample` / `.template` | `dotenv`, `config`, `template` | dotenv |
| `.env.keys` | `dotenv`, `key`, `security` | dotenv |
| `.env.encrypted` | `dotenv`, `config` | dotenv |

`.env` variants are a function rule, as `pylock.<name>.toml` is: `.env`
optionally followed by `.<anything>` (`^\.env(\..+)?$`). The last segment
decides the extras: `example`, `sample` or `template` adds `template`, and
`.env.keys` adds `key` and `security`. Symfony's `.env.local.php` fits the
pattern but is PHP, so it is excluded. `.envrc` and `benchmarks.env` don't
fit it.

### Not proposed

| Candidate | Why |
|---|---|
| `*.asc` | OpenPGP armor of any kind; signatures are the common case. Tagging it `key` would mislabel every release signature |
| `*.env` (`benchmarks.env`, `.xcode.env`) | Not the dotenv convention; other tools' names |
| `.env.local.php` | Symfony's compiled cache. It is PHP, and a `*.php` rule would be wrong; candidate for a later exact rule |
| `.envrc` | direnv's bash script, not dotenv. Worth its own rule (`direnv`, `config`, filetype Shell), but outside this issue; see decision 6 |
| `*.p8` | PKCS #8 private keys (App Store Connect's `AuthKey_*.p8`). Apple's page couldn't be fetched, and only third-party pages confirm the name |
| `known_hosts`, `authorized_keys` | Public SSH data under `~/.ssh`, user-level, and not secret |
| `.netrc` | Credentials, but user-level (`~/.netrc`); no source fetched |

### Fixtures

Fixtures must not look like real keys, or secret scanners (GitHub push
protection, GitLeaks) will flag this repository. No `-----BEGIN ... KEY-----`
lines; plain placeholder text only.

## Decisions

Taken 2026-11-02; Peter's answers in brackets.

1. **`dotenv`, not the issue's `env`** [agreed]. It names the format every
   tool above uses, and leaves room for direnv's `.envrc` later. One
   pattern rule covers `.env` and every `.env.<name>`, so `.env.example`
   and `.env.local.example` match too.
2. **`security`** on keys, certificates and keystores, but not on public
   keys, templates or plain `.env` files [agreed]. Not every `.env` holds
   secrets: Symfony commits defaults.
3. **`.pem` is tagged `PEM`, not `certificate` and `key`** [Peter's
   change]. RFC 7468 defines nine labels and a file can hold several, so the
   path can't say whether it is a certificate, a key, a chain or a CSR.
   `PEM` says only what is known. The same applies to `.der`, a binary
   encoding of any of those (the sample has SCTs), so it is tagged `DER`.
   `.crt`, `.cer`, `.key` and `.p12`/`.pfx` keep their type tags, because
   an RFC or the extension's own name says what they hold. kospex looking
   for committed keys queries `key` or `PEM`.
4. **No tag for `.local` env files** [agreed]. "Should not be committed" is
   policy, and kospex can match the name.
5. **`.key` and `.pub` are tagged,** with the Keynote and Microsoft
   Publisher collisions documented [agreed].
6. **`.envrc` is a separate issue** [agreed]: it's a direnv tool rule.
7. **`.ppk`, `.kdbx`, `.csr`, `.crl`, `.p7b`, `.der` and `.env.keys` are
   included,** though #76 didn't list them [agreed].

## Implemented

The rules table above was implemented as decided, with `.pem` and `.der`
tagged `PEM` and `DER`.

- **Rule kinds.** The extensions are `extension_rules`, the OpenSSH names
  and `.env.keys` are exact-filename rules, and the dotenv pattern is two
  function rules in `core.py`. `is_dotenv()` matches `^\.env(\..+)?$` and
  skips `DOTENV_EXCLUDED` (`.env.local.php`, plus `.env.keys`, which has
  its own rule). `is_dotenv_template()` adds `template` when the last
  segment is `example`, `sample` or `template`.
- **`id_<type>.pub` names** get `SSH` from an exact rule, plus `key` from
  the `.pub` extension rule. Other `*.pub` files get `key` alone.
- **Filetypes.** dotenv files report `dotenv` through
  `get_language_edge_cases()`, as the `appsettings` variants report
  `JSONC`.
- **Vocabulary.** Ten new tags (`certificate`, `key`, `keystore`, `dotenv`,
  `template`, `PEM`, `DER`, `SSH`, `PuTTY`, `KeePass`), so 168 → 178. The
  fourteen new filetypes are all non-languages, so 117 → 131. A check
  found no case collision with any current or retired tag under a
  case-insensitive `LIKE`.
- **Docs.** `docs/cli.md` has a new *Keys, certificates and env files*
  section, which also says that kospex looking for private keys should
  query `key` or `PEM`.

**Fixtures** are in `tests/fixtures/secretsapp/`: 22 files of placeholder
text. None contains a `BEGIN … KEY` line or any key-like content, so secret
scanners won't flag the repository; a grep for `BEGIN` and `PRIVATE` finds
none. The repository's `.gitignore` ignores `.env`, so it has a narrow
exception, `!tests/fixtures/secretsapp/.env`, like the `.warp/` fixtures.

**Tests** are in `tests/test_keys_certificates_env.py`. 58 failed before the
rules were added; the 14 that passed are negative guards (`.asc`,
`.envrc`, `benchmarks.env`, `known_hosts`, lookalikes) and `.env.local.php`
staying `PHP`.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://www.rfc-editor.org/rfc/rfc7468.html> | PEM labels; multiple instances per file; `.crt` SHOULD, `.cer` common | 2026-11-02 |
| <https://www.rfc-editor.org/rfc/rfc8555.html> | `application/pem-certificate-chain`, extension `.pem` (§9.1) | 2026-11-02 |
| <https://www.rfc-editor.org/rfc/rfc2585.html> | `.cer` and `.crl` media types; one DER certificate per `.cer` | 2026-11-02 |
| <https://www.rfc-editor.org/rfc/rfc7292.html> | PKCS #12 contents; no extension named | 2026-11-02 |
| <https://learn.microsoft.com/en-us/previous-versions/bb416252(v=msdn.10)> | `.pfx`/`.p12` hold private keys; `.cer` and `.p7b` don't | 2026-11-02 (archived page, 2015-11-18) |
| <https://man.openbsd.org/ssh-keygen> | SSH private key names; `.pub` not secret | 2026-11-02 |
| <https://the.earth.li/~sgtatham/putty/0.83/htmldoc/Chapter8.html> | `.ppk` holds the private key | 2026-11-02 (PuTTY 0.83) |
| <https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html> | Default `~/.keystore`; storetype not tied to extension | 2026-11-02 (JDK 21) |
| <https://developer.android.com/studio/publish/app-signing> | `.jks`/`.keystore`; `$HOME/.android/debug.keystore`; `.der`/`.pem` certificates | 2026-11-02 |
| <https://www.rfc-editor.org/rfc/rfc9580.html> | OpenPGP armor header lines (§6.2.1); no extension | 2026-11-02 |
| <https://keepass.info/help/kb/kdbx.html> | KDBX stores user names and passwords | 2026-11-02 |
| <https://github.com/motdotla/dotenv> | `.env` at the root; don't commit; per-environment files; `.env.keys` | 2026-11-02 |
| <https://nextjs.org/docs/app/guides/environment-variables> | File names, load order, `.env*.local` ignored | 2026-11-02 (updated 2026-08-25) |
| <https://vite.dev/guide/env-and-mode> | `.env.[mode].local`; `*.local` in `.gitignore` | 2026-11-02 |
| <https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/> | `.env` beside `compose.yaml`; `--env-file` | 2026-11-02 |
| <https://laravel.com/docs/12.x/configuration> | `.env.example` committed with placeholders; `.env.encrypted` | 2026-11-02 (Laravel 12.x) |
| <https://symfony.com/doc/current/configuration.html> | `.env` committed with defaults; `.local` files not; `.env.local.php` | 2026-11-02 (Symfony 8.1) |
| <https://direnv.net/> | `.envrc` is bash; secrets use case | 2026-11-02 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://developer.apple.com/documentation/appstoreconnectapi/creating-api-keys-for-app-store-connect-api> | — | Content didn't load (script-rendered); `.p8` not proposed |
| <https://keepass.info/help/base/repair.html> | KDB/KDBX header holds decryption data | Background; `kdbx.html` used instead |
| <https://docs.fileformat.com/presentation/key>, <https://www.cleverfiles.com/howto/?p=9003>, <https://fileinfo.com/software/apple/keynote> | Keynote saves `.key` files | Third-party; the collision is noted, not confirmed by Apple |
| <https://learn.microsoft.com/archive/blogs/kaushal/various-ssltls-certificate-file-typesextensions> | `.p7b` "typically", "not always"; `.pfx` a relic name for PKCS #12 | Supports "extension doesn't fix contents" |
| <https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/cc770735(v=ws.10)> | PKCS #12 is the only export format with the private key | Not fetched; search summary only |
