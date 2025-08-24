#!/usr/bin/env python3
"""
Test script for modern UI components
Tests the new UI enhancements without requiring GUI display
"""

import sys
import os
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class TestModernUIComponents(unittest.TestCase):
    """Test modern UI components functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path("/tmp/test_voicesub")
        self.temp_dir.mkdir(exist_ok=True)
        
    def test_modern_error_handler_import(self):
        """Test that modern error handler can be imported"""
        try:
            from src.gui.components.modern_error_handler import ModernErrorHandler
            self.assertTrue(hasattr(ModernErrorHandler, 'show_error_dialog'))
            self.assertTrue(hasattr(ModernErrorHandler, 'handle_exception'))
        except ImportError as e:
            self.fail(f"Could not import ModernErrorHandler: {e}")
            
    def test_modern_translation_dialog_import(self):
        """Test that modern translation dialog can be imported"""
        try:
            from src.gui.components.modern_translation_dialog import ModernTranslationDialog
            self.assertTrue(hasattr(ModernTranslationDialog, 'LANGUAGES'))
            self.assertTrue(hasattr(ModernTranslationDialog, 'SERVICES'))
            
            # Test language mapping
            dialog_class = ModernTranslationDialog
            self.assertIn("🇻🇳 Tiếng Việt", dialog_class.LANGUAGES)
            self.assertEqual(dialog_class.LANGUAGES["🇻🇳 Tiếng Việt"], "vi")
            
        except ImportError as e:
            self.fail(f"Could not import ModernTranslationDialog: {e}")
            
    def test_subtitle_preview_import(self):
        """Test that subtitle preview can be imported"""
        try:
            from src.gui.components.subtitle_preview import SubtitlePreviewPanel
            self.assertTrue(hasattr(SubtitlePreviewPanel, 'parse_srt'))
            self.assertTrue(hasattr(SubtitlePreviewPanel, 'parse_vtt'))
            
        except ImportError as e:
            self.fail(f"Could not import SubtitlePreviewPanel: {e}")
            
    def test_subtitle_parsing(self):
        """Test subtitle file parsing functionality"""
        from src.gui.components.subtitle_preview import SubtitlePreviewPanel
        
        # Create test SRT content
        srt_content = """1
00:00:01,000 --> 00:00:03,000
Test subtitle line 1

2
00:00:04,000 --> 00:00:06,000
Test subtitle line 2
with multiple lines"""
        
        # Write test file
        test_file = self.temp_dir / "test.srt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(srt_content)
            
        # Test parsing (create a mock panel for testing)
        class MockPanel:
            def parse_srt(self, file_path):
                return SubtitlePreviewPanel.parse_srt(None, file_path)
                
        panel = MockPanel()
        
        try:
            subtitles = panel.parse_srt(str(test_file))
            
            self.assertEqual(len(subtitles), 2)
            self.assertEqual(subtitles[0]['index'], 1)
            self.assertEqual(subtitles[0]['start_time'], '00:00:01,000')
            self.assertEqual(subtitles[0]['end_time'], '00:00:03,000')
            self.assertEqual(subtitles[0]['text'], 'Test subtitle line 1')
            
            self.assertEqual(subtitles[1]['index'], 2)
            self.assertEqual(subtitles[1]['text'], 'Test subtitle line 2\nwith multiple lines')
            
        except Exception as e:
            self.fail(f"Subtitle parsing failed: {e}")
            
    def test_modern_settings_import(self):
        """Test that modern settings can be imported"""
        try:
            from src.gui.components.modern_settings_dialog import ModernSettingsDialog
            self.assertTrue(hasattr(ModernSettingsDialog, 'load_settings'))
            self.assertTrue(hasattr(ModernSettingsDialog, 'save_settings'))
            
        except ImportError as e:
            self.fail(f"Could not import ModernSettingsDialog: {e}")
            
    def test_modern_tooltip_import(self):
        """Test that modern tooltip can be imported"""
        try:
            from src.gui.components.modern_tooltip import ModernTooltip, add_tooltip
            self.assertTrue(callable(add_tooltip))
            
        except ImportError as e:
            self.fail(f"Could not import ModernTooltip: {e}")
            
    def test_file_selection_import(self):
        """Test that modern file selection can be imported"""
        try:
            from src.gui.components.modern_file_selection import ModernDragDropFrame, ModernFileSelectionPanel
            self.assertTrue(hasattr(ModernFileSelectionPanel, 'get_folders'))
            
        except ImportError as e:
            self.fail(f"Could not import file selection components: {e}")
            
    def test_modern_app_import(self):
        """Test that modern app can be imported"""
        try:
            from src.gui.modern_app import ModernSubtitleApp, main
            self.assertTrue(callable(main))
            
        except ImportError as e:
            self.fail(f"Could not import modern app: {e}")
            
    def test_cache_manager_fix(self):
        """Test that cache manager syntax is fixed"""
        try:
            from src.utils.cache_manager import CacheManager, cache_result
            self.assertTrue(callable(cache_result))
            
        except (ImportError, SyntaxError) as e:
            self.fail(f"Cache manager has issues: {e}")
            
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


class TestUIEnhancements(unittest.TestCase):
    """Test UI enhancement features"""
    
    def test_error_message_mapping(self):
        """Test error message mapping"""
        from src.gui.components.modern_error_handler import ModernErrorHandler
        
        # Test that error messages are properly defined
        self.assertIn("FileNotFoundError", ModernErrorHandler.ERROR_MESSAGES)
        self.assertIn("ConnectionError", ModernErrorHandler.ERROR_MESSAGES)
        
        # Test error message structure
        file_error = ModernErrorHandler.ERROR_MESSAGES["FileNotFoundError"]
        self.assertIn("title", file_error)
        self.assertIn("message", file_error) 
        self.assertIn("suggestions", file_error)
        self.assertIsInstance(file_error["suggestions"], list)
        
    def test_language_service_mapping(self):
        """Test language and service mappings"""
        from src.gui.components.modern_translation_dialog import ModernTranslationDialog
        
        # Test language mappings
        languages = ModernTranslationDialog.LANGUAGES
        self.assertIn("🇺🇸 English", languages)
        self.assertEqual(languages["🇺🇸 English"], "en")
        
        # Test service mappings
        services = ModernTranslationDialog.SERVICES
        self.assertIn("🚀 Novita AI", services)
        self.assertEqual(services["🚀 Novita AI"], "novita")
        
    def test_keyboard_shortcuts_defined(self):
        """Test that keyboard shortcuts are properly defined"""
        # This would test the keyboard shortcut bindings
        # Since we can't test actual GUI events, we check the method exists
        from src.gui.modern_app import ModernSubtitleApp
        
        self.assertTrue(hasattr(ModernSubtitleApp, 'setup_keyboard_shortcuts'))
        self.assertTrue(hasattr(ModernSubtitleApp, 'show_help'))


def run_tests():
    """Run all tests"""
    print("🧪 Testing Modern UI Components...")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestModernUIComponents))
    suite.addTest(unittest.makeSuite(TestUIEnhancements))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    
    print(f"\n📊 Test Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {total_tests - failures - errors}")
    print(f"   Failed: {failures}")
    print(f"   Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("✅ All tests passed! Modern UI components are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)