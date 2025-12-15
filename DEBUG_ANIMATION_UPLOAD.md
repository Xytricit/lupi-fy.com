# Debug Guide: Animation Upload Not Working

## If nothing happens when you click "Create Animation":

### Step 1: Open Browser Console
Press **F12** → Click **Console** tab

### Step 2: Try Upload Again
1. Click **"🎬 Upload Sprite Sheet"** button
2. Select a PNG/JPG file
3. Configuration modal appears
4. Click **"Create Animation"** button

### Step 3: Check Console Logs
You should see messages like:

```
Creating animation...
Animation config: {name: "walk", framesPerRow: 4, totalFrames: 8, frameDuration: 100, autoTag: true}
Animation object: {id: 1702837..., name: "walk", ...}
Added to assets: [...]
Saved to localStorage
Rendered
Modal closed
Toast shown
✅ Animation created successfully!
```

---

## If You See an Error:

Copy the error message from the console and check:

### Error: "Cannot read property 'animations' of undefined"
- **Cause**: AssetManager not initialized
- **Fix**: Refresh the page, try again

### Error: "showToast is not defined"
- **Cause**: Missing toast notification function
- **Fix**: Check if page loaded completely

### Error: "Cannot read property 'querySelector' of null"
- **Cause**: Modal HTML didn't render properly
- **Fix**: Check browser for JavaScript errors above

---

## Manual Test (If Modal Isn't Appearing):

Open console and type:

```javascript
// Check if AssetManager exists
console.log('AssetManager:', AssetManager);

// Check if animation upload is attached
console.log('Upload input:', document.getElementById('animationUpload'));

// Manually trigger animation config
AssetManager.showSpriteSheetConfig(
  'test.png',
  'data:image/png;base64,iVBORw0KGgoAAAANS...',  // any valid image data URI
  256,  // width
  128   // height
);
```

---

## Verify Animation Was Created:

In console, type:

```javascript
// Check all animations
console.log('Animations:', AssetManager.assets.animations);

// Should output something like:
// [{id: 123, name: "walk", totalFrames: 8, frameDuration: 100, ...}]

// Check localStorage
console.log('Saved:', localStorage.getItem('lupiforge_assets'));
```

If you see your animation in the array → **Animation was created successfully!**

---

## To View Your Animation:

1. If animation exists in console, it should auto-appear in Asset Panel
2. Click **"🎬 Animations"** tab
3. Your animation thumbnail should show with first frame preview
4. Click it to open **Animation Editor**

---

## Still Not Working?

1. **Check for JS errors**: Look for red errors in console (F12)
2. **Refresh page**: Sometimes initialization issue
3. **Try different file**: Make sure PNG/JPG is valid
4. **Check file size**: Huge images might timeout
5. **Use a test image**: Try a small (256x256) sprite sheet

---

## Quick Test Sprite Sheet:

Create a simple 256x256 image with 4 frames in a row (64x256 each):
- Frame 1: Red square
- Frame 2: Green square
- Frame 3: Blue square
- Frame 4: Yellow square

Upload it as:
- Name: "test"
- Frames Per Row: 4
- Total Frames: 4
- Duration: 100ms

Should see a 4-frame animation preview!

---

## If Modal Never Appears:

The modal might not be created. Check:

```javascript
// Is the file being read?
// Add this to your upload input:
document.getElementById('animationUpload').addEventListener('change', (e) => {
  console.log('File selected:', e.target.files[0]);
});

// Try uploading again and check console
```

---

## Get Help:

Post the **console output** and **any red errors** - that will show exactly what's failing.
