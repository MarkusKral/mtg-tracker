# Avatar/Profile Picture Upload Feature

## Overview
Players can now upload custom profile pictures (avatars) in addition to selecting their deck colors.

## Features Implemented

### ✅ Avatar Upload
- Upload custom profile pictures (JPG, PNG, GIF)
- Maximum file size: 5MB
- Instant preview before saving
- Remove/clear avatar option

### ✅ Avatar Display
- Shows in player profile header (matches screen)
- Circular avatar with 👤 placeholder if no avatar set
- Avatar displayed alongside name and deck colors

### ✅ Profile Settings Modal
- Accessible via "⚙️ Profile" button in matches screen
- Two sections:
  1. **Profile Picture** - Upload/remove avatar
  2. **Deck Colors** - Select mana colors (W, U, B, R, G)

## How to Use

### For Players:

1. **Access Profile Settings**
   - Go to the matches screen
   - Click "⚙️ Profile" button in top-right

2. **Upload Avatar**
   - Click "Upload Image" button
   - Select an image file (JPG, PNG, or GIF)
   - Preview appears immediately
   - Click "Save Changes" to upload

3. **Remove Avatar**
   - Click "Remove" button in profile settings
   - Click "Save Changes" to confirm removal

4. **Change Anytime**
   - You can update your avatar and colors at any time
   - Changes take effect immediately after saving

## Technical Details

### Backend API
Endpoint: `PUT /api/players/{player_id}/profile`

**Request (FormData):**
```
avatar: <file>           // Optional: Image file
colors: '["W","U"]'      // Optional: JSON array of colors
```

**Response:**
```json
{
  "player_id": 1,
  "name": "Player Name",
  "avatar_url": "/uploads/avatars/player_1_uuid.jpg",
  "colors": ["W", "U"]
}
```

### File Storage
- **Location**: `backend/uploads/avatars/`
- **Naming**: `player_{id}_{uuid}.{ext}`
- **Access**: `http://localhost:8000/uploads/avatars/{filename}`
- **Served via**: FastAPI StaticFiles

### Validation
- ✅ File size limit: 5MB
- ✅ File type: Images only (image/*)
- ✅ Client-side validation before upload
- ✅ Instant preview with FileReader API

### Frontend Components

#### Avatar Preview (Header)
```html
<div class="w-12 h-12 rounded-full overflow-hidden bg-gray-700">
  <img id="player-avatar-display" class="w-full h-full object-cover">
  <span id="player-avatar-placeholder" class="text-2xl">👤</span>
</div>
```

#### Upload Modal
```html
<input type="file" id="avatar-upload" accept="image/*">
<button onclick="removeAvatar()">Remove</button>
```

## User Experience

### Visual Feedback
- **No Avatar**: Shows 👤 placeholder emoji
- **With Avatar**: Shows uploaded image in circular frame
- **Upload Preview**: Image previews immediately after selection
- **Success**: "Profile updated successfully!" message

### Error Handling
- File too large (>5MB): Alert message
- Invalid file type: Alert message
- Upload failure: Detailed error message

## File Management

### Unique Filenames
Each uploaded avatar gets a unique filename:
```
player_1_a3f8b2c4-5d6e-7f8g-9h0i-1j2k3l4m5n6o.jpg
```

### Storage Structure
```
backend/
  uploads/
    avatars/
      player_1_uuid1.jpg
      player_2_uuid2.png
      player_3_uuid3.gif
```

### Cleanup
Old avatars are NOT automatically deleted when uploading a new one. To implement cleanup:
1. Track previous avatar path in database
2. Delete old file when uploading new one
3. Delete file when player is removed

## Future Enhancements (Optional)

### Possible Additions:
- ✨ Avatar presets (choose from gallery)
- ✨ Image cropping/editing before upload
- ✨ Compression for large images
- ✨ Avatar moderation/approval system
- ✨ Default avatars based on deck colors
- ✨ Integration with Gravatar

## Security Considerations

### Current Implementation:
- ✅ File size limits (5MB)
- ✅ File type validation (images only)
- ✅ Unique filenames (prevents overwrites)
- ✅ Separate upload directory

### Recommended Additions:
- ⚠️ Server-side file type validation (check magic bytes)
- ⚠️ Image processing/sanitization
- ⚠️ Rate limiting on uploads
- ⚠️ Disk space monitoring

## Browser Compatibility

### Tested/Supported:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Requirements:
- FileReader API (for preview)
- FormData API (for upload)
- fetch API (for HTTP requests)

All modern browsers support these features.

## Example Usage

```javascript
// Upload avatar
const formData = new FormData();
formData.append('avatar', fileInput.files[0]);
formData.append('colors', JSON.stringify(['W', 'U', 'R']));

await fetch(`${API_URL}/api/players/${playerId}/profile`, {
    method: 'PUT',
    body: formData
});
```

## Summary

Players can now:
✅ Upload custom profile pictures
✅ Preview images before uploading
✅ Remove avatars
✅ See avatars in their profile header
✅ Update avatars anytime (not just on registration)

This enhances personalization and makes it easier to identify players in the tournament!

