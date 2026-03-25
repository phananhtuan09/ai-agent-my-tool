# Pre-defined Themes

This folder contains pre-defined themes for the `frontend-design-theme-factory` skill.

## Available Themes

| Theme | Personality | Best For |
|-------|-------------|----------|
| `professional-blue` | Corporate, trustworthy | Business apps, dashboards |
| `minimal-monochrome` | Sophisticated, timeless | Portfolios, editorial |
| `bold-vibrant` | Creative, energetic | Marketing, creative tools |
| `bold-gradient` | Modern, eye-catching | Tech products, SaaS |
| `warm-organic` | Natural, friendly | Lifestyle, wellness apps |
| `warm-earthy` | Grounded, comfortable | E-commerce, hospitality |
| `creative-vibrant` | Artistic, expressive | Creative agencies, studios |
| `playful-colorful` | Fun, approachable | Kids apps, games, social |

## Theme Structure

Each theme JSON file contains:

- `name` - Display name
- `personality` - Keywords describing the aesthetic
- `colors` - Primary, neutral, and semantic color scales (50-900)
- `typography` - Font families and scale
- `spacing` - Base unit and scale
- `borderRadius` - Radius values
- `shadows` - Shadow definitions

## Usage

The theme-factory skill presents these themes when users ask for help choosing colors/fonts.

To add a custom theme:
1. Create a new `.theme.json` file in this folder
2. Follow the existing structure
3. Use descriptive personality keywords
