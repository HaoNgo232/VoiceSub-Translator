# Clean Architecture Migration Plan

## 🧹 Files Cleanup Status

### ✅ Completed - Removed
- [x] debug_import.py, debug_subtitle.py (dev test files)
- [x] test_basic.py, test_parsing.py, validate_architecture.py (temp tests)
- [x] quick_test.py, project_summary.py (analysis utilities)
- [x] course_processing.log (empty log file)
- [x] __pycache__ directories (Python cache)

### 🚧 ACTIVE Components - Do NOT Remove

#### 🔴 HIGH PRIORITY - Need Migration
- **src/translator/** (4 files) - Legacy translation logic
  - Used by: GUI, utils, tests
  - Replace with: Clean Architecture
  
- **src/gui/** (6 files) - Main application interface
  - Used by: Main app entry point
  - Update to: Use TranslationFacade
  
- **src/api/** (15 files) - API handlers and providers
  - Used by: GUI, utils, tests
  - Integrate with: New ProviderService

#### 🟡 MEDIUM PRIORITY - Review Needed  
- **src/utils/** (13 files) - Utility functions
  - Some overlap with new architecture (cache, subtitle management)
  - Review each for integration potential

#### 🟢 LOW PRIORITY - Keep As Is
- **src/processor/** (2 files) - Video processing (separate concern)
- **src/scripts/** (3 files) - Standalone utility scripts

## 🎯 Current Status Summary

**✅ Clean Architecture**: Hoàn thành và tested
- Core Domain Layer (5 files)
- Application Layer (8 files) 
- Infrastructure Layer (12 files)
- Integration Layer (1 file)

**⏳ Migration Status**: Ready but pending
- Legacy adapter created for smooth transition
- Backward compatibility ensured
- No functionality will be lost

**💡 Safe Strategy**: 
- DON'T remove anything yet
- START with GUI migration first
- TEST thoroughly at each step
- Remove legacy code only after migration complete

## 🚀 Immediate Next Steps
1. Test new Clean Architecture with real translation
2. Migrate one GUI component as proof of concept
3. Gradually replace legacy imports
4. Clean up legacy code (final step)
