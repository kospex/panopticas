# Archives, Packages, Libraries, Databases, Backups and Dumps

For [#79](https://github.com/kospex/panopticas/issues/79).

**Status:** researched, not implemented. Verified 2026-11-02. The decisions
at the end are needed before implementing; some formats still need a
source (see *Unconfirmed*).

These are files that matter by being in the repository at all: a committed
installer, a database, a heap dump. Panopticas tags what the file is;
whether it should be committed, and how large is too large, is kospex's
call (detector, not policy). Path-based only.

## Current state

Only `.zip` and `.jar` (`binary`), `.exe` (`binary`) and `.dll` (`binary`,
`.NET`) are tagged today. Everything else below is `Unknown` with no tags.

Counts are from a local kospex database (376 repositories), current files
only:

| Extension | Files | Repos | | Extension | Files | Repos |
|---|---|---|---|---|---|---|
| `.gz` | 175 | 10 | | `.so` | 38 | 1 |
| `.zip` | 142 | 10 | | `.db` | 26 | 3 |
| `.bin` | 128 | 9 | | `.wasm` | 20 | 4 |
| `.jar` | 46 | 17 | | `.apk` | 17 | 2 |
| `.exe` | 11 | 3 | | `.o` | 11 | 2 |
| `.a` | 9 | 2 | | `.obj` | 4 | 3 |
| `.bak` | 4 | 1 | | `.aar` | 3 | 3 |
| `.whl`, `.aab`, `.dmg`, `.old` | 2 each | 1–2 | | `.lib`, `.swp` | 1 each | 1 |

`.tar.gz` appears 3 times. No `.tar`, `.7z`, `.rar`, `.war`, `.nupkg`,
`.dylib`, `.sqlite`, `.mdb`, `.hprof`, `.dmp`, `.heapsnapshot`, `core` or
`*~` files appear.

**kospex has no size for any of these files.** `Bytes` is 0 on every row
above, because size comes only from scc, which doesn't count binaries
(kospex/kospex#334). Until that is fixed, size can't catch a committed
dump, which makes the tags the only signal.

What the names show (basenames only; no file was opened):

- **Some are plainly committed by mistake or convenience:**
  `TypingMind-1.5.4.dmg` (an app installer), `index.js.bak` and
  `page.server.js.bak` (backups of source files), `.current.txt.swp` (a
  Vim swap file).
- **Most `.gz` files are compressed test data,** `expectedResults.json.gz`,
  not multi-file archives.
- **`.obj` files here are Windows object files** (`win64.obj`). `.obj` is
  also the Wavefront 3D model format, which is text.
- **`.bin` is generic:** model weights (`sparse_tensor.bin`), test inputs,
  and files named by their hash.
- **`.db` names are application caches** (`cache.db`, `v3.db`).
- **`.so`, `.a` and `.o` files are linker and debugger test fixtures**
  (`libtestelf-stripped-all.so`).

## Findings

### Archives and compression

- **gzip.** RFC 1952 defines "a lossless compressed data format" for "a
  data stream", which "consists of a series of 'members'". It names no
  suffix; gzip's man page says `-S` "changes the default suffix from .gz".
  gzip compresses one stream, so a `.gz` file is compressed data, not an
  archive of several files.
- **bzip2.** Each file "is replaced by a compressed version of itself, with
  the name "original_name.bz2"", and `filename.tbz2` and `filename.tbz`
  become `filename.tar`.
- **xz.** "The native file format is the .xz format, but the legacy .lzma
  format" is also handled; xz "also recognizes the suffixes .txz and .tlz,
  and replaces them with the .tar suffix".
- **zstd.** "When compressing, the suffix .zst is appended".
- **tar.** bsdtar's `-a` "Use[s] the archive suffix to decide a set of the
  format and the compressions": `archive.tgz` is a pax archive with gzip,
  `archive.tar.bz2` with bzip2. GNU tar's suffix table couldn't be fetched
  (403 and 429 responses).

So `.tar` is an archive, `.gz`, `.bz2`, `.xz`, `.lzma` and `.zst` are
compressed data, and `.tgz`, `.tbz`, `.tbz2`, `.txz`, `.tlz` and
`.tar.<compression>` are both.

### Packages

- **Wheel:** "A wheel is a ZIP-format archive with a specially formatted
  file name and the .whl extension." The spec mentions the older "egg
  binary formats" only in passing.
- **NuGet:** "a NuGet package is a single ZIP file with the `.nupkg`
  extension that contains compiled code (DLLs)".
- **Cargo:** `cargo package` will "create a distributable, compressed
  `.crate` file", "stored in the `target/package` directory".
- **RubyGems:** `gem build` prints "File: hola-0.0.0.gem".
- **JAR:** "a file format based on the popular ZIP file format and is used
  for aggregating many files into one."
- **Android:** "an Android library compiles into an Android Archive (AAR)
  file that you can use as a dependency", "instead of compiling into an APK
  that runs on a device". "An Android App Bundle is a publishing format that
  includes all your app's compiled code and resources, and defers APK
  generation and signing to Google Play."

### Native libraries and objects

- **macOS `ld`:** `-lx` "tells the linker to search for libx.dylib or
  libx.a".
- **`ar`:** "creates and maintains groups of files combined into an
  archive", which is what a static `.a` library is.
- **Linux shared libraries** (Program Library HOWTO): the soname is
  `lib<name>.so.<version>`, the real name adds minor and release numbers
  (`libreadline.so.3.0`), and the linker name is the bare `.so`.
  Versioned names (`libfoo.so.1`) end in a number, so an extension rule
  on `.so` doesn't match them.
- **GCC:** "the object file name for a source file is made by replacing the
  suffix ‘.c’, ‘.i’, ‘.s’, etc., with ‘.o’."
- **MSVC LIB:** "creates and manages a library of Common Object File Format
  (COFF) object files"; `/EXTRACT` "Create[s] an object (.obj) file". LIB
  also creates import libraries, which are `.lib` too.

### Databases

- **SQLite:** "SQLite does not have any file naming requirements and so the
  application can use any custom file suffix that it wants". So `.sqlite`,
  `.sqlite3` and `.db` are conventions, not SQLite's. `.db` is also used by
  other engines and by Windows' `Thumbs.db` thumbnail cache.

### Backups and editor leftovers

- **patch:** "By default the original file is saved with a backup extension
  of ".orig"", and a hunk that can't be applied goes to "a reject file,
  which normally is the name of the output file plus ".rej"".
- **Vim swap files:** the name is "normally the same as the file you are
  editing, with the extension ".swp""; "On Unix, a '.' is prepended"; if
  the name is taken, ""..swo", ".swn", etc." is used.
- **Vim backups:** `backupext` is "String which is appended to a file name
  to make the name of the backup file", default `"~"`. The help adds: "You
  might prefer using ".bak"". Emacs's backup naming page couldn't be
  fetched (403).

### Dumps

- **JVM heap dumps:** with `-XX:+HeapDumpOnOutOfMemoryError`, "the heap
  dump is created in a file called `java_pid<pid>.hprof` in the working
  directory of the VM"; the example dump is 531,535,128 bytes.
- **Windows minidumps:** "user-mode minidump files, which contain a useful
  subset of the information contained in a crash dump file". A full
  user-mode dump includes "The entire memory space of a process". Neither
  Microsoft page fetched names the `.dmp` extension.
- **Node.js heap snapshots:** `v8.writeHeapSnapshot()` "writes it to a JSON
  file", by default `Heap-${yyyymmdd}-${hhmmss}-${pid}-${thread_id}.heapsnapshot`.
  This one is text, not binary.
- **`core`** and **`.pmem`:** left out, as the issue recommends (questions 4
  and 5). `core` is also a common directory name, and `.pmem` has no
  documented format.

## Proposal

### Kind tags

The issue proposed five kinds. The findings split two of them:

| Tag | Meaning | Files |
|---|---|---|
| `archive` | several files in one container | `.tar`, `.zip`, `.tgz`, `.tar.*` |
| `compressed` | one compressed stream | `.gz`, `.bz2`, `.xz`, `.lzma`, `.zst`, and the tarball forms |
| `package` | a built distributable for a package manager or app store | `.whl`, `.nupkg`, `.crate`, `.gem`, `.jar`, `.aar`, `.apk`, `.aab` |
| `library` | a shared or static native library | `.so`, `.dylib`, `.a`, `.lib`, `.dll` |
| `object` | a compiled object file | `.o`, `.obj` |
| `database` | a database file | `.sqlite`, `.sqlite3`, `.db` |
| `backup` | a backup or editor leftover | `.bak`, `.orig`, `*~`, `.swp`, `.swo`, `.swn` |
| `dump` | a memory or heap dump | `.hprof`, `.dmp`, `.heapsnapshot` |

### Rules

| Files | Tags | Filetype |
|---|---|---|
| `.tar` | `archive`, `binary` | Tar Archive |
| `.tgz`, `.tbz`, `.tbz2`, `.txz`, `.tlz`, `*.tar.gz`, `*.tar.bz2`, `*.tar.xz`, `*.tar.zst`, `*.tar.lzma` | `archive`, `compressed`, `binary` | Tar Archive |
| `.gz` | `compressed`, `binary` | Gzip |
| `.bz2` | `compressed`, `binary` | Bzip2 |
| `.xz`, `.lzma` | `compressed`, `binary` | XZ |
| `.zst` | `compressed`, `binary` | Zstandard |
| `.zip` | gains `archive` | ZIP (unchanged) |
| `.whl` | `package`, `binary`, `Python`, `PyPI` | Python Wheel |
| `.nupkg` | `package`, `binary`, `.NET`, `NuGet` | NuGet Package |
| `.crate` | `package`, `binary`, `Rust`, `crates.io` | Crate |
| `.gem` | `package`, `binary`, `Ruby`, `RubyGems` | Gem |
| `.jar` | gains `package` | Java Archive (unchanged) |
| `.aar` | `package`, `binary`, `Android` | Android Archive |
| `.apk` | `package`, `binary`, `Android` | Android Package |
| `.aab` | `package`, `binary`, `Android` | Android App Bundle |
| `.so`, `.dylib` | `library`, `binary` | Shared Library |
| `.a`, `.lib` | `library`, `binary` | Static Library |
| `.dll` | gains `library` | DLL (unchanged) |
| `.o`, `.obj` | `object`, `binary` | Object File |
| `.sqlite`, `.sqlite3`, `.db` | `database`, `binary` | Database |
| `.bak`, `.orig` | `backup` | Backup |
| `*~` | `backup` | Backup |
| `.swp`, `.swo`, `.swn` | `backup`, `Vim` | Vim Swap File |
| `.hprof` | `dump`, `binary`, `Java` | Heap Dump |
| `.dmp` | `dump`, `binary` | Minidump |
| `.heapsnapshot` | `dump`, `JavaScript` | JSON |

The tarball forms need a function rule, since `splitext` gives `.gz` for
`x.tar.gz`. `*~` is also a function rule. Backups carry no `binary`, since
they are often text (issue question 2). New tags: `archive`, `compressed`,
`package`, `library`, `object`, `database`, `backup`, `dump`, `Android` and
`Vim`.

### Unconfirmed

These are candidates, but no official source naming the extension could be
fetched:

| Candidate | What was tried | Recommendation |
|---|---|---|
| `.7z` | 7-zip.org didn't resolve | Confirm before adding |
| `.rar` | not fetched | Confirm before adding |
| `.war`, `.ear` | Jakarta Servlet 6.0 spec is too long to fetch to section 10.6 | Confirm before adding |
| `.mdb`, `.accdb` | Microsoft's Access page returned 404 | Confirm before adding |
| `.duckdb` | DuckDB's page only redirected | Confirm before adding |
| `.wasm` | MDN describes the binary format but not the extension; the W3C spec was too large to fetch | Confirm before adding (20 files in the sample) |
| `.dmp` | Microsoft's pages describe minidumps but don't name `.dmp` | Included above; see decision 5 |
| `.dmg`, `.iso`, `.msi`, `.deb`, `.rpm`, `.ipa`, `.egg`, `.pyc` | not researched | A later pass |

### Not proposed

| Candidate | Why |
|---|---|
| `.bin` | Generic: weights, firmware, test inputs, hashes |
| `.old`, `.tmp` | Generic suffixes, no tool convention found |
| `.rej` | A patch reject, not a backup; a candidate for its own tag later |
| `core`, `core.<pid>` | Also a common directory name (question 4) |
| `.pmem` | No documented format (question 5) |
| `libfoo.so.1` (versioned) | The extension is the number; a pattern rule could catch it later |

## Decisions needed

1. **Kinds: eight, not five.** The issue had `archive`, `library`,
   `database`, `backup` and `dump`. *Recommendation:* split `compressed`
   from `archive` (a `.gz` is one stream, RFC 1952), and add `package`
   (wheels, crates, APKs) and `object` (`.o`/`.obj` aren't libraries).
   Tarballs carry both `archive` and `compressed`.
2. **Ecosystem tags on packages** (issue question 6). *Recommendation:*
   yes, following #73: `.whl` → `Python`, `PyPI`; `.nupkg` → `.NET`,
   `NuGet`; `.crate` → `Rust`, `crates.io`; `.gem` → `Ruby`, `RubyGems`.
   Android files get a new `Android` tag.
3. **Existing tags gain a kind.** `.zip` gains `archive`, `.jar`
   `package`, and `.dll` `library`. *Recommendation:* yes; it only adds
   tags.
4. **`.db` is generic.** SQLite documents no suffix, and `.db` also covers
   Windows' `Thumbs.db` and other engines. *Recommendation:* tag it
   `database`, as `.key` was tagged despite Keynote, and document it.
5. **`.dmp`** has no official page naming it. *Recommendation:* include it;
   it is the extension WinDbg, ProcDump and Windows Error Reporting are
   known for. Or leave it unconfirmed like the others; your call, since it
   breaks the "confirmed source" rule.
6. **The unconfirmed formats.** *Recommendation:* leave them out of this
   PR, and do a second research pass (`.7z`, `.rar`, `.war`/`.ear`,
   `.mdb`/`.accdb`, `.duckdb`, `.wasm`, then the installers) as a
   follow-up issue.
7. **`.obj` collides** with Wavefront 3D models, which are text.
   *Recommendation:* tag it `object`, `binary` anyway; all four in the
   sample are COFF objects. Document the collision.

## Sources

| Page | Used for | Checked |
|---|---|---|
| <https://www.rfc-editor.org/rfc/rfc1952.html> | gzip is one compressed stream of members; no suffix | 2026-11-02 |
| `gzip(1)`, Apple gzip 487.0.1 | default suffix `.gz` | 2026-11-02 |
| `bzip2(1)` (macOS) | `.bz2`; `.tbz2`/`.tbz` become `.tar` | 2026-11-02 |
| `xz(1)`, XZ Utils 5.8.3 | `.xz`, `.lzma`; `.txz`/`.tlz` become `.tar` | 2026-11-02 |
| `zstd(1)`, v1.5.7 | `.zst` | 2026-11-02 |
| `tar(1)`, bsdtar 3.5.3 | `-a` picks format and compression from the suffix (`.tgz`, `.tar.bz2`) | 2026-11-02 |
| <https://packaging.python.org/en/latest/specifications/binary-distribution-format/> | `.whl` is a ZIP-format archive | 2026-11-02 |
| <https://learn.microsoft.com/en-us/nuget/what-is-nuget> | `.nupkg` is a single ZIP file | 2026-11-02 (updated 2026-03-03) |
| <https://doc.rust-lang.org/cargo/commands/cargo-package.html> | `.crate`, a compressed tarball in `target/package` | 2026-11-02 |
| <https://guides.rubygems.org/make-your-own-gem/> | `gem build` output `hola-0.0.0.gem` | 2026-11-02 |
| <https://docs.oracle.com/en/java/javase/21/docs/specs/jar/jar.html> | JAR is ZIP-based, aggregates files | 2026-11-02 (JDK 21) |
| <https://developer.android.com/studio/projects/android-library> | AAR versus APK and JAR | 2026-11-02 |
| <https://developer.android.com/guide/app-bundle> | Android App Bundle | 2026-11-02 |
| `ld(1)`, Apple command line tools | `-lx` finds `libx.dylib` or `libx.a` | 2026-11-02 |
| `ar(1)`, Apple command line tools | `ar` builds archives | 2026-11-02 |
| <https://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html> | `.so` soname, real name and linker name | 2026-11-02 |
| <https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html> | object files are `.o` | 2026-11-02 |
| <https://learn.microsoft.com/en-us/cpp/build/reference/lib-reference> | LIB manages libraries of COFF objects | 2026-11-02 |
| <https://learn.microsoft.com/en-us/cpp/build/reference/overview-of-lib> | `/EXTRACT` creates an `.obj` | 2026-11-02 |
| <https://www.sqlite.org/appfileformat.html> | SQLite has no file naming requirements | 2026-11-02 |
| `patch(1)`, Apple patch 2.0-12u11 | `.orig` backups, `.rej` rejects | 2026-11-02 |
| <https://vimhelp.org/recover.txt.html> | `.swp`, leading dot on Unix, `.swo`/`.swn` | 2026-11-02 |
| <https://vimhelp.org/options.txt.html> | `backupext` default `~`; `.bak` as an alternative | 2026-11-02 |
| <https://docs.oracle.com/en/java/javase/21/troubleshoot/command-line-options1.html> | `java_pid<pid>.hprof` | 2026-11-02 (JDK 21) |
| <https://learn.microsoft.com/en-us/windows/win32/debug/minidump-files> | what a minidump is; no extension | 2026-11-02 (updated 2025-07-16) |
| <https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/user-mode-dump-files> | full dumps include the whole process memory; no extension | 2026-11-02 (updated 2025-07-18) |
| <https://nodejs.org/api/v8.html> | `.heapsnapshot` is JSON; default name | 2026-11-02 |

### Leads, not used as confirmation

| Page | What it said | Outcome |
|---|---|---|
| <https://www.gnu.org/software/tar/manual/html_section/Compression.html> | — | 429, then 403 to curl; bsdtar's man page used instead |
| <https://www.gnu.org/software/tar/manual/html_section/gzip.html> | Only a heading and a link | Not useful |
| <https://www.gnu.org/software/diffutils/manual/html_node/Backups.html>, <https://www.gnu.org/software/diffutils/manual/html_node/Reject-Names.html> | — | 429; `patch(1)` used instead |
| <https://www.gnu.org/software/emacs/manual/html_node/emacs/Backup-Names.html> | — | 403; Vim's `backupext` used for `~` |
| <https://guides.rubygems.org/what-is-a-gem/> | Only the gemspec | `make-your-own-gem` used instead |
| <https://developer.apple.com/library/archive/documentation/DeveloperTools/Conceptual/DynamicLibraries/100-Articles/OverviewOfDynamicLibraries.html> | Describes dynamic and static libraries; no extensions | `ld(1)` used instead |
| <https://docs.oracle.com/en/java/javase/21/troubleshoot/troubleshooting-tools.html> | Index page only | `command-line-options1.html` used instead |
| <https://jakarta.ee/specifications/servlet/6.0/jakarta-servlet-spec-6.0> (404), <https://jakarta.ee/specifications/servlet/6.0/jakarta-servlet-spec-6.0.html> | Section 10.6 past the fetch limit | `.war` unconfirmed |
| <https://www.7-zip.org/7z.html> | — | Didn't resolve; `.7z` unconfirmed |
| <https://duckdb.org/docs/stable/connect/overview> | Redirect only | `.duckdb` unconfirmed |
| <https://support.microsoft.com/en-us/office/introduction-to-access-databases-ef5e5c3f-c86a-4e0f-87fb-a5ec05e3f9e6> | — | 404; `.mdb`/`.accdb` unconfirmed |
| <https://developer.mozilla.org/en-US/docs/WebAssembly/Guides/Concepts> | The binary format, but not the extension | `.wasm` unconfirmed |
| <https://www.w3.org/TR/wasm-core-2/> | — | Too large to fetch |
