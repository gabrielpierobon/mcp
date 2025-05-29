# Screen Capture Tool Documentation

Revolutionary visual context tool that enables AI agents to see and understand your desktop environment in real-time.

## Overview

The Screen Capture Tool provides AI agents with visual awareness of your desktop by capturing screenshots and copying them directly to the clipboard for instant sharing with Claude Desktop. This enables contextual guidance, error troubleshooting, and workflow assistance based on what's actually displayed on your screen.

## Installation Requirements

```bash
# Essential libraries
pip install mss pillow

# Optional: Enhanced Windows clipboard support
pip install pywin32

# Linux users (choose one)
sudo apt-get install xclip        # X11 systems
sudo apt-get install wl-clipboard  # Wayland systems
```

## Environment Variables

None required. Works with system clipboard and screen capture permissions.

## Available Functions

### Core Functions

#### `quick_capture`
Primary function for taking screenshots with clipboard integration.

**What it does:**
- Captures the entire primary screen
- Copies screenshot directly to system clipboard
- Returns capture status and user instructions
- Optimized for speed and reliability

**Parameters:**
- `context` (optional) - Description of what you need help with

**Returns:**
- Screenshot capture confirmation
- Clipboard copy status
- Instructions for pasting into Claude Desktop
- Image metadata and capture details

#### `detect_and_capture`
Automatic screenshot trigger when `[CAPTURE]` keyword is detected in messages.

**What it does:**
- Monitors messages for `[CAPTURE]` keyword
- Automatically extracts context from the message
- Triggers screenshot capture to clipboard
- Provides seamless natural language integration

**Parameters:**
- `user_message` (required) - Message text to scan for [CAPTURE] keyword

**Returns:**
- Screenshot capture result if keyword detected
- Context extraction from user message
- Usage guidance if no keyword found

### Advanced Functions

#### `capture_region_to_clipboard`
Captures specific rectangular areas of the screen.

**What it does:**
- Takes screenshot of defined screen region
- Copies cropped image to clipboard
- Useful for focusing on specific UI elements
- Reduces image size for faster processing

**Parameters:**
- `x` (required) - Left coordinate of region
- `y` (required) - Top coordinate of region
- `width` (required) - Width of region in pixels
- `height` (required) - Height of region in pixels
- `context` (optional) - Description of the region contents

#### `capture_monitor_to_clipboard`
Captures specific monitors in multi-monitor setups.

**What it does:**
- Takes screenshot of specified monitor
- Supports multi-monitor configurations
- Copies full monitor display to clipboard
- Identifies monitor by number (1, 2, 3, etc.)

**Parameters:**
- `monitor_number` (required) - Monitor to capture (1 = primary, 2 = secondary, etc.)
- `context` (optional) - Description of what's on the monitor

#### `capture_to_clipboard`
Advanced function with full customization options.

**What it does:**
- Provides complete control over capture settings
- Supports monitor selection and region specification
- Handles all clipboard operations
- Base function for other capture methods

**Parameters:**
- `monitor` (optional) - Specific monitor number
- `region` (optional) - Dictionary with x, y, width, height
- `context` (optional) - User context for the screenshot

## [CAPTURE] Keyword System

### Natural Language Integration

The tool responds to `[CAPTURE]` keywords in natural conversation:

**Basic Usage:**
```
[CAPTURE]
```

**With Context:**
```
[CAPTURE] I need help with this dialog box
[CAPTURE] What should I click next?
[CAPTURE] I'm getting an error message
[CAPTURE] I'm stuck on this configuration screen
```

### Context Extraction

The tool automatically extracts context from your message:
- `[CAPTURE] I can't find the save button` → Context: "I can't find the save button"
- `[CAPTURE] This error makes no sense` → Context: "This error makes no sense"
- `[CAPTURE]` → Context: None (general screenshot)

## Cross-Platform Support

### Windows
- **Primary Method**: PowerShell-based clipboard integration
- **Enhanced Method**: Win32 clipboard API (requires pywin32)
- **Fallback**: Basic image clipboard operations

