# tools/screen_capture_tool.py
from typing import Dict, Any, Optional
import os
import platform
from datetime import datetime
import importlib.util

# Check available libraries
MSS_AVAILABLE = importlib.util.find_spec("mss") is not None
PILLOW_AVAILABLE = importlib.util.find_spec("PIL") is not None
PYAUTOGUI_AVAILABLE = importlib.util.find_spec("pyautogui") is not None
PYPERCLIP_AVAILABLE = importlib.util.find_spec("pyperclip") is not None

# Import available libraries
if MSS_AVAILABLE:
    import mss
    
if PILLOW_AVAILABLE:
    from PIL import Image
    
if PYAUTOGUI_AVAILABLE:
    import pyautogui
    pyautogui.FAILSAFE = True

if PYPERCLIP_AVAILABLE:
    import pyperclip

# Platform-specific clipboard handling
def _copy_image_to_clipboard(image: Image.Image) -> bool:
    """Copy PIL Image to system clipboard."""
    try:
        system = platform.system().lower()
        
        if system == "windows":
            return _copy_to_windows_clipboard(image)
        elif system == "darwin":  # macOS
            return _copy_to_mac_clipboard(image)
        elif system == "linux":
            return _copy_to_linux_clipboard(image)
        else:
            return False
            
    except Exception as e:
        print(f"ERROR: Clipboard copy failed: {str(e)}")
        return False

def _copy_to_windows_clipboard(image: Image.Image) -> bool:
    """Copy image to Windows clipboard."""
    try:
        import io
        import win32clipboard
        from PIL import ImageWin
        
        # Convert to Windows DIB format
        output = io.BytesIO()
        image.save(output, "BMP")
        data = output.getvalue()[14:]  # Remove BMP header
        
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
        
    except ImportError:
        # Fallback: try with pywin32 alternative or other methods
        try:
            import io
            output = io.BytesIO()
            image.save(output, format='PNG')
            
            # Try using subprocess with PowerShell (Windows 10+)
            import subprocess
            import base64
            
            img_data = base64.b64encode(output.getvalue()).decode()
            ps_script = f'''
            Add-Type -AssemblyName System.Drawing
            Add-Type -AssemblyName System.Windows.Forms
            $bytes = [Convert]::FromBase64String("{img_data}")
            $ms = New-Object IO.MemoryStream($bytes, 0, $bytes.Length)
            $image = [System.Drawing.Image]::FromStream($ms)
            [System.Windows.Forms.Clipboard]::SetImage($image)
            $image.Dispose()
            $ms.Dispose()
            '''
            
            subprocess.run(["powershell", "-Command", ps_script], 
                         capture_output=True, check=True)
            return True
            
        except Exception:
            return False
    except Exception:
        return False

def _copy_to_mac_clipboard(image: Image.Image) -> bool:
    """Copy image to macOS clipboard."""
    try:
        import subprocess
        import io
        
        # Save to temporary bytes
        output = io.BytesIO()
        image.save(output, format='PNG')
        
        # Use pbcopy with PNG data
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(output.getvalue())
        return process.returncode == 0
        
    except Exception:
        return False

def _copy_to_linux_clipboard(image: Image.Image) -> bool:
    """Copy image to Linux clipboard."""
    try:
        import subprocess
        import io
        
        # Save to temporary bytes
        output = io.BytesIO()
        image.save(output, format='PNG')
        
        # Try xclip first
        try:
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard', '-t', 'image/png'],
                stdin=subprocess.PIPE
            )
            process.communicate(output.getvalue())
            if process.returncode == 0:
                return True
        except FileNotFoundError:
            pass
        
        # Try wl-copy (Wayland)
        try:
            process = subprocess.Popen(
                ['wl-copy', '--type', 'image/png'],
                stdin=subprocess.PIPE
            )
            process.communicate(output.getvalue())
            return process.returncode == 0
        except FileNotFoundError:
            pass
            
        return False
        
    except Exception:
        return False

