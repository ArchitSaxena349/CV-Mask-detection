"""
Windows Service wrapper for Mask Detection System
Requires: pip install pywin32
"""
import os
import sys
import time
import servicemanager
import win32event
import win32service
import win32serviceutil
from app import create_app
from waitress import serve

class MaskDetectionService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaskDetectionService"
    _svc_display_name_ = "Mask Detection System"
    _svc_description_ = "AI-powered face mask detection web service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        try:
            # Set up environment
            os.environ['FLASK_CONFIG'] = 'production'
            
            # Create Flask app
            app = create_app('production')
            
            # Start server in a separate thread
            import threading
            server_thread = threading.Thread(
                target=lambda: serve(
                    app,
                    host='0.0.0.0',
                    port=8000,
                    threads=4
                )
            )
            server_thread.daemon = True
            server_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")
        
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MaskDetectionService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MaskDetectionService)