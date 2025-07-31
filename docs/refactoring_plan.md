# VoiceSub-Translator Refactoring Plan 🛠️

## 🔍 Current Issues Analysis

### 1. Duplicate TranslationService Classes
**Problem:** 
- `src/api/translation_service.py` - Handles provider selection & rate limiting
- `src/translator/translator_service.py` - Abstract interface + API implementation

**Solution:** Merge into proper layered architecture

### 2. Missing Translation Strategy Pattern
**Problem:** Context-aware translation can't be easily plugged in
**Solution:** Implement Strategy Pattern for different translation approaches

### 3. Tightly Coupled Translation Logic
**Problem:** Translation logic scattered across multiple files
**Solution:** Centralize translation orchestration with proper dependency injection

## 🎯 Refactored Architecture

```
src/
├── core/                          # Core domain entities & interfaces  
│   ├── interfaces/
│   │   ├── translation_strategy.py    # Strategy interface
│   │   ├── provider_interface.py      # Provider interface
│   │   └── transcription_interface.py # Transcription interface
│   └── entities/
│       ├── subtitle_block.py          # Domain entity
│       └── translation_context.py     # Context entity
│
├── infrastructure/                # External concerns (APIs, storage)
│   ├── providers/                 # API providers (moved from src/api/providers)
│   ├── cache/                     # Cache implementations
│   └── transcription/             # Whisper implementations
│
├── application/                   # Application layer (use cases)
│   ├── services/
│   │   ├── translation_service.py     # Main translation orchestrator
│   │   ├── transcription_service.py   # Main transcription orchestrator
│   │   └── subtitle_service.py        # Main subtitle processing
│   └── strategies/
│       ├── simple_translation.py      # Current block-by-block
│       ├── context_aware_translation.py # New context-aware
│       └── batch_translation.py       # Future batch processing
│
├── presentation/                  # UI layer
│   └── gui/                       # Moved from src/gui
│
└── legacy/                        # Keep old structure during transition
    ├── api/
    ├── translator/
    └── utils/
```

## 🚀 Implementation Steps

### Phase 1: Core Foundations (Day 1)
1. Create `core/interfaces/` with proper abstractions
2. Create `core/entities/` for domain objects
3. Define `TranslationStrategy` interface

### Phase 2: Strategy Implementation (Day 2)
4. Implement `SimpleTranslationStrategy` (current logic)
5. Implement `ContextAwareTranslationStrategy` (new feature)
6. Create unified `TranslationService` orchestrator

### Phase 3: Infrastructure Layer (Day 3)
7. Move providers to `infrastructure/providers/`
8. Refactor caching to `infrastructure/cache/`
9. Update dependency injection

### Phase 4: Integration & Testing (Day 4)
10. Update GUI to use new architecture
11. Maintain backward compatibility
12. Add comprehensive tests
