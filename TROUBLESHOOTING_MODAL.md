# Troubleshooting: Incident Detail Modal Not Opening

## Issue
The incident detail modal is not opening when clicking on incidents in the Supporting Evidence section.

## Root Cause
The browser has likely cached the old JavaScript file before the modal functionality was added.

## Solution Steps

### Step 1: Hard Refresh the Browser

**Windows/Linux:**
- Press `Ctrl + Shift + R` or `Ctrl + F5`

**Mac:**
- Press `Cmd + Shift + R`

This will force the browser to reload all files without using the cache.

---

### Step 2: Clear Browser Cache Completely

**Chrome/Edge:**
1. Press `F12` to open Developer Tools
2. Right-click on the refresh button
3. Select "Empty Cache and Hard Reload"

**Firefox:**
1. Press `Ctrl + Shift + Delete`
2. Select "Cached Web Content"
3. Click "Clear Now"

---

### Step 3: Verify Files Are Loaded

1. Open Developer Tools (`F12`)
2. Go to the "Console" tab
3. Refresh the page
4. Look for any JavaScript errors (red text)
5. If you see errors related to `openIncidentDetailModal`, the file didn't reload

---

### Step 4: Force File Reload

If the above doesn't work, add a cache-busting parameter to the script tag:

**Edit `index.html` line 284:**

Change from:
```html
<script src="app.js"></script>
```

To:
```html
<script src="app.js?v=2"></script>
```

Then refresh the page.

---

### Step 5: Verify Modal HTML Exists

1. Open Developer Tools (`F12`)
2. Go to the "Elements" or "Inspector" tab
3. Press `Ctrl + F` to search
4. Search for `incident-detail-modal`
5. You should see the modal HTML structure

---

### Step 6: Test Modal Manually

1. Open Developer Tools (`F12`)
2. Go to the "Console" tab
3. Type this command and press Enter:

```javascript
openIncidentDetailModal({
    id: 'TEST001',
    text: 'Test incident description',
    resolution: 'Test resolution steps',
    score: 0.95
});
```

4. The modal should appear
5. If it does, the issue is with the click event listener
6. If it doesn't, check for JavaScript errors

---

### Step 7: Check Click Event Listeners

1. After performing a search and getting results
2. Open Developer Tools Console
3. Type:

```javascript
window.incidentData
```

4. You should see an array of incident objects
5. If it's `undefined`, the `renderEvidence` function didn't run

---

### Step 8: Restart the Server

Sometimes the server needs to be restarted to serve the updated files:

```bash
# Stop the current server (Ctrl + C in the terminal)
# Then restart:
python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

---

## Quick Test Procedure

1. **Hard refresh** the browser (`Ctrl + Shift + R`)
2. **Enter a query**: "Payment Gateway 500 errors"
3. **Click Analyze**
4. **Wait for results** to appear
5. **Hover over an incident card** - it should lift slightly
6. **Click on an incident card** - modal should appear
7. **Click X or press ESC** - modal should close

---

## Expected Behavior

### Before Click:
- Incident cards show truncated description and resolution
- Hovering over cards shows lift effect and blue border
- Cursor changes to pointer

### After Click:
- Dark overlay appears with blur effect
- White modal slides up from center
- Modal shows:
  - Incident ID in blue header
  - Full description in gray box
  - Full resolution in gray box
  - Green relevance score badge

### Closing:
- Click X button → modal fades out
- Click outside modal → modal fades out
- Press ESC key → modal fades out

---

## Still Not Working?

If none of the above works, please check:

1. **Browser Console for Errors**:
   - Open DevTools (`F12`)
   - Check Console tab for red errors
   - Share the error message

2. **Verify File Contents**:
   ```bash
   # Check if app.js has the modal function
   findstr /C:"openIncidentDetailModal" frontend\app.js
   
   # Check if index.html has the modal
   findstr /C:"incident-detail-modal" frontend\index.html
   
   # Check if style.css has the modal styles
   findstr /C:"incident-detail-modal" frontend\style.css
   ```

3. **Check Network Tab**:
   - Open DevTools → Network tab
   - Refresh page
   - Look for `app.js` in the list
   - Check if it's loading from cache (should say "200" not "304")

---

## Files Modified

- `frontend/index.html` - Modal HTML structure (lines 245-282)
- `frontend/app.js` - Modal functions and event listeners (lines 254-340)
- `frontend/style.css` - Modal styles (lines 863-1045)

All changes are in place and should work after a hard refresh!