### macOS
- **Method**: pbcopy command-line integration
- **Format**: PNG data to system clipboard
- **Compatibility**: Works with all macOS versions

### Linux
- **X11 Systems**: xclip integration for clipboard
- **Wayland Systems**: wl-copy integration
- **Fallback**: Attempts multiple clipboard methods

## Use Cases

### Desktop Workflow Assistance
- **Software Navigation**: Get guidance through complex applications
- **Configuration Help**: Visual assistance with settings dialogs
- **UI Element Identification**: Find buttons, menus, and controls
- **Workflow Optimization**: Learn efficient navigation paths

### Error Troubleshooting
- **Error Dialog Analysis**: Understand error messages and solutions
- **System Issue Diagnosis**: Visual debugging of system problems
- **Application Crashes**: Analyze crash screens and error states
- **Configuration Problems**: Fix settings and configuration issues

### Learning and Training
- **Software Tutorials**: Step-by-step visual guidance
- **Feature Discovery**: Learn about available options and tools
- **Best Practices**: Get recommendations for efficient workflows
- **Keyboard Shortcuts**: Learn relevant shortcuts for current context

### Development and Design
- **Code Review**: Visual context for coding problems
- **UI/UX Feedback**: Design analysis and suggestions
- **Testing Support**: Visual bug reporting and analysis
- **Layout Problems**: CSS, design, and layout troubleshooting

## Workflow Examples

### Basic Screenshot Sharing
```
[CAPTURE] What do you see on my screen?
```
1. Screenshot captured automatically
2. Image copied to clipboard
3. Paste (Ctrl+V) image into Claude Desktop
4. Receive visual analysis and recommendations

### Error Troubleshooting
```
[CAPTURE] I'm getting this weird error and don't know what it means
```
1. Error dialog captured
2. AI analyzes error message visually
3. Provides specific troubleshooting steps
4. Offers alternative solutions

### Software Learning
```
[CAPTURE] How do I access advanced settings in this application?
```
1. Current application interface captured
2. AI identifies application and current state
3. Provides step-by-step navigation guidance
4. Highlights relevant UI elements

### Multi-Monitor Assistance
```
Can you help me with what's on my second monitor?
```
Then call: `capture_monitor_to_clipboard(2, "second monitor help")`

### Region-Specific Help
```
I need help with just the top-right corner
```
Then call: `capture_region_to_clipboard(1000, 0, 920, 500, "top-right corner")`

## Integration Patterns

### With Web Search
```python
# Take screenshot, then search for solutions
capture_result = await quick_capture("software error")
# User pastes screenshot
search_result = await brave_web_search("how to fix [specific error seen in image]")
```

### With File Operations
```python
# Capture configuration screen, then save settings
await quick_capture("current settings")
# User pastes image showing current config
await write_file("configs/current_setup.txt", "Configuration notes based on screenshot")
```

### With Browser Automation
```python
# See desktop, then automate web actions
await quick_capture("website form I need to fill")
# Analyze form, then automate filling
await navigate_to_page("form_url")
await fill_form_field("#username", "extracted_value")
```

## Technical Features

### Screenshot Methods
- **MSS (Primary)**: Fastest cross-platform screenshot library
- **PyAutoGUI (Fallback)**: Reliable backup screenshot method
- **PIL Integration**: Image processing and format conversion

### Clipboard Integration
- **Direct Copy**: No temporary files or storage
- **Format Optimization**: PNG format for quality and compatibility
- **Cross-Platform**: Native clipboard APIs for each OS
- **Memory Efficient**: Images processed in memory only

### Performance Characteristics
- **Speed**: < 1 second for full screen capture
- **Memory**: Minimal memory footprint
- **Quality**: Lossless PNG compression
- **Reliability**: Multiple fallback methods

## Security and Privacy

### Local Processing
- **No External APIs**: All processing done locally
- **No File Storage**: Images only copied to clipboard
- **No Persistence**: Screenshots not saved permanently
- **Memory Only**: Images processed in RAM only

