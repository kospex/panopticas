# Line Counting Feature Implementation - July 7, 2025

## Overview

This document details the implementation of optional line counting functionality in panopticas, allowing users to display line counts for each file in the `assess` command using a new `--lines` CLI flag. The implementation uses separate functions to ensure 100% backward compatibility.

## Feature Description

The line counting feature adds the ability to count and display the number of lines in each file when assessing a directory. This provides additional insight into codebase metrics and file sizes. The feature is implemented using separate functions to avoid any breaking changes to existing APIs.

## Implementation Details

### 1. Core Function - `count_lines()`

**Location**: `src/panopticas/core.py`

```python
def count_lines(file_path):
    """
    Count the number of lines in a file.
    
    Args:
        file_path (str): Path to the file to count lines in
        
    Returns:
        int or str: Number of lines in the file, or "N/A" for binary files or errors
    """
```

**Key Features:**
- Efficient line counting without loading entire files into memory using `sum(1 for _ in file)`
- Handles UTF-8 encoding gracefully
- Returns "N/A" for binary files, encoding errors, or other exceptions
- Robust error handling for file access issues

### 2. Separate Functions for Backward Compatibility

**Location**: `src/panopticas/core.py`

**Design Decision:**
To ensure 100% backward compatibility and avoid breaking changes, the implementation uses two separate functions instead of modifying the existing `identify_files()` function.

#### **Original Function (Unchanged)**
```python
def identify_files(directory):
    """Identify files in a directory. Returns a dict of relative path filenames to their file_type"""
    # Returns: {relative_path: file_type}
```

#### **New Function (Enhanced)**
```python
def identify_files_with_metrics(directory):
    """Identify files with additional metrics including line counts."""
    # Returns: {relative_path: {'type': file_type, 'lines': line_count}}
```

**Benefits of This Approach:**
- ✅ Zero breaking changes for existing applications
- ✅ Clear API intentions through function names
- ✅ Opt-in enhancement model
- ✅ Future-proof for additional metrics

### 3. CLI Enhancement

**Location**: `src/panopticas/cli.py`

**New Option:**
```bash
@click.option('--lines', is_flag=True, default=False, help="Include line count for each file.")
```

**Changes:**
- Added `--lines` flag to the `assess` command
- CLI automatically selects appropriate function based on flag:
  - Without `--lines`: Uses `identify_files()` (original behavior)
  - With `--lines`: Uses `identify_files_with_metrics()` (enhanced data)
- Dynamic table header generation based on flag presence
- Updated table row generation to handle both data structures
- Right-aligned line count column for better readability

### 4. Package Exports

**Location**: `src/panopticas/__init__.py`

- Added `count_lines` to the exported functions list
- Added `identify_files_with_metrics` to the exported functions list
- Both functions available for programmatic use:
  - `import panopticas; panopticas.count_lines(file_path)`
  - `import panopticas; panopticas.identify_files_with_metrics(directory)`

## Usage Examples

### CLI Usage

```bash
# Basic assessment (existing behavior)
panopticas assess

# Assessment with line counts
panopticas assess --lines

# Specific directory with line counts
panopticas assess /path/to/directory --lines

# Combine with other flags
panopticas assess --lines -unknown
```

### Programmatic Usage

```python
import panopticas

# Count lines in a single file
line_count = panopticas.count_lines("README.md")

# Original function (backward compatible)
files = panopticas.identify_files(".")
for file_path, file_type in files.items():
    print(f"{file_path}: {file_type}")  # Works exactly as before

# New function with enhanced metrics
files_with_metrics = panopticas.identify_files_with_metrics(".")
for file_path, info in files_with_metrics.items():
    print(f"{file_path}: {info['type']} ({info['lines']} lines)")
```

## Table Output Comparison

### Without --lines Flag (Existing)
```
+--------------------------------------+----------------+-----------------------------+
| File                                 | Language       | Meta                        |
+--------------------------------------+----------------+-----------------------------+
| README.md                            | Markdown       |                             |
| pyproject.toml                       | TOML           | build, dependencies, Python |
+--------------------------------------+----------------+-----------------------------+
```

