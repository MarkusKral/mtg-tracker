# Profile Settings Update - Change Colors Anytime

## Changes Made

### 1. New Official MTG Mana Symbol SVGs ✅
Created high-quality SVG mana symbols that match the official MTG style:
- **W.svg** - White mana (sun/star symbol)
- **U.svg** - Blue mana (water droplet symbol)
- **B.svg** - Black mana (skull symbol)
- **R.svg** - Red mana (flame symbol)
- **G.svg** - Green mana (tree/leaf symbol)

Location: `frontend/assets/avatars/`

### 2. Profile Settings Modal ✅
Added a profile settings modal to the player view where users can:
- View their current deck colors
- Add or remove colors at any time
- Select up to 5 colors
- Save changes instantly

**How to Access:**
- Click the "⚙️ Profile" button in the top-right of the matches screen

### 3. Updated Color Display ✅
- All screens now use the new official mana symbol SVGs
- Colors display consistently across:
  - Player profile header
  - Match listings
  - Opponent information
  - Standings table
  - Live dashboard

### 4. Updated Files

**Frontend:**
- `frontend/player.html` - Added profile modal and settings functionality
- `frontend/dashboard.html` - Updated to use new SVG files
- `frontend/assets/avatars/` - New mana symbol SVGs

**Backend:**
- No changes needed - the update profile endpoint was already available

## How to Use

### For Players:

1. **Initial Setup** (when joining tournament):
   - Select your deck colors on the join screen
   - Colors are optional but recommended

2. **Update Anytime**:
   - Go to the matches screen
   - Click "⚙️ Profile" button (top-right)
   - Click on mana symbols to add/remove colors
   - Click "Save Changes"

3. **Color Selection Tips**:
   - Click a color to select it (blue glow appears)
   - Click again to deselect
   - Maximum 5 colors can be selected
   - Colors help opponents identify your deck strategy

### Color Meanings:
- **W (White)** - Plains, healing, protection, order
- **U (Blue)** - Islands, counters, card draw, control
- **B (Black)** - Swamps, removal, graveyard, sacrifice
- **R (Red)** - Mountains, burn, aggro, chaos
- **G (Green)** - Forests, ramp, creatures, growth

## Technical Details

### API Endpoint Used:
```
PUT /api/players/{player_id}/profile
```

**Request (FormData):**
```
colors: '["W","U","R"]'  // JSON string array
```

**No Authentication Required** - Players can update their own profile

### Mana Symbol Files:
- Format: SVG (vector, scalable)
- Size: 600x600 viewBox (scales to any size)
- Style: Official MTG-inspired design
- Colors: Match official MTG color palette

## Benefits

✅ **Better UX** - Players can change colors without re-registering
✅ **Flexibility** - Update deck colors between rounds
✅ **Visual** - Official-looking mana symbols enhance MTG theme
✅ **Informative** - Opponents can see deck colors at a glance
✅ **Accessible** - Simple modal interface with clear icons

## Removed Files

Old placeholder SVG files have been removed:
- ~~white.svg~~ → W.svg
- ~~blue.svg~~ → U.svg
- ~~black.svg~~ → B.svg
- ~~red.svg~~ → R.svg
- ~~green.svg~~ → G.svg

