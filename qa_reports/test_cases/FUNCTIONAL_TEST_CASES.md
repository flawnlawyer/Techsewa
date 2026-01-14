# TECHSEWA ULTIMATE PRO - FUNCTIONAL TEST CASES
## Version 1.0 | Date: 2025-12-21

---

## 1. CONFIGURATION MANAGEMENT TEST CASES

### TC-CFG-001: Load Default Configuration
**Objective:** Verify application loads with default configuration when config.json is missing
**Steps:**
1. Delete config.json file
2. Launch application
3. Verify default values are applied

**Expected Result:** 
- Application launches without errors
- Default config values applied: enable_internet=true, enable_voice=true, min_confidence=80, theme=light

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-CFG-002: Save Configuration Changes
**Objective:** Verify configuration changes are saved to file
**Steps:**
1. Open Settings tab
2. Change theme to "dark"
3. Change voice_rate to 180
4. Click Save Settings
5. Close and reopen application
6. Verify settings are restored

**Expected Result:** 
- Settings saved to config.json
- Settings persist after application restart
- No error messages displayed

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-CFG-003: Invalid Configuration Handling
**Objective:** Verify graceful handling of corrupted config files
**Steps:**
1. Corrupt config.json with invalid JSON
2. Launch application
3. Observe error handling

**Expected Result:** 
- Application detects invalid JSON
- Falls back to default configuration
- Displays user-friendly error message
- Creates backup of corrupted file

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 2. USER INTERFACE TEST CASES

### TC-UI-001: Application Startup
**Objective:** Verify application starts successfully and displays main window
**Steps:**
1. Run: python ui.py
2. Wait for window to fully load
3. Check all tabs are visible

**Expected Result:**
- Window displays with title "Techsewa Ultimate Pro 5.0"
- Window size is 1400x900 pixels
- All 6 tabs visible: Assistant, System Info, Alerts, Settings, Knowledge Base, Brain Stats
- No error messages in console

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-UI-002: Tab Navigation
**Objective:** Verify all tabs are accessible and functional
**Steps:**
1. Click on each tab sequentially: Assistant, System Info, Alerts, Settings, Knowledge Base, Brain Stats
2. Verify tab content loads correctly
3. Check for any rendering issues

**Expected Result:**
- All tabs open without errors
- Content loads within 2 seconds
- UI remains responsive
- No visual glitches or overlapping elements

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-UI-003: Chat Interface Functionality
**Objective:** Verify chat display and message formatting
**Steps:**
1. Open Assistant tab
2. Type a sample query: "How do I fix slow computer?"
3. Click Send or press Enter
4. Verify message appears in chat display

**Expected Result:**
- User message appears with "You:" prefix
- System response appears below with "Techsewa:" prefix
- Messages are properly formatted with timestamps
- Chat scrolls to show latest message
- Emojis display correctly (✅, ⚠️, etc.)

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-UI-004: Settings Validation
**Objective:** Verify settings input validation
**Steps:**
1. Open Settings tab
2. Try to set confidence below 0
3. Try to set confidence above 100
4. Try to set voice_rate to invalid value

**Expected Result:**
- Invalid inputs are rejected
- Error message explains valid range
- Original valid value is retained
- Settings cannot be saved with invalid values

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 3. SYSTEM SCANNING TEST CASES

### TC-SYS-001: System Scan Initiation
**Objective:** Verify system scan starts and completes
**Steps:**
1. Open System Info tab
2. Click "Run Full Scan"
3. Monitor scan progress
4. Wait for completion

**Expected Result:**
- Scan initiates within 1 second of clicking
- Progress bar appears and updates
- CPU usage shows live metrics
- Memory usage shows live metrics
- Disk usage shows live metrics
- Scan completes within 10 seconds

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SYS-002: System Metrics Collection
**Objective:** Verify accurate system metrics are displayed
**Steps:**
1. Open System Info tab
2. Note CPU, Memory, Disk percentages
3. Cross-reference with Task Manager
4. Verify values are within ±5% tolerance

**Expected Result:**
- CPU percentage matches Task Manager
- Memory percentage matches Task Manager
- Disk percentage matches File Explorer
- All metrics update in real-time (every 1-2 seconds)
- No negative values displayed

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SYS-003: Export System Report
**Objective:** Verify system report export functionality
**Steps:**
1. Complete a system scan
2. Click "Export Report"
3. Choose save location
4. Verify file creation
5. Open exported file

**Expected Result:**
- Export dialog appears
- File is saved in selected location
- File format is human-readable (TXT or JSON)
- Report contains all scan data
- Report includes timestamp
- File size is reasonable (< 5MB)

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 4. KNOWLEDGE BASE TEST CASES

### TC-KB-001: View Knowledge Base
**Objective:** Verify knowledge base loads and displays entries
**Steps:**
1. Open Knowledge Base tab
2. Wait for entries to load
3. Scroll through entries
4. Check entry details

**Expected Result:**
- Knowledge base displays all entries
- Each entry shows question and answers in both languages
- Entries are searchable
- Total entry count is displayed
- Entries load within 2 seconds

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-KB-002: Add Knowledge Entry
**Objective:** Verify new knowledge entries can be added
**Steps:**
1. Open Knowledge Base tab
2. Click "Add Entry"
3. Fill in: Question, English Answer, Nepali Answer
4. Click Save
5. Verify entry appears in list

**Expected Result:**
- Add Entry dialog opens
- All fields accept input
- Question field is mandatory
- English Answer field is mandatory
- Nepali Answer field is optional
- New entry appears in knowledge base list
- Entry is immediately searchable

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-KB-003: Search Knowledge Base
**Objective:** Verify knowledge base search functionality
**Steps:**
1. Open Knowledge Base tab
2. Type search term in search box
3. Observe results filtered in real-time
4. Try multiple search terms
5. Clear search

**Expected Result:**
- Results update as you type
- Only matching entries are displayed
- Search is case-insensitive
- Search works on both questions and answers
- Clear search shows all entries again
- Search completes within 500ms

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 5. ALERTS AND NOTIFICATIONS TEST CASES

### TC-ALERT-001: Alert Display
**Objective:** Verify system alerts are displayed correctly
**Steps:**
1. Open Alerts tab
2. Trigger a system issue (e.g., high CPU usage)
3. Observe alert appearance
4. Check alert details

**Expected Result:**
- Alerts appear in Alerts tab
- Alert includes: severity level, description, timestamp
- Alert color coding: Red for critical, Orange for warning, Yellow for info
- Alert counter updates
- Alerts are sortable by severity

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-ALERT-002: Alert Resolution
**Objective:** Verify alerts can be addressed
**Steps:**
1. Display an alert
2. Click "Heal" or "Resolve"
3. Monitor resolution process
4. Verify alert status changes

**Expected Result:**
- Healing process starts automatically
- Progress updates are shown
- Alert status changes to "Resolved" on success
- Alert can be dismissed
- Resolution history is logged

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 6. VOICE FUNCTIONALITY TEST CASES

### TC-VOICE-001: Text-to-Speech Output
**Objective:** Verify text-to-speech functionality works
**Steps:**
1. Enable voice in settings
2. Submit a query
3. Wait for audio output
4. Listen to response

**Expected Result:**
- Audio plays through speakers
- Voice is clear and intelligible
- Speaking rate matches settings
- No stuttering or distortion
- Volume matches settings level

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-VOICE-002: Language Support
**Objective:** Verify TTS supports English and Nepali
**Steps:**
1. Submit English query
2. Listen to English response
3. Set language to Nepali
4. Submit Nepali query
5. Listen to Nepali response

**Expected Result:**
- English responses use English voice
- Nepali responses use appropriate accent/pronunciation
- Both languages are understandable
- Language auto-detects based on input

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 7. NETWORK CONNECTIVITY TEST CASES

### TC-NET-001: Internet Status Detection
**Objective:** Verify internet connectivity is detected
**Steps:**
1. Ensure internet is connected
2. Check Settings: "Enable Internet Lookup"
3. Disable internet (disconnect network)
4. Observe application behavior
5. Reconnect internet

**Expected Result:**
- Application detects internet status correctly
- Online queries use internet lookup when enabled
- Offline queries use local knowledge base only
- No network timeouts exceed 30 seconds
- User is informed of connection status

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-NET-002: Network Timeout Handling
**Objective:** Verify graceful handling of network issues
**Steps:**
1. Enable internet lookup
2. Simulate slow network connection
3. Submit query requiring internet
4. Wait for timeout
5. Observe error handling

**Expected Result:**
- Network timeouts occur within 30 seconds (not indefinite)
- Fallback to local knowledge base
- User sees informative message
- Application remains responsive
- User can retry or proceed offline

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 8. PERFORMANCE TEST CASES

### TC-PERF-001: Application Startup Time
**Objective:** Verify application launches within acceptable time
**Steps:**
1. Close application completely
2. Clear memory cache
3. Run: python ui.py
4. Time until window is fully responsive
5. Repeat 3 times

**Expected Result:**
- Average startup time < 5 seconds
- All UI elements responsive after startup
- No hangs or delays during initialization
- Consistent startup times

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-PERF-002: Query Response Time
**Objective:** Verify queries are answered quickly
**Steps:**
1. Open Assistant tab
2. Submit various queries
3. Measure response time (from send to answer displayed)
4. Test 10 different queries
5. Calculate average response time

**Expected Result:**
- Local knowledge base queries: < 1 second
- Internet lookup queries: < 5 seconds
- UI remains responsive during processing
- Response times consistent
- No memory leaks detected over 100 queries

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-PERF-003: Memory Usage
**Objective:** Verify memory usage is reasonable
**Steps:**
1. Monitor memory before launch
2. Launch application
3. Run 50 queries
4. Monitor memory after queries
5. Run system scan 5 times
6. Check for memory leaks

**Expected Result:**
- Initial memory usage < 200MB
- Memory doesn't increase significantly after 50 queries
- Memory returns to near-initial level after operations
- No memory leaks detected
- Peak memory usage < 500MB

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 9. DATA INTEGRITY TEST CASES

### TC-DATA-001: Knowledge Base Integrity
**Objective:** Verify knowledge base data is not corrupted
**Steps:**
1. Perform multiple read/write operations
2. Add entries, search, delete
3. Export and reimport knowledge base
4. Verify data consistency

**Expected Result:**
- All data written is correctly read back
- No data loss during operations
- Exported file matches database content
- Special characters and Unicode preserved
- Database file integrity maintained

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-DATA-002: Configuration Persistence
**Objective:** Verify configuration changes persist correctly
**Steps:**
1. Change all configurable settings
2. Save configuration
3. Close application
4. Reopen application
5. Verify all settings restored

**Expected Result:**
- All settings saved to config.json
- No settings are lost on restart
- Settings order is preserved in JSON
- Backup of previous config exists (optional)

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 10. SECURITY TEST CASES

### TC-SEC-001: Input Validation
**Objective:** Verify application validates user inputs
**Steps:**
1. Try to submit empty query
2. Try to add entry with special characters
3. Try to input extremely long text (10MB)
4. Try to submit JSON payloads
5. Try SQL-like injections

**Expected Result:**
- Empty inputs rejected gracefully
- Special characters handled safely
- Extremely long inputs truncated or rejected
- No code injection possible
- User sees clear validation error messages

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SEC-002: File Access Control
**Objective:** Verify sensitive files are protected
**Steps:**
1. Check file permissions on config.json
2. Check file permissions on problems.json
3. Try to access files from other processes
4. Verify quarantine directory is secured

**Expected Result:**
- Config files readable only by application
- Database files have appropriate permissions
- Quarantine directory isolated from user files
- No sensitive data in logs
- Passwords/tokens not stored in plain text

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 11. COMPATIBILITY TEST CASES

### TC-COMPAT-001: Windows Compatibility
**Objective:** Verify application works on Windows
**Steps:**
1. Test on Windows 10/11
2. Check for Windows-specific path handling
3. Verify all dependencies work
4. Test with different screen DPIs

**Expected Result:**
- Application launches without DLL errors
- File paths handled correctly
- GUI displays properly at different DPIs
- No platform-specific crashes

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-COMPAT-002: Python Version Compatibility
**Objective:** Verify application works with Python 3.8+
**Steps:**
1. Test with Python 3.8
2. Test with Python 3.9
3. Test with Python 3.10
4. Test with Python 3.11
5. Test with Python 3.12 (if available)

**Expected Result:**
- Application runs on all tested Python versions
- No syntax errors
- All dependencies compatible
- No version-specific warnings

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 12. ERROR RECOVERY TEST CASES

### TC-ERR-001: Crash Recovery
**Objective:** Verify application recovers gracefully from errors
**Steps:**
1. Delete required file and restart
2. Corrupt database and restart
3. Trigger unhandled exceptions
4. Force-close application

**Expected Result:**
- Missing files trigger graceful fallback
- Corrupted database is detected and recovered
- Unhandled exceptions are logged
- Application can be restarted without residual issues

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-ERR-002: Error Logging
**Objective:** Verify errors are properly logged
**Steps:**
1. Trigger various errors
2. Check application logs
3. Verify log entries contain useful information

**Expected Result:**
- All errors logged with timestamp
- Log includes error type, message, traceback
- Logs are readable and organized
- Log files don't grow excessively (< 50MB per session)

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## SUMMARY

**Total Test Cases:** 31
**Test Coverage Areas:**
- Configuration Management: 3 tests
- User Interface: 4 tests
- System Scanning: 3 tests
- Knowledge Base: 3 tests
- Alerts: 2 tests
- Voice: 2 tests
- Network: 2 tests
- Performance: 3 tests
- Data Integrity: 2 tests
- Security: 2 tests
- Compatibility: 2 tests
- Error Recovery: 2 tests

**Pass/Fail Tracking:**
Document results in the QA report folder after execution.
