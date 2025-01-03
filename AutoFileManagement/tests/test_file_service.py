import unittest
from pathlib import Path
import os
import time
import warnings
import logging
from unittest.mock import patch, MagicMock
from ..AutoFileOpening.services.file import FileService
from ..AutoFileOpening.services.apple_script import AppleScriptService

# Suppress ResourceWarnings about unclosed files
warnings.filterwarnings("ignore", category=ResourceWarning)

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    force=True
)

class TestFileService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = Path("/Users/xiao/Projects/git/XimeHelperV1/AutoFileManagement/data/test_files")
        
        # Map actual files in test directory
        cls.test_files = {
            "txt1": cls.test_dir / "test1.txt",
            "txt2": cls.test_dir / "test2.txt",
            "md": cls.test_dir / "test3.md",
            "pdf": cls.test_dir / "ChatGPT 1 basic (v5).pdf",
            "csv": cls.test_dir / "ProjectsData.csv",
            "png": cls.test_dir / "AutoFileOpeningFrame.png"
        }
        
        # Verify all test files exist
        for name, path in cls.test_files.items():
            if not path.exists():
                raise FileNotFoundError(f"Required test file not found: {path}")
        
        # Clean up at the start
        AppleScriptService.quit_applications()
        time.sleep(1)

    def setUp(self):
        """Set up test cases"""
        # Create mock app with only necessary configuration
        self.app_mock = MagicMock()
        self.app_mock.config = {
            'AUTO_FILE_OPENING_WHITE_DIRS': [str(self.test_dir)],
            'AUTO_FILE_OPENING_FILE_TYPES': {
                'text': ['.txt', '.md'],
                'data': ['.csv'],
                'document': ['.pdf'],
                'image': ['.png']
            },
            'AUTO_FILE_OPENING_MAX_PROCESSABLE_SIZE': float('inf'),
            'AUTO_FILE_OPENING_APP_MAPPING': {
                'txt': 'TextEdit',
                'md': 'TextEdit',
                'pdf': 'PDF Reader',
                'csv': 'Microsoft Excel',
                'png': 'Preview'
            }
        }
        
        # Patch current_app to use our mock in FileService
        self.patcher = patch('AutoFileManagement.AutoFileOpening.services.file.current_app', self.app_mock)
        self.patcher.start()
        
        # Create file service instance
        self.file_service = FileService()
        
        # Clean up any leftover open files before each test
        AppleScriptService.quit_applications()
        time.sleep(1)

    def tearDown(self):
        """Clean up after each test"""
        self.patcher.stop()
        # Clean up any open files
        AppleScriptService.quit_applications()
        time.sleep(1)

    def _wait_for_file_open(self, path, timeout=5, interval=0.2):
        """Wait for file to be detected as open with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.file_service.is_file_open(path):
                return True
            time.sleep(interval)
        return False

    def _wait_for_file_close(self, path, timeout=5, interval=0.2):
        """Wait for file to be detected as closed with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.file_service.is_file_open(path):
                return True
            time.sleep(interval)
        return False

    def test_file_open_detection_by_type(self):
        """Test file open detection for each file type"""
        for name, path in self.test_files.items():
            with self.subTest(file_type=name):
                logging.info(f"\n{'='*20} Testing {name} file {'='*20}")
                logging.info(f"File path: {path}")
                
                # Open file and wait for application to be ready
                os.system(f'open "{path}"')
                time.sleep(1)  # Give more time for PDF Reader and Excel
                
                # Test detection
                is_open = self.file_service.is_file_open(path)
                logging.info(f"Is file open? {is_open}")
                self.assertTrue(
                    is_open,
                    f"Failed to detect that {name} ({path}) is open"
                )
                
                # Close file
                success = self.file_service.close_specific_file(path)
                logging.info(f"Close operation success? {success}")
                self.assertTrue(
                    success,
                    f"Failed to close {name} ({path})"
                )
                
                time.sleep(1)  # Give more time for applications to quit
                
                # Verify file is closed
                is_still_open = self.file_service.is_file_open(path)
                logging.info(f"Is file still open? {is_still_open}")
                self.assertFalse(
                    is_still_open,
                    f"{name} ({path}) should be closed"
                )
                logging.info(f"{'='*50}\n")

    def test_multiple_files_handling(self):
        """Test handling multiple open files of the same type"""
        txt_files = [self.test_files['txt1'], self.test_files['txt2']]
        
        logging.info("\n=== Testing Multiple Files Handling ===")
        logging.info("Opening multiple text files...")
        
        # Open both text files
        for path in txt_files:
            os.system(f'open "{path}"')
            time.sleep(0.3)
        
        # Verify both are open
        for path in txt_files:
            is_open = self.file_service.is_file_open(path)
            logging.info(f"Is {path.name} open? {is_open}")
            self.assertTrue(
                is_open,
                f"Failed to detect that {path} is open"
            )
        
        logging.info("\nClosing first text file...")
        # Close first file only
        success = self.file_service.close_specific_file(txt_files[0])
        logging.info(f"Close operation success? {success}")
        self.assertTrue(
            success,
            "Failed to close first text file"
        )
        
        time.sleep(0.3)  # Short delay for file to close
        
        # Verify first file is closed but second remains open
        is_first_open = self.file_service.is_file_open(txt_files[0])
        is_second_open = self.file_service.is_file_open(txt_files[1])
        logging.info(f"Is first file still open? {is_first_open}")
        logging.info(f"Is second file still open? {is_second_open}")
        
        self.assertFalse(
            is_first_open,
            "First text file should be closed"
        )
        self.assertTrue(
            is_second_open,
            "Second text file should remain open"
        )
        
        # Clean up
        logging.info("\nCleaning up...")
        self.file_service.close_specific_file(txt_files[1])
        logging.info("=== Multiple Files Test Complete ===\n")

    def test_modified_files_by_type(self):
        """Test closing modified files of different types"""
        # Test with text files only (since we can't save PDF/Excel)
        test_files = ['txt2']
        for file_key in test_files:
            with self.subTest(file_type=file_key):
                file_path = self.test_files[file_key]
                logging.info(f"\n=== Testing Modified File: {file_path.name} ===")
                
                # Open file
                os.system(f'open "{file_path}"')
                time.sleep(0.3)
                
                # Prompt for modification
                input(f"Please modify {file_path.name} and save. Press Enter when done...")
                
                # Try to close
                success = self.file_service.close_specific_file(file_path)
                logging.info(f"Close operation success? {success}")
                self.assertTrue(
                    success,
                    f"Failed to close modified {file_key} file"
                )
                
                time.sleep(0.3)  # Short delay for file to close
                
                # Verify file is closed
                is_still_open = self.file_service.is_file_open(file_path)
                logging.info(f"Is file still open? {is_still_open}")
                self.assertFalse(
                    is_still_open,
                    f"Modified {file_key} file should be closed"
                )
                logging.info(f"=== Modified File Test Complete ===\n")

    def test_pdf_and_excel_handling(self):
        """Test specifically PDF and Excel file handling"""
        test_files = {
            "pdf": self.test_files["pdf"],
            "csv": self.test_files["csv"]
        }
        
        for name, path in test_files.items():
            with self.subTest(file_type=name):
                logging.info(f"\n{'='*20} Testing {name} file {'='*20}")
                logging.info(f"File path: {path}")
                
                # Open file and wait for application to be ready
                os.system(f'open "{path}"')
                time.sleep(1)
                
                # Test detection
                is_open = self.file_service.is_file_open(path)
                logging.info(f"Is file open? {is_open}")
                self.assertTrue(
                    is_open,
                    f"Failed to detect that {name} ({path}) is open"
                )
                
                # Close file
                success = self.file_service.close_specific_file(path)
                logging.info(f"Close operation success? {success}")
                self.assertTrue(
                    success,
                    f"Failed to close {name} ({path})"
                )
                
                time.sleep(1)
                
                # Verify file is closed
                is_still_open = self.file_service.is_file_open(path)
                logging.info(f"Is file still open? {is_still_open}")
                self.assertFalse(
                    is_still_open,
                    f"{name} ({path}) should be closed"
                )
                logging.info(f"{'='*50}\n")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        logging.info("\nFinal cleanup of any remaining open files...")
        AppleScriptService.quit_applications()
        time.sleep(1)

if __name__ == '__main__':
    unittest.main() 