### With --lines Flag (New)
```
+--------------------------------------+----------------+-----------------------------+-------+
| File                                 | Language       | Meta                        | Lines |
+--------------------------------------+----------------+-----------------------------+-------+
| README.md                            | Markdown       |                             |    31 |
| pyproject.toml                       | TOML           | build, dependencies, Python |    27 |
+--------------------------------------+----------------+-----------------------------+-------+
```

## Technical Considerations

### Performance
- **Efficient Implementation**: Uses generator expression `sum(1 for _ in file)` to avoid loading entire files into memory
- **On-Demand Processing**: Line counting only performed when `--lines` flag is used
- **Scalable**: Handles large files efficiently without memory issues

### Error Handling
- **Binary Files**: Returns "N/A" for files that cannot be decoded as UTF-8
- **Missing Files**: Gracefully handles file not found errors
- **Encoding Issues**: Catches and handles `UnicodeDecodeError` exceptions
- **General Robustness**: Catches all other exceptions to prevent crashes

### Backward Compatibility
- **CLI Interface**: Existing commands work unchanged
- **API Interface**: `identify_files()` maintains exact original behavior with no changes
- **Data Structures**: Original return format completely preserved in original function
- **Breaking Change Elimination**: Separate functions ensure no existing code can break

## Testing Results

### Accuracy Verification
- Line counts verified against system `wc -l` command
- Perfect accuracy match for all tested files
- Consistent results across different file types

### Edge Case Testing
- ✅ Binary files properly return "N/A"
- ✅ Empty files correctly return 0 lines
- ✅ Large files handled efficiently
- ✅ Files with various encodings handled gracefully

### Compatibility Testing
- ✅ Existing CLI commands unchanged
- ✅ Flag combinations work correctly (`--lines -unknown`)
- ✅ Different directory structures supported
- ✅ Programmatic API maintains 100% compatibility
- ✅ Original function returns exact same data structure
- ✅ New function provides enhanced data structure
- ✅ No breaking changes for any existing applications

## Benefits

1. **Enhanced Analysis**: Provides additional codebase metrics for better understanding
2. **Optional Feature**: Non-intrusive implementation that doesn't affect existing workflows
3. **Efficient Performance**: Optimized for handling large codebases
4. **Robust Error Handling**: Gracefully handles edge cases and errors
5. **Consistent Interface**: Integrates seamlessly with existing CLI patterns

## Files Modified

1. **`src/panopticas/core.py`**
   - Added `count_lines()` function
   - Added `identify_files_with_metrics()` function (new, separate from original)
   - Restored `identify_files()` to original implementation (no parameters, original behavior)

2. **`src/panopticas/cli.py`**
   - Added `--lines` CLI option
   - Updated CLI logic to choose appropriate function based on flag
   - Updated table display logic for dynamic columns

3. **`src/panopticas/__init__.py`**
   - Added `count_lines` to package exports
   - Added `identify_files_with_metrics` to package exports

## API Design Summary

### Original API (Unchanged)
```python
# Existing applications continue to work exactly as before
files = panopticas.identify_files(directory)
# Returns: {"file.py": "Python", "README.md": "Markdown"}

for file_path, file_type in files.items():
    print(f"{file_path}: {file_type}")  # ✅ No changes needed
```

### Enhanced API (New)
```python
# New applications can opt into enhanced functionality
files = panopticas.identify_files_with_metrics(directory)
# Returns: {"file.py": {"type": "Python", "lines": 100}}

for file_path, info in files.items():
    print(f"{file_path}: {info['type']} ({info['lines']} lines)")
```

## Conclusion

The line counting feature successfully enhances panopticas with valuable codebase metrics while maintaining 100% backward compatibility through the use of separate functions. This design eliminates any possibility of breaking changes and follows the principle of least surprise. The implementation provides performance optimization, robust error handling, and a clear upgrade path for applications that want enhanced functionality, establishing a solid foundation for future analytical features.