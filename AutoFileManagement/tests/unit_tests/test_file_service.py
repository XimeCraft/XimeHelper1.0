import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from flask import Flask
from AutoFileManagement.AutoFileOpening.services.file import FileService

class TestConfig:
    """Test configuration class"""
    TESTING = True
    AUTO_FILE_OPENING_FILE_TYPES = {
        'DOCUMENTS': ['.txt', '.md'],
        'IMAGES': ['.jpg', '.png'],
        'DATA': ['.csv', '.xlsx', '.xls', '.json'],
    }
    AUTO_FILE_OPENING_MAX_PROCESSABLE_SIZE = 1024 * 1024  # 1MB
    AUTO_FILE_OPENING_APP_MAPPING = {
        'txt': 'TextEdit',
        'md': 'Typora',
        'jpg': 'Preview',
        'png': 'Preview',
        'csv': 'Excel',
        'xlsx': 'Excel',
        'xls': 'Excel',
        'json': 'VSCode'
    }

class TestFileService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create Flask test app
        self.app = Flask(__name__)
        self.app.config.from_object(TestConfig)
        
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Set white directories in a clean way
        self.app.config['AUTO_FILE_OPENING_WHITE_DIRS'] = [self.test_dir]
        
        # Create test files with different types
        self.test_files = {
            'document.txt': 'Hello, World!',
            'document.md': '# Markdown Test',
            'image.jpg': b'fake_image_data',
            'image.png': b'fake_png_data',
            'data.csv': 'name,age\njohn,30',
            'data.json': '{"test": "data"}',
            'large_file.txt': 'x' * (2 * 1024 * 1024)  # 2MB file
        }
        
        for filename, content in self.test_files.items():
            file_path = os.path.join(self.test_dir, filename)
            mode = 'wb' if isinstance(content, bytes) else 'w'
            with open(file_path, mode) as f:
                f.write(content)
        
        # Create test context and FileService instance
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.file_service = FileService()
    
    def tearDown(self):
        """Clean up test fixtures after each test method"""
        # Clean up the application context
        self.ctx.pop()
        
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_verify_file_path(self):
        """Test file path verification"""
        # Test valid file in white directory
        valid_file = os.path.join(self.test_dir, 'document.txt')
        verified_path = self.file_service._verify_file_path(valid_file)
        self.assertEqual(os.path.abspath(valid_file), verified_path)
        
        # Test file outside white directory
        invalid_file = '/tmp/test.txt'
        with self.assertRaises(ValueError):
            self.file_service._verify_file_path(invalid_file)
        
        # Test non-existent file
        non_existent = os.path.join(self.test_dir, 'non_existent.txt')
        with self.assertRaises(FileNotFoundError):
            self.file_service._verify_file_path(non_existent)
    
    def test_get_app_name(self):
        """Test getting application name for file types"""
        # Test document types
        self.assertEqual(self.file_service._get_app_name('test.txt'), 'TextEdit')
        self.assertEqual(self.file_service._get_app_name('test.md'), 'Typora')
        
        # Test image types
        self.assertEqual(self.file_service._get_app_name('test.jpg'), 'Preview')
        self.assertEqual(self.file_service._get_app_name('test.png'), 'Preview')
        
        # Test data types
        self.assertEqual(self.file_service._get_app_name('test.csv'), 'Excel')
        self.assertEqual(self.file_service._get_app_name('test.xlsx'), 'Excel')
        self.assertEqual(self.file_service._get_app_name('test.json'), 'VSCode')
        
        # Test unknown extension
        self.assertEqual(self.file_service._get_app_name('test.unknown'), '')
    
    @patch('subprocess.run')
    def test_get_process_info(self, mock_run):
        """Test getting process info for open files"""
        # Mock subprocess.run to return some process info
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\nTextEdit  123 user   3r   REG    8,1    12345    1 document.txt\n'
        )
        
        test_file = os.path.join(self.test_dir, 'document.txt')
        processes = self.file_service._get_process_info(test_file)
        self.assertEqual(processes, ['TextEdit'])
        
        # Test with no processes
        mock_run.return_value = MagicMock(returncode=1, stdout='')
        processes = self.file_service._get_process_info(test_file)
        self.assertEqual(processes, [])
    
    def test_get_files(self):
        """Test getting list of files from directories"""
        # Test getting all files
        files = self.file_service.get_files()
        self.assertEqual(len(files), 6)  # All files except large_file.txt
        
        # Test getting files by type
        document_files = self.file_service.get_files(file_type='DOCUMENTS')
        self.assertEqual(len(document_files), 2)
        self.assertTrue(any(f['name'] == 'document.txt' for f in document_files))
        self.assertTrue(any(f['name'] == 'document.md' for f in document_files))
        
        image_files = self.file_service.get_files(file_type='IMAGES')
        self.assertEqual(len(image_files), 2)
        self.assertTrue(any(f['name'] == 'image.jpg' for f in image_files))
        self.assertTrue(any(f['name'] == 'image.png' for f in image_files))
        
        data_files = self.file_service.get_files(file_type='DATA')
        self.assertEqual(len(data_files), 2)
        self.assertTrue(any(f['name'] == 'data.csv' for f in data_files))
        self.assertTrue(any(f['name'] == 'data.json' for f in data_files))
        
        # Test getting files from specific directory
        dir_files = self.file_service.get_files(directory=self.test_dir)
        self.assertEqual(len(dir_files), 6)  # All files except large_file.txt
    
    def test_is_white_type(self):
        """Test file type validation"""
        # Test document types
        self.assertTrue(self.file_service._is_white_type('.txt', 'DOCUMENTS'))
        self.assertTrue(self.file_service._is_white_type('.md', 'DOCUMENTS'))
        
        # Test image types
        self.assertTrue(self.file_service._is_white_type('.jpg', 'IMAGES'))
        self.assertTrue(self.file_service._is_white_type('.png', 'IMAGES'))
        
        # Test data types
        self.assertTrue(self.file_service._is_white_type('.csv', 'DATA'))
        self.assertTrue(self.file_service._is_white_type('.xlsx', 'DATA'))
        self.assertTrue(self.file_service._is_white_type('.json', 'DATA'))
        
        # Test invalid combinations
        self.assertFalse(self.file_service._is_white_type('.txt', 'IMAGES'))
        self.assertFalse(self.file_service._is_white_type('.jpg', 'DOCUMENTS'))
        self.assertFalse(self.file_service._is_white_type('.csv', 'IMAGES'))

if __name__ == '__main__':
    unittest.main() 