import os
import subprocess
import logging
import time

class AppleScriptService:
    @staticmethod
    def run_script(script):
        """Execute an AppleScript and return its result"""
        try:
            # Initialize System Events if needed
            init_script = '''
            tell application "System Events"
                if not exists process "System Events" then
                    launch
                end if
                return true
            end tell
            '''
            subprocess.run(['osascript', '-e', init_script], capture_output=True)
            
            # Execute the actual script
            result = subprocess.run(['osascript', '-e', script], 
                                 capture_output=True, 
                                 text=True)
            
            # Check for errors
            if result.stderr:
                logging.error(f"AppleScript error: {result.stderr}")
                return None
                
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error executing AppleScript: {e}")
            return None

    @classmethod
    def find_window_process(cls, file_name):
        """Find process that has a window containing the file name"""
        script = f'''
        tell application "System Events"
            set foundProcess to {{}}
            repeat with proc in processes
                try
                    if exists (windows of proc whose name contains "{file_name}") then
                        copy {{name of proc, id of proc}} to the end of foundProcess
                        exit repeat
                    end if
                end try
            end repeat
            return foundProcess
        end tell
        '''
        return cls.run_script(script)

    @classmethod
    def get_open_processes(cls, file_name):
        """Get list of processes that have the file open"""
        script = f'''
        tell application "System Events"
            set openProcesses to {{}}
            set targetProcesses to processes
            repeat with proc in targetProcesses
                try
                    if exists (windows of proc whose name contains "{file_name}") then
                        copy (name of proc) to the end of openProcesses
                        exit repeat
                    end if
                end try
            end repeat
            
            -- Special check for PDF Reader and Excel
            if "{file_name}" ends with ".pdf" and exists process "PDF Reader" then
                copy "PDF Reader" to the end of openProcesses
            end if
            if "{file_name}" ends with ".csv" and exists process "Microsoft Excel" then
                copy "Microsoft Excel" to the end of openProcesses
            end if
            
            return openProcesses
        end tell
        '''
        return cls.run_script(script)

    @classmethod
    def save_and_close_window(cls, process_name, file_name):
        """Save and close a specific window in a process"""
        # Different applications have different ways to close windows
        if process_name == "Preview":
            return cls._close_preview_window(file_name)
        elif process_name == "Microsoft Excel":
            return cls._close_excel_window(file_name)
        elif process_name == "PDF Reader":
            return cls._close_pdf_reader_window(file_name)
        else:
            return cls._close_standard_window(process_name, file_name)

    @classmethod
    def _close_standard_window(cls, process_name, file_name):
        """Standard window closing for most applications"""
        script = f'''
        tell application "{process_name}"
            activate
            delay 0.1
            close every window whose name contains "{file_name}"
            return true
        end tell
        '''
        result = cls.run_script(script)
        if result == "true":
            return True
            
        # If that fails, try using System Events
        script = f'''
        tell application "System Events"
            tell application "{process_name}" to activate
            delay 0.1
            tell process "{process_name}"
                keystroke "w" using command down
                return true
            end tell
        end tell
        '''
        return cls.run_script(script) == "true"

    @classmethod
    def _close_preview_window(cls, file_name):
        """Special handling for Preview.app"""
        script = f'''
        tell application "System Events"
            tell process "Preview"
                set targetWindow to first window whose name contains "{file_name}"
                click button 1 of targetWindow
                return true
            end tell
        end tell
        '''
        result = cls.run_script(script)
        if result == "true":
            return True
            
        # If direct close fails, try force quit
        script = f'''
        tell application "Preview"
            close (every window whose name contains "{file_name}")
            return true
        end tell
        '''
        return cls.run_script(script) == "true"

    @classmethod
    def _close_excel_window(cls, file_name):
        """Special handling for Microsoft Excel - save and quit"""
        script = '''
        tell application "Microsoft Excel"
            activate
            delay 0.2
            tell application "System Events"
                keystroke "s" using {command down}
            end tell
            quit
            return true
        end tell
        '''
        return cls.run_script(script) == "true"

    @classmethod
    def _close_pdf_reader_window(cls, file_name):
        """Special handling for PDF Reader - save and quit"""
        script = '''
        tell application "PDF Reader"
            activate
            delay 0.2
            tell application "System Events"
                keystroke "s" using {command down}
            end tell
            quit
            return true
        end tell
        '''
        result = cls.run_script(script)
        if result == "true":
            return True
            
        # If that fails, try force quit
        script = '''
        tell application "System Events"
            if exists process "PDF Reader" then
                do shell script "killall 'PDF Reader'"
            end if
            return true
        end tell
        '''
        return cls.run_script(script) == "true"

    @classmethod
    def check_app_permissions(cls):
        """Check and request permissions for all required applications"""
        apps_to_check = ["Microsoft Excel", "Preview", "TextEdit", "PDF Reader", "System Events"]
        for app in apps_to_check:
            script = f'''
            tell application "System Events"
                try
                    tell application "{app}" to activate
                    delay 0.2
                    tell process "{app}"
                        set frontmost to true
                    end tell
                    return true
                on error
                    return false
                end try
            end tell
            '''
            cls.run_script(script)
            time.sleep(0.3)  # 给用户时间响应权限请求
        
        # 确保所有应用程序都退出
        cls.quit_applications()

    @classmethod
    def quit_applications(cls):
        """Safely quit all applications we might have opened"""
        script = '''
        tell application "System Events"
            set appsToQuit to {"TextEdit", "Preview", "Microsoft Excel", "PDF Reader"}
            repeat with appName in appsToQuit
                if exists (processes where name is appName) then
                    tell application appName
                        try
                            quit saving yes
                        end try
                    end tell
                end if
            end repeat
        end tell
        '''
        return cls.run_script(script)

    @classmethod
    def get_default_app(cls, file_path):
        """Get the default application for a file type"""
        script = f'''
        tell application "Finder"
            try
                return name of (get application file id (get creator type of (information for "{file_path}")))
            on error
                return missing value
            end try
        end tell
        '''
        return cls.run_script(script) 