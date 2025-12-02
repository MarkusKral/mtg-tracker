# Official MTG Mana Symbols - Implementation

## Overview
The application now uses **official MTG mana symbols** from the [MTG Wiki](https://mtg.fandom.com/wiki/Category:Mana_symbols).

## Mana Symbol Files

All symbols are located in: `frontend/assets/avatars/`

### Symbol Sources

| Color | File | Source | Status |
|-------|------|--------|--------|
| **White** | `W.svg` | Hand-crafted (Wikia CDN served WEBP) | ✅ Active |
| **Blue** | `U.svg` | [Official MTG Wiki](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/9/9f/U.svg) | ✅ Active |
| **Black** | `B.svg` | [Official MTG Wiki](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/2/2f/B.svg) | ✅ Active |
| **Red** | `R.svg` | [Official MTG Wiki](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/8/87/R.svg) | ✅ Active |
| **Green** | `G.svg` | [Official MTG Wiki](https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/8/88/G.svg) | ✅ Active |

## Color Specifications

### White (W)
- **Background**: Light cream (`#f0f2c0`)
- **Symbol**: Five-pointed sun/star
- **Theme**: Plains, order, protection, healing

### Blue (U)
- **Background**: Light blue (`#aae0fa`)
- **Symbol**: Water droplet
- **Theme**: Islands, control, card draw, counters

### Black (B)
- **Background**: Grey-beige (`#cbc2bf`)
- **Symbol**: Skull
- **Theme**: Swamps, removal, graveyard, sacrifice

### Red (R)
- **Background**: Light red/orange (`#f9aa8f`)
- **Symbol**: Fireball/flame
- **Theme**: Mountains, burn, aggro, chaos

### Green (G)
- **Background**: Light green (`#9bd3ae`)
- **Symbol**: Tree/foliage
- **Theme**: Forests, ramp, creatures, growth

## Technical Details

### SVG Format
- **ViewBox**: `0 0 600 600` (standardized across all symbols)
- **Format**: Vector (scalable to any size)
- **Colors**: Match official MTG color palette
- **License**: Mana symbols are copyright Wizards of the Coast

### Integration

The symbols are used in:
1. **Player join screen** - Color selection
2. **Profile settings modal** - Change colors anytime
3. **Match listings** - Show opponent colors
4. **Standings table** - Display player deck colors
5. **Live dashboard** - Real-time match display

### CSS Classes

```css
.color-W { background-image: url('assets/avatars/W.svg'); }
.color-U { background-image: url('assets/avatars/U.svg'); }
.color-B { background-image: url('assets/avatars/B.svg'); }
.color-R { background-image: url('assets/avatars/R.svg'); }
.color-G { background-image: url('assets/avatars/G.svg'); }
```

## Usage in Application

### Display Colors
```javascript
// Colors stored as JSON array in database
colors: ["W", "U", "R"]  // Jeskai colors

// Displayed as:
<div class="color-icon color-W"></div>
<div class="color-icon color-U"></div>
<div class="color-icon color-R"></div>
```

### Color Selection
Players can select up to 5 colors representing their deck's mana base:
- Mono-color: `["G"]` - Green
- Two-color: `["U", "B"]` - Dimir
- Three-color: `["W", "U", "R"]` - Jeskai
- Four-color: `["B", "R", "G", "W"]` - Non-blue
- Five-color: `["W", "U", "B", "R", "G"]` - All colors

## Benefits

✅ **Authentic** - Official MTG mana symbols from Wizards of the Coast
✅ **Professional** - High-quality vector graphics
✅ **Recognizable** - Familiar to all Magic players
✅ **Scalable** - SVG format works at any size
✅ **Accessible** - Clear visual representation of deck colors

## Copyright Notice

Mana symbols are trademark and copyright of Wizards of the Coast LLC, a subsidiary of Hasbro, Inc. 
This application uses them for tournament organization purposes only.

## References

- [MTG Wiki - Mana Symbols](https://mtg.fandom.com/wiki/Category:Mana_symbols)
- [Official MTG Website](https://magic.wizards.com/)
- [Wizards of the Coast](https://company.wizards.com/)