### Permission Requirements
- **Screen Recording**: System permission to capture screen
- **Clipboard Access**: Permission to write to system clipboard
- **No Network**: No internet connection required
- **No File System**: No file write permissions needed

## Error Handling

### Common Issues

**"Screenshot libraries not available"**
```bash
pip install mss pillow pyautogui
```

**"Failed to copy to clipboard"**
- Check system clipboard permissions
- Try different capture method
- Restart application with proper permissions

**"Permission denied" (macOS/Linux)**
- Grant screen recording permissions in System Preferences
- Add terminal/Python to accessibility permissions
- Use `sudo` if necessary for system permissions

**Windows PowerShell restrictions**
- Enable PowerShell execution policy
- Try enhanced mode with: `pip install pywin32`

### Platform-Specific Troubleshooting

**Windows:**
- Run as administrator if clipboard fails
- Check Windows privacy settings for screen capture
- Install pywin32 for enhanced clipboard support

**macOS:**
- System Preferences → Security & Privacy → Privacy → Screen Recording
- Add Terminal and Python to allowed applications
- Grant accessibility permissions if needed

**Linux:**
- Install xclip: `sudo apt-get install xclip`
- For Wayland: `sudo apt-get install wl-clipboard`
- Check X11/Wayland session type: `echo $XDG_SESSION_TYPE`

## Best Practices

### Effective Screenshot Usage
- **Be Specific**: Include context with [CAPTURE] for better analysis
- **Timing**: Capture when the relevant content is fully loaded
- **Focus**: Use region capture for specific UI elements
- **Context**: Always explain what you need help with

### Optimal Workflow
1. **Prepare Screen**: Arrange windows to show relevant content
2. **Capture**: Use [CAPTURE] with descriptive context
3. **Paste Immediately**: Paste into Claude Desktop right after capture
4. **Follow Up**: Ask specific questions about what's shown

### Multi-Monitor Tips
- **Identify Monitors**: Use monitor capture for specific screens
- **Primary Focus**: Most tools work best with primary monitor
- **Context Clarity**: Specify which monitor when asking for help

## Limitations and Considerations

### Technical Limitations
- **Clipboard Size**: Very large screenshots may have clipboard limits
- **Color Depth**: Some systems may reduce color depth in clipboard
- **Animation**: Static screenshots don't capture motion or animation
- **Protected Content**: Some applications prevent screenshot capture

### Usage Limitations
- **Manual Paste**: Must manually paste image into Claude Desktop
- **One at a Time**: Single screenshot per capture operation
- **Timing Dependent**: Screenshots capture specific moments in time
- **Context Dependent**: Effectiveness depends on clear user context

## Advanced Usage

### Automated Workflows
```python
# Programmatic capture with context
result = await detect_and_capture("[CAPTURE] analyze this dashboard")
if result["clipboard_copied"]:
    print("Ready to paste - dashboard screenshot captured")
```

### Region Optimization
```python
# Capture specific dialog box (example coordinates)
dialog_screenshot = await capture_region_to_clipboard(
    x=400, y=200, width=800, height=600,
    context="settings dialog box"
)
```

### Multi-Monitor Workflows
```python
# Capture each monitor for comprehensive analysis
for monitor in range(1, 4):  # Monitors 1, 2, 3
    await capture_monitor_to_clipboard(monitor, f"monitor {monitor} analysis")
```

## Future Enhancements

### Planned Features
- **OCR Integration**: Automatic text extraction from screenshots
- **UI Element Detection**: Automatic identification of buttons and controls
- **Annotation Tools**: Add arrows and highlights to screenshots
- **Batch Capture**: Multiple screenshots in sequence
- **Screen Recording**: Video capture for dynamic content

### Integration Roadmap
- **Email Integration**: Send screenshots via email tools
- **Document Integration**: Embed screenshots in Google Docs/Slides
- **Project Management**: Attach screenshots to task management tools
- **File Organization**: Categorize and organize captured content

---

*The Screen Capture Tool transforms AI assistance by providing visual context, enabling precise guidance and troubleshooting for any desktop application or workflow scenario.*