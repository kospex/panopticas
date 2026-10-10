# C++ Source and Header Extensions

Closes [#43](https://github.com/kospex/panopticas/issues/43).

## Summary

`.cpp` was the only C++ extension in `EXT_FILETYPES`. Every other common
spelling reported `Unknown`:

    file.cc    'Unknown'        file.hpp   'Unknown'
    file.cxx   'Unknown'        file.hh    'Unknown'
    file.c++   'Unknown'        file.hxx   'Unknown'
                                file.h++   'Unknown'

A C++ codebase using `.cc` and `.hpp` — a very common pairing — showed no C++
at all. The gap surfaced during the `.m`/`.h` analysis in #40.

## Changes

Seven entries in `EXT_FILETYPES`, and `C++ Header` added to
`LANGUAGE_FILETYPES`:

    ".cc":  "C++"            ".hpp": "C++ Header"
    ".cxx": "C++"            ".hh":  "C++ Header"
    ".c++": "C++"            ".hxx": "C++ Header"
                             ".h++": "C++ Header"

## Source

The [GCC documentation](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)
lists the suffixes it treats as C++:

- **Source:** `.cc`, `.cp`, `.cxx`, `.cpp`, `.CPP`, `.c++`, `.C`
- **Header:** `.hh`, `.H`, `.hp`, `.hxx`, `.hpp`, `.HPP`, `.h++`, `.tcc`

## Design notes

- **`C++ Header` is a new language name**, paralleling the existing
  `C Header`. Headers are reported separately from sources because that is
  what panopticas already does for C. Reporting them as plain `C++` was the
  alternative; it would have been simpler but inconsistent with `.h`.
- **`.h` is unchanged.** It is shared by C, C++ and Objective-C — GCC's own
  entry for it reads "C, C++, Objective-C or Objective-C++ header file" — and
  cannot be resolved from the path. That is the subject of #40.
- Additive only: no existing mapping changes, so kospex is unaffected until a
  re-sync.

## Not mapped

The complete list of C++-related suffixes considered and left out, so none
needs rediscovering.

| Suffix | What it is | Reports as | Why not mapped |
|---|---|---|---|
| `.C` | C++ source (GCC, literal capital) | `C` | panopticas lowercases the extension before lookup, so it is indistinguishable from `.c` |
| `.H` | C++ header (GCC, literal capital) | `C Header` | Same: indistinguishable from `.h` |
| `.cp` | C++ source (GCC) | `Unknown` | Rare, and short enough to collide with unrelated uses |
| `.hp` | C++ header (GCC) | `Unknown` | Rare |
| `.tcc` | C++ header holding template definitions (GCC) | `Unknown` | Rare |
| `.ii` | C++ source that should not be preprocessed (GCC) | `Unknown` | Compiler output, not something a repository normally holds |
| `.ipp`, `.tpp`, `.inl`, `.txx` | Template and inline implementation files | `Unknown` | Project conventions rather than compiler-defined suffixes; not checked against any documentation |
| `.cppm`, `.ixx`, `.ccm`, `.mpp` | C++20 module interface units | `Unknown` | Vary by compiler; not checked against any compiler's documentation |
| `.h` | C, C++ or Objective-C header | `C Header` | Shared by three languages and not resolvable from the path — see #40 |

`.CPP` and `.HPP`, which GCC lists separately, need no entry: lowercasing
resolves them to `.cpp` and `.hpp`, so they report `C++` and `C++ Header`.

The first six rows are from the GCC suffix list above. The template and module
rows are from general knowledge and would need verifying before any of them
became a mapping.

## Tests

`tests/test_panopticas.py` covers all seven extensions, asserts `.h` still
reports `C Header`, and has a fixture for each extension in `src/tests/`.