async def capture_to_clipboard(
    monitor: Optional[int] = None,
    region: Optional[Dict[str, int]] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Capture screenshot and copy directly to clipboard for pasting into Claude Desktop.
    
    Args:
        monitor: Monitor number (None for primary monitor)
        region: Specific region {"x": 0, "y": 0, "width": 1920, "height": 1080}
        context: User context about what they need help with
    
    Returns:
        Dictionary with clipboard copy status and instructions
    """
    print(f"INFO: capture_to_clipboard called with context: {context}")
    
    # Check if screenshot libraries are available
    if not (MSS_AVAILABLE or PYAUTOGUI_AVAILABLE):
        return {
            "error": "Screenshot libraries not available. Install with: pip install mss pillow",
            "installation_help": "pip install mss pillow pyautogui",
            "status": "error"
        }
    
    if not PILLOW_AVAILABLE:
        return {
            "error": "PIL (Pillow) required for image processing. Install with: pip install pillow",
            "status": "error"
        }
    
    try:
        screenshot_image = None
        method_used = None
        
        # Try MSS first (fastest and most reliable)
        if MSS_AVAILABLE:
            with mss.mss() as sct:
                if region:
                    # Capture specific region
                    monitor_config = {
                        "top": region.get("y", 0),
                        "left": region.get("x", 0),
                        "width": region.get("width", 1920),
                        "height": region.get("height", 1080)
                    }
                    screenshot = sct.grab(monitor_config)
                else:
                    # Capture specific monitor or primary
                    if monitor is not None and 0 < monitor < len(sct.monitors):
                        screenshot = sct.grab(sct.monitors[monitor])
                    else:
                        screenshot = sct.grab(sct.monitors[1])  # Primary monitor
                
                # Convert to PIL Image
                screenshot_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                method_used = "mss"
                
        # Fallback to PyAutoGUI
        elif PYAUTOGUI_AVAILABLE:
            if region:
                screenshot_image = pyautogui.screenshot(region=(
                    region.get("x", 0), 
                    region.get("y", 0),
                    region.get("width", 1920), 
                    region.get("height", 1080)
                ))
            else:
                screenshot_image = pyautogui.screenshot()
            method_used = "pyautogui"
        
        if not screenshot_image:
            return {
                "error": "Failed to capture screenshot with available methods",
                "status": "error"
            }
        
        # Copy to clipboard
        clipboard_success = _copy_image_to_clipboard(screenshot_image)
        
        if clipboard_success:
            return {
                "screenshot_captured": True,
                "clipboard_copied": True,
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "image_info": {
                    "size": screenshot_image.size,
                    "width": screenshot_image.size[0],
                    "height": screenshot_image.size[1],
                    "mode": screenshot_image.mode
                },
                "capture_info": {
                    "method_used": method_used,
                    "monitor": monitor,
                    "region": region,
                    "platform": platform.system()
                },
                "instructions": "Screenshot copied to clipboard! Paste (Ctrl+V or Cmd+V) into this Claude Desktop conversation to show me your screen.",
                "message": f"📸 Screenshot captured and copied to clipboard! {f'Context: {context}. ' if context else ''}Now paste it here so I can see your screen and help you.",
                "status": "success"
            }
        else:
            return {
                "screenshot_captured": True,
                "clipboard_copied": False,
                "error": "Screenshot captured but failed to copy to clipboard",
                "platform_info": {
                    "system": platform.system(),
                    "requires": "Additional system dependencies may be needed for clipboard support"
                },
                "fallback_suggestion": "Try using the manual screenshot method or install clipboard dependencies",
                "status": "partial"
            }
        
    except Exception as e:
        print(f"ERROR: capture_to_clipboard failed: {str(e)}")
        return {
            "error": f"Screenshot capture failed: {str(e)}",
            "context": context,
            "troubleshooting": {
                "check_permissions": "Ensure the application has screen capture permissions",
                "check_display": "Verify display/monitor configuration",
                "install_dependencies": "Try: pip install mss pillow pyautogui"
            },
            "status": "error"
        }

def _extract_capture_context(message: str) -> Optional[str]:
    """Extract context from [CAPTURE] messages."""
    import re
    # Look for [CAPTURE] followed by optional context
    pattern = r'\[CAPTURE\]\s*(.*)'
    match = re.search(pattern, message, re.IGNORECASE)
    if match:
        context = match.group(1).strip()
        return context if context else None
    return None

async def detect_and_capture(user_message: str) -> Dict[str, Any]:
    """
    Detect [CAPTURE] keyword in user messages and automatically capture screen.
    
    Args:
        user_message: The user's message to check for [CAPTURE] keyword
        
    Returns:
        Screenshot capture result if [CAPTURE] detected, otherwise notification
    """
    print(f"INFO: detect_and_capture called with message: {user_message[:100]}...")
    
    # Check if message contains [CAPTURE] keyword
    if "[CAPTURE]" in user_message.upper():
        context = _extract_capture_context(user_message)
        print(f"INFO: [CAPTURE] keyword detected, context: {context}")
        
        result = await capture_to_clipboard(context=context)
        
        if result.get("status") == "success":
            result["triggered_by"] = "[CAPTURE] keyword"
            result["original_message"] = user_message
        
        return result
    else:
        return {
            "capture_triggered": False,
            "message": "No [CAPTURE] keyword detected in message",
            "usage_tip": "Include [CAPTURE] in your message to automatically take a screenshot",
            "status": "no_action"
        }

async def quick_capture(context: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick screenshot capture to clipboard - main function for direct calls.
    
    Args:
        context: Optional context about what the user needs help with
        
    Returns:
        Screenshot capture result with clipboard copy status
    """
    print(f"INFO: quick_capture called - context: {context}")
    return await capture_to_clipboard(context=context)

async def capture_region_to_clipboard(
    x: int,
    y: int, 
    width: int,
    height: int,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Capture a specific region of the screen to clipboard.
    
    Args:
        x: Left coordinate of the region
        y: Top coordinate of the region  
        width: Width of the region
        height: Height of the region
        context: Optional context about what's in this region
        
    Returns:
        Screenshot capture result for the specified region
    """
    print(f"INFO: capture_region_to_clipboard called - region: {x},{y} {width}x{height}")
    
    region = {"x": x, "y": y, "width": width, "height": height}
    result = await capture_to_clipboard(region=region, context=context)
    
    if result.get("status") == "success":
        result["region_captured"] = region
        result["message"] = f"📸 Region ({x},{y}) sized {width}x{height} copied to clipboard! {f'Context: {context}. ' if context else ''}Paste it here to show me this area."
        
    return result

async def capture_monitor_to_clipboard(
    monitor_number: int,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Capture a specific monitor to clipboard.
    
    Args:
        monitor_number: Monitor number to capture (1, 2, 3, etc.)
        context: Optional context about what's on this monitor
        
    Returns:
        Screenshot capture result from the specified monitor
    """
    print(f"INFO: capture_monitor_to_clipboard called - monitor: {monitor_number}")
    
    result = await capture_to_clipboard(monitor=monitor_number, context=context)
    
    if result.get("status") == "success":
        result["monitor_captured"] = monitor_number
        result["message"] = f"📸 Monitor {monitor_number} copied to clipboard! {f'Context: {context}. ' if context else ''}Paste it here to show me this screen."
        
    return result

def register(mcp_instance):
    """Register the screen capture tools with the MCP server"""
    
    # Check library availability
    available_libs = []
    missing_libs = []
    
    if MSS_AVAILABLE:
        available_libs.append("mss (fast screenshots)")
    else:
        missing_libs.append("mss")
        
    if PILLOW_AVAILABLE:
        available_libs.append("pillow (image processing)")
    else:
        missing_libs.append("pillow")
        
    if PYAUTOGUI_AVAILABLE:
        available_libs.append("pyautugui (fallback screenshots)")
    else:
        missing_libs.append("pyautogui")
    
    # Check clipboard capabilities
    system = platform.system().lower()
    clipboard_info = []
    
    if system == "windows":
        clipboard_info.append("Windows clipboard support via PowerShell")
        try:
            import win32clipboard
            clipboard_info.append("Enhanced Windows clipboard (pywin32 available)")
        except ImportError:
            clipboard_info.append("Basic Windows clipboard (consider: pip install pywin32)")
    elif system == "darwin":
        clipboard_info.append("macOS clipboard support via pbcopy")
    elif system == "linux":
        clipboard_info.append("Linux clipboard support (requires xclip or wl-copy)")
    
    # Register tools
    mcp_instance.tool()(capture_to_clipboard)
    mcp_instance.tool()(quick_capture)
    mcp_instance.tool()(capture_region_to_clipboard)
    mcp_instance.tool()(capture_monitor_to_clipboard)
    mcp_instance.tool()(detect_and_capture)  # NEW: For [CAPTURE] keyword detection
    
    print(f"INFO: Screen capture tools registered successfully")
    print(f"INFO: Platform: {platform.system()}")
    print(f"INFO: Available libraries: {', '.join(available_libs) if available_libs else 'None'}")
    print(f"INFO: Clipboard support: {', '.join(clipboard_info)}")
    
    if missing_libs:
        print(f"INFO: Install for full functionality: pip install {' '.join(missing_libs)}")
    
    print("INFO: Use [CAPTURE] keyword in messages or call quick_capture() directly")
    print("INFO: [CAPTURE] examples:")
    print("  - '[CAPTURE] I need help with this dialog'")
    print("  - '[CAPTURE] What should I click next?'")
    print("  - '[CAPTURE] I'm getting an error'")
    print("  - Just '[CAPTURE]' for general screen capture")