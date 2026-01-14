# TECHSEWA - API & INTEGRATION TEST CASES
## Version 1.0 | Date: 2025-12-21

---

## 1. BRAIN MODULE TEST CASES

### TC-BRAIN-001: Brain Module Initialization
**Objective:** Verify SmartBrain/SmartBrainPro initializes correctly
**Steps:**
1. Import brain module
2. Initialize with default database path
3. Check knowledge base loaded
4. Verify brain is ready for queries

**Expected Result:**
- Brain module imports without errors
- Brain initializes within 2 seconds
- Database loads with all entries
- No unhandled exceptions
- Brain ready to process queries

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-BRAIN-002: Local Query Resolution
**Objective:** Verify brain can solve queries from local knowledge base
**Steps:**
1. Submit query that exists in knowledge base
2. Verify answer is returned
3. Check confidence score
4. Check response time
5. Try different query formats

**Expected Result:**
- Query is understood and matched
- Appropriate answer returned
- Confidence score > 80%
- Response time < 1 second
- Query variations are recognized

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-BRAIN-003: Query Teaching
**Objective:** Verify brain can learn new problem-solution pairs
**Steps:**
1. Add new entry to knowledge base: ("test query", "test answer")
2. Query the new entry
3. Verify brain recognizes it
4. Delete the entry
5. Verify brain no longer has it

**Expected Result:**
- Entry adds successfully
- Brain immediately recognizes new entry
- Query matches the new entry
- Entry deletes successfully
- Brain forgets deleted entry

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-BRAIN-004: Confidence Threshold
**Objective:** Verify confidence threshold works correctly
**Steps:**
1. Set min_confidence to 95
2. Submit query with ambiguous match
3. Verify response or "not found"
4. Lower min_confidence to 50
5. Resubmit query

**Expected Result:**
- High threshold rejects low-confidence matches
- Low threshold accepts low-confidence matches
- Confidence score always included in response
- Threshold prevents inaccurate answers

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-BRAIN-005: Multiple Language Support
**Objective:** Verify brain supports English and Nepali
**Steps:**
1. Submit English query
2. Receive English answer
3. Submit Nepali query
4. Receive Nepali answer (if available)
5. Check language detection

**Expected Result:**
- English queries answered in English
- Nepali queries use Nepali answers if available
- Falls back to English if Nepali not available
- Language detection is automatic
- Both languages handled without errors

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 2. SYSTEM SCANNER API TEST CASES

### TC-SCAN-001: CPU Metrics Collection
**Objective:** Verify CPU metrics are accurately collected
**Steps:**
1. Call CPU metrics function
2. Verify percentage returned
3. Cross-check with system tools
4. Test during high CPU usage

**Expected Result:**
- Returns valid percentage (0-100)
- Matches system tools within 5%
- Responds within 100ms
- Accurate during high CPU usage
- No errors or exceptions

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SCAN-002: Memory Metrics Collection
**Objective:** Verify memory metrics are accurately collected
**Steps:**
1. Call memory metrics function
2. Verify percentage returned
3. Cross-check with Task Manager
4. Test with different memory loads

**Expected Result:**
- Returns valid percentage (0-100)
- Matches Task Manager within 5%
- Includes available and used memory
- Accurate under different loads
- No memory leaks from collection

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SCAN-003: Disk Metrics Collection
**Objective:** Verify disk metrics are accurately collected
**Steps:**
1. Call disk metrics function
2. Verify percentage returned
3. Check specific drives
4. Cross-check with File Explorer

**Expected Result:**
- Returns percentage for each drive
- Values match File Explorer within 5%
- All partitions included
- Includes total and free space
- No read access issues

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-SCAN-004: Network Metrics Collection
**Objective:** Verify network metrics are collected
**Steps:**
1. Call network metrics function
2. Verify bytes sent/received
3. Check during active network usage
4. Monitor for accuracy

**Expected Result:**
- Network stats returned
- Values update in real-time
- Matches system stats
- Includes upload/download speeds
- Handles disconnected state

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 3. PROBLEM DETECTION API TEST CASES

### TC-DETECT-001: High CPU Detection
**Objective:** Verify high CPU usage is detected
**Steps:**
1. Start background heavy process
2. Monitor problem detector
3. Wait for alert
4. Stop heavy process
5. Verify alert is resolved

**Expected Result:**
- High CPU detected (>80%)
- Alert generated immediately
- Alert includes severity and suggestion
- Alert clears when CPU returns to normal

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-DETECT-002: Low Memory Detection
**Objective:** Verify low memory is detected
**Steps:**
1. Fill system memory (if possible)
2. Monitor problem detector
3. Wait for alert
4. Free up memory
5. Verify alert is resolved

**Expected Result:**
- Low memory detected (<20%)
- Alert generated with suggestions
- Alert includes recommended actions
- Alert clears when memory available

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-DETECT-003: Disk Space Detection
**Objective:** Verify low disk space is detected
**Steps:**
1. Check disk space status
2. Monitor problem detector
3. Trigger alert (if nearly full)
4. Free up space
5. Verify alert resolves

**Expected Result:**
- Low disk space detected (<10%)
- Alert generated with severity
- Suggestions provided for cleanup
- Alert resolves when space freed

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 4. AUTO-HEALER API TEST CASES

### TC-HEAL-001: Healing Process Execution
**Objective:** Verify healing process can execute
**Steps:**
1. Detect a problem
2. Initiate healing process
3. Monitor healing progress
4. Wait for completion
5. Verify problem resolved

**Expected Result:**
- Healing starts within 1 second of request
- Progress updates are shown
- Healing completes within reasonable time
- No system damage from healing
- Problem is actually resolved

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-HEAL-002: Safety Verification
**Objective:** Verify healing doesn't harm system
**Steps:**
1. Create backup of critical files
2. Execute healing on test system
3. Verify no critical files modified
4. Verify no permanent changes to system
5. Verify system still fully functional

**Expected Result:**
- No critical system files deleted
- No registry changes (Windows)
- No configuration files corrupted
- System remains bootable and functional
- Can revert if needed

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 5. TTS (TEXT-TO-SPEECH) API TEST CASES

### TC-TTS-001: English TTS
**Objective:** Verify English text-to-speech works
**Steps:**
1. Initialize TTS
2. Call speak function with English text
3. Verify audio output
4. Check speech quality
5. Test various text lengths

**Expected Result:**
- Audio output is clear and intelligible
- Speech rate matches settings
- No stuttering or distortion
- Works with punctuation
- Handles special characters

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-TTS-002: Nepali TTS
**Objective:** Verify Nepali text-to-speech works
**Steps:**
1. Initialize TTS with Nepali
2. Call speak function with Nepali text
3. Verify audio output
4. Check pronunciation
5. Test various Nepali text samples

**Expected Result:**
- Audio output is understandable
- Nepali pronunciation is correct
- No distortion or artifacts
- Works with various Nepali characters
- Speech rate appropriate for Nepali

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-TTS-003: TTS Caching
**Objective:** Verify TTS cache reduces processing time
**Steps:**
1. Speak text first time (creates cache)
2. Measure time to cache file
3. Speak same text second time
4. Measure time from cache
5. Verify cache is used

**Expected Result:**
- First call: creates cache file
- Second call: uses cached file
- Cache retrieval is faster (<100ms)
- Cache files are properly stored
- Cache doesn't consume excessive disk space

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 6. ANTIVIRUS API TEST CASES

### TC-AV-001: Threat Signature Detection
**Objective:** Verify antivirus can detect known threats
**Steps:**
1. Create EICAR test file (safe malware signature)
2. Scan file with antivirus
3. Verify detection
4. Check quarantine process
5. Verify file is quarantined

**Expected Result:**
- EICAR test file is detected
- File moved to quarantine
- Alert is generated
- Quarantine prevents file execution
- Can view quarantined files list

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-AV-002: Heuristic Detection
**Objective:** Verify heuristic detection works
**Steps:**
1. Test on suspicious behavior
2. Verify heuristic analysis
3. Check confidence scores
4. Verify alert generation

**Expected Result:**
- Suspicious patterns detected
- Confidence score provided
- User informed of risk level
- Quarantine available
- False positives are minimal

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-AV-003: Real-Time Monitoring
**Objective:** Verify real-time protection works
**Steps:**
1. Enable real-time monitoring
2. Monitor file operations
3. Create/modify files
4. Verify scanning in background
5. Verify no performance impact

**Expected Result:**
- Real-time scanning enabled
- New files are scanned automatically
- Scanning doesn't block file operations
- Performance impact is minimal (<5%)
- No missed files

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 7. INTERNET LOOKUP API TEST CASES

### TC-WEB-001: Web Search Integration
**Objective:** Verify web search functionality works
**Steps:**
1. Enable internet lookup
2. Submit query not in knowledge base
3. Verify web search is performed
4. Check results returned
5. Verify response is relevant

**Expected Result:**
- Web search executes within 10 seconds
- Results returned from search engine
- Results are relevant to query
- Multiple results provided
- Source is cited

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-WEB-002: Network Error Handling
**Objective:** Verify graceful handling of network errors
**Steps:**
1. Disable internet connection
2. Attempt web search
3. Observe error handling
4. Reconnect internet
5. Retry web search

**Expected Result:**
- Error detected within 30 seconds
- Clear message: "No internet connection"
- Fallback to local knowledge base
- No hanging or crashes
- User can proceed offline

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 8. PLUGIN SYSTEM TEST CASES (if applicable)

### TC-PLUGIN-001: Plugin Loading
**Objective:** Verify plugins load correctly
**Steps:**
1. Place plugin in plugins directory
2. Restart application
3. Verify plugin is loaded
4. Check plugin functionality

**Expected Result:**
- Plugin auto-discovered
- Plugin loads without errors
- Plugin features available
- Plugin doesn't interfere with core functions

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-PLUGIN-002: Plugin Isolation
**Objective:** Verify plugins don't crash main application
**Steps:**
1. Create faulty plugin
2. Load in application
3. Trigger plugin error
4. Verify main app continues
5. Unload plugin

**Expected Result:**
- Plugin error doesn't crash app
- Error is logged
- App continues functioning
- Plugin can be disabled
- User is informed of plugin issue

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## 9. DATABASE API TEST CASES

### TC-DB-001: JSON Serialization
**Objective:** Verify database JSON serialization works
**Steps:**
1. Load problems.json
2. Parse JSON structure
3. Verify all entries loaded
4. Modify entry
5. Serialize back to JSON
6. Verify no data loss

**Expected Result:**
- JSON parses without errors
- All entries loaded correctly
- Modifications preserved
- Unicode characters handled
- File size reasonable

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

### TC-DB-002: Database Backup
**Objective:** Verify database can be backed up
**Steps:**
1. Create database backup
2. Modify database
3. Restore from backup
4. Verify data matches original
5. Check backup file integrity

**Expected Result:**
- Backup created successfully
- Backup is readable
- Restore is accurate
- No data loss in restore
- Backup timestamp recorded

**Acceptance Criteria:** ✅ PASS / ❌ FAIL

---

## SUMMARY

**Total API & Integration Test Cases:** 29
**Coverage Areas:**
- Brain Module: 5 tests
- System Scanner API: 4 tests
- Problem Detection: 3 tests
- Auto-Healer: 2 tests
- TTS API: 3 tests
- Antivirus: 3 tests
- Internet Lookup: 2 tests
- Plugin System: 2 tests
- Database: 2 tests

**Integration Testing Notes:**
- Test APIs in isolation first
- Test APIs in combination
- Test error conditions thoroughly
- Verify data integrity through multiple operations
- Check for memory leaks and resource leaks
- Verify thread safety where applicable
- Test concurrency scenarios
