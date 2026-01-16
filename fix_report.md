# Test Error Fix Report

## Summary

Fixed compatibility issues in `tests/test_netlist.py` and dependency specifications that caused test failures in the GitHub Actions CI environment due to NetworkX version incompatibilities with the `netlistx` library.

## Problem Description

### Error Details

The following tests were failing in the CI environment:

- `tests/test_FMBiPartMgr.py::test_FMBiPartMgr[<lambda>-list]`
- `tests/test_FMKWayPartMgr.py::test_FMKWayPartMgr[<lambda>-5-list]`
- `tests/test_MLPartMgr.py::test_MLBiPartMgr2`
- `tests/test_MLPartMgr.py::test_MLKWayPartMgr`
- `tests/test_netlist.py::test_json`
- `tests/test_netlist.py::test_json2`
- `tests/test_netlist.py::test_readjson`

### Root Cause

The issue was a breaking change in NetworkX 3.4+ that affected the `netlistx.read_json()` function:

**NetworkX 3.4+ Breaking Change:**
- The `link` parameter was deprecated in favor of `edges`
- When both `edges` and `link` are `None` (default), NetworkX 3.4+ doesn't know where to look for edge data
- The `netlistx.read_json()` function converts 'links' to 'edges' but doesn't specify the `edges="edges"` parameter when calling `node_link_graph()`

**Dependency Issue:**
- The requirements specified `networkx>=2.1`, allowing any version from 2.1 onwards
- The CI environment was installing NetworkX 3.4+ which is incompatible with the current version of `netlistx`

## Solution

### 1. Fixed Test Files

Modified `tests/test_netlist.py` to convert 'links' to 'edges' in the JSON data before passing it to `node_link_graph()`. This approach:

1. Works with both NetworkX 2.x and 3.x
2. Follows the same pattern used in the `netlistx.read_json()` function
3. Eliminates the need for version-specific parameter handling

**File:** `tests/test_netlist.py`

**Modified Functions:**
- `test_json()`
- `test_json2()`

**Change Pattern:**
```python
# Before
ugraph = json_graph.node_link_graph(data, edges="links")

# After
if "links" in data and "edges" not in data:
    data["edges"] = data.pop("links")
ugraph = json_graph.node_link_graph(data)
```

### 2. Pinned NetworkX Version

Updated dependency specifications to pin NetworkX to versions <3.4 to avoid breaking changes:

**Files Modified:**
- `requirements/default.txt`
- `setup.cfg`

**Change:**
```
# Before
networkx>=2.1

# After
networkx>=2.1,<3.4
```

This ensures that the CI environment installs a NetworkX version that is compatible with the current version of `netlistx`.

## Verification

### Test Results

All 39 tests now pass successfully:
```
======================= 39 passed in 109.94s (0:01:49) ========================
```

### Code Coverage

Overall coverage: 97%
- 869 statements
- 28 missed
- 336 branches
- 4 branch parts missed

## Environment Details

- **Python Version:** 3.12.4 (local), 3.10.19 (CI)
- **NetworkX Version:** 3.6.1 (local), will be pinned to <3.4 in CI
- **Test Framework:** pytest 8.3.2
- **Operating System:** Windows 10 (win32)

## Recommendations

To prevent similar issues in the future:

1. **Update netlistx:** The `netlistx` library should be updated to specify `edges="edges"` when calling `node_link_graph()` to support NetworkX 3.4+
2. **Version Testing:** Add tests that verify compatibility with supported NetworkX versions
3. **Documentation:** Document the NetworkX version requirements in the project README

## Files Modified

- `tests/test_netlist.py` - Updated `test_json()` and `test_json2()` functions
- `requirements/default.txt` - Pinned NetworkX to version <3.4
- `setup.cfg` - Updated install_requires to pin NetworkX to version <3.4

## Files Deleted

- `err.log` - Cleaned up error log file after fixes were verified
- `err2.log` - Cleaned up error log file after fixes were verified