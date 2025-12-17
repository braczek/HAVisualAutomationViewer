"""Theme Manager - Manage and apply themes."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import json
import os

_LOGGER = logging.getLogger(__name__)


@dataclass
class ColorScheme:
    """Color palette definition."""

    primary: str  # e.g., #4CAF50
    secondary: str
    success: str
    warning: str
    error: str
    background: str
    text: str
    border: str


@dataclass
class AutomationTheme:
    """Complete theme definition."""

    name: str
    description: str

    # Component colors
    trigger_color: str
    condition_color: str
    action_color: str
    metadata_color: str

    # Advanced
    color_scheme: Dict[str, str]  # Using dict for JSON compatibility
    edge_color: str
    highlight_color: str
    disabled_color: str

    # UI
    card_background: str
    card_border: str
    text_color: str
    accent_color: str

    # Metadata
    author: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    user_created: bool = False
    is_builtin: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ThemeManager:
    """Manage theme definitions and applications."""

    # Built-in themes
    BUILTIN_THEMES = {
        "default": {
            "name": "Default",
            "description": "Material Design colors - balanced and clear",
            "trigger_color": "#4CAF50",  # Green
            "condition_color": "#FFC107",  # Amber
            "action_color": "#2196F3",  # Blue
            "metadata_color": "#9E9E9E",  # Grey
            "edge_color": "#616161",
            "highlight_color": "#FF9800",
            "disabled_color": "#E0E0E0",
            "color_scheme": {
                "primary": "#2196F3",
                "secondary": "#03DAC6",
                "success": "#4CAF50",
                "warning": "#FFC107",
                "error": "#F44336",
                "background": "#FFFFFF",
                "text": "#212121",
                "border": "#E0E0E0",
            },
            "card_background": "#FFFFFF",
            "card_border": "#E0E0E0",
            "text_color": "#212121",
            "accent_color": "#2196F3",
        },
        "dark": {
            "name": "Dark Mode",
            "description": "Optimized for night viewing and eye comfort",
            "trigger_color": "#81C784",  # Light Green
            "condition_color": "#FFD54F",  # Light Amber
            "action_color": "#64B5F6",  # Light Blue
            "metadata_color": "#BDBDBD",  # Light Grey
            "edge_color": "#BDBDBD",
            "highlight_color": "#FFB74D",
            "disabled_color": "#424242",
            "color_scheme": {
                "primary": "#64B5F6",
                "secondary": "#4DB8FF",
                "success": "#81C784",
                "warning": "#FFD54F",
                "error": "#EF5350",
                "background": "#121212",
                "text": "#FFFFFF",
                "border": "#424242",
            },
            "card_background": "#1E1E1E",
            "card_border": "#424242",
            "text_color": "#FFFFFF",
            "accent_color": "#64B5F6",
        },
        "high_contrast": {
            "name": "High Contrast",
            "description": "Accessibility - maximum contrast for visibility",
            "trigger_color": "#00AA00",  # Bright Green
            "condition_color": "#FFAA00",  # Bright Orange
            "action_color": "#0066FF",  # Bright Blue
            "metadata_color": "#333333",  # Dark Grey
            "edge_color": "#000000",
            "highlight_color": "#FF0000",
            "disabled_color": "#CCCCCC",
            "color_scheme": {
                "primary": "#0066FF",
                "secondary": "#00CCFF",
                "success": "#00AA00",
                "warning": "#FFAA00",
                "error": "#FF0000",
                "background": "#FFFFFF",
                "text": "#000000",
                "border": "#000000",
            },
            "card_background": "#FFFFFF",
            "card_border": "#000000",
            "text_color": "#000000",
            "accent_color": "#0066FF",
        },
        "colorblind_deuteranopia": {
            "name": "Colorblind (Deuteranopia)",
            "description": "Optimized for red-green colorblind users",
            "trigger_color": "#0173B2",  # Blue
            "condition_color": "#DE8F05",  # Orange
            "action_color": "#CC78BC",  # Purple
            "metadata_color": "#999999",  # Grey
            "edge_color": "#029E73",
            "highlight_color": "#CA9161",
            "disabled_color": "#E0E0E0",
            "color_scheme": {
                "primary": "#0173B2",
                "secondary": "#DE8F05",
                "success": "#029E73",
                "warning": "#DE8F05",
                "error": "#CC78BC",
                "background": "#FFFFFF",
                "text": "#000000",
                "border": "#CCCCCC",
            },
            "card_background": "#FFFFFF",
            "card_border": "#CCCCCC",
            "text_color": "#000000",
            "accent_color": "#0173B2",
        },
        "professional": {
            "name": "Professional",
            "description": "Professional appearance for documentation",
            "trigger_color": "#1B5E20",  # Dark Green
            "condition_color": "#E65100",  # Dark Orange
            "action_color": "#0D47A1",  # Dark Blue
            "metadata_color": "#424242",  # Charcoal
            "edge_color": "#212121",
            "highlight_color": "#FF6F00",
            "disabled_color": "#BDBDBD",
            "color_scheme": {
                "primary": "#0D47A1",
                "secondary": "#1565C0",
                "success": "#1B5E20",
                "warning": "#E65100",
                "error": "#B71C1C",
                "background": "#FFFFFF",
                "text": "#212121",
                "border": "#9E9E9E",
            },
            "card_background": "#F5F5F5",
            "card_border": "#9E9E9E",
            "text_color": "#212121",
            "accent_color": "#0D47A1",
        },
        "pastel": {
            "name": "Pastel",
            "description": "Soft colors for presentations",
            "trigger_color": "#A5D6A7",  # Soft Green
            "condition_color": "#FFE082",  # Soft Yellow
            "action_color": "#90CAF9",  # Soft Blue
            "metadata_color": "#EEEEEE",  # Light Grey
            "edge_color": "#BCAAA4",
            "highlight_color": "#FFAB91",
            "disabled_color": "#F5F5F5",
            "color_scheme": {
                "primary": "#90CAF9",
                "secondary": "#80DEEA",
                "success": "#A5D6A7",
                "warning": "#FFE082",
                "error": "#EF9A9A",
                "background": "#FFFFFF",
                "text": "#424242",
                "border": "#E0E0E0",
            },
            "card_background": "#FAFAFA",
            "card_border": "#E0E0E0",
            "text_color": "#424242",
            "accent_color": "#90CAF9",
        },
    }

    def __init__(self, hass, theme_storage_dir: str = "visualautoview_themes"):
        """Initialize theme manager."""
        self.hass = hass
        self.theme_storage_dir = os.path.join(hass.config.path(), theme_storage_dir)
        self._themes: Dict[str, AutomationTheme] = {}
        self._current_theme = "default"
        self._user_preference = None

        # Ensure storage directory exists
        os.makedirs(self.theme_storage_dir, exist_ok=True)

        _LOGGER.debug(
            f"Theme Manager initialized with storage at {self.theme_storage_dir}"
        )

    async def initialize(self) -> None:
        """Initialize themes (load built-ins and user themes)."""
        try:
            # Load built-in themes
            self._load_builtin_themes()

            # Load user themes
            await self._load_user_themes()

            _LOGGER.info(f"Theme Manager loaded {len(self._themes)} themes")

        except Exception as err:
            _LOGGER.error(f"Error initializing themes: {err}", exc_info=True)
            raise

    def _load_builtin_themes(self) -> None:
        """Load built-in themes."""
        for theme_id, theme_data in self.BUILTIN_THEMES.items():
            theme = AutomationTheme(
                name=theme_data["name"],
                description=theme_data["description"],
                trigger_color=theme_data["trigger_color"],
                condition_color=theme_data["condition_color"],
                action_color=theme_data["action_color"],
                metadata_color=theme_data["metadata_color"],
                edge_color=theme_data["edge_color"],
                highlight_color=theme_data["highlight_color"],
                disabled_color=theme_data["disabled_color"],
                color_scheme=theme_data["color_scheme"],
                card_background=theme_data["card_background"],
                card_border=theme_data["card_border"],
                text_color=theme_data["text_color"],
                accent_color=theme_data["accent_color"],
                is_builtin=True,
            )
            self._themes[theme_id] = theme

    async def _load_user_themes(self) -> None:
        """Load user-created themes from storage."""
        try:
            themes_file = os.path.join(self.theme_storage_dir, "themes.json")

            if os.path.exists(themes_file):
                with open(themes_file, "r") as f:
                    themes_data = json.load(f)

                for theme_id, theme_data in themes_data.items():
                    theme = AutomationTheme(
                        name=theme_data["name"],
                        description=theme_data["description"],
                        trigger_color=theme_data["trigger_color"],
                        condition_color=theme_data["condition_color"],
                        action_color=theme_data["action_color"],
                        metadata_color=theme_data["metadata_color"],
                        edge_color=theme_data["edge_color"],
                        highlight_color=theme_data["highlight_color"],
                        disabled_color=theme_data["disabled_color"],
                        color_scheme=theme_data["color_scheme"],
                        card_background=theme_data["card_background"],
                        card_border=theme_data["card_border"],
                        text_color=theme_data["text_color"],
                        accent_color=theme_data["accent_color"],
                        author=theme_data.get("author"),
                        created_at=theme_data.get("created_at"),
                        user_created=True,
                    )
                    self._themes[theme_id] = theme

                _LOGGER.debug(f"Loaded {len(themes_data)} user themes")

        except Exception as err:
            _LOGGER.warning(f"Error loading user themes: {err}")

    async def create_theme(self, theme: AutomationTheme) -> bool:
        """
        Create a new user theme.

        Args:
            theme: AutomationTheme object

        Returns:
            True if successful
        """
        try:
            # Validate theme
            if not self._validate_theme(theme):
                raise ValueError("Theme validation failed")

            # Check for duplicates
            if theme.name in self._themes:
                raise ValueError(f"Theme '{theme.name}' already exists")

            # Mark as user-created
            theme.user_created = True

            # Store in memory
            self._themes[theme.name] = theme

            # Persist to disk
            await self._save_user_themes()

            _LOGGER.info(f"Created theme: {theme.name}")
            return True

        except Exception as err:
            _LOGGER.error(f"Error creating theme: {err}", exc_info=True)
            raise

    async def update_theme(self, theme_id: str, theme: AutomationTheme) -> bool:
        """
        Update an existing user theme.

        Args:
            theme_id: Theme identifier
            theme: Updated AutomationTheme object

        Returns:
            True if successful
        """
        try:
            # Check if theme exists
            if theme_id not in self._themes:
                raise ValueError(f"Theme '{theme_id}' not found")

            # Check if it's built-in (cannot edit)
            if self._themes[theme_id].is_builtin:
                raise ValueError("Cannot edit built-in themes")

            # Validate theme
            if not self._validate_theme(theme):
                raise ValueError("Theme validation failed")

            # Update
            theme.user_created = True
            self._themes[theme_id] = theme

            # Persist to disk
            await self._save_user_themes()

            _LOGGER.info(f"Updated theme: {theme_id}")
            return True

        except Exception as err:
            _LOGGER.error(f"Error updating theme: {err}", exc_info=True)
            raise

    async def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a user theme.

        Args:
            theme_id: Theme identifier

        Returns:
            True if successful
        """
        try:
            # Check if theme exists
            if theme_id not in self._themes:
                raise ValueError(f"Theme '{theme_id}' not found")

            # Check if it's built-in (cannot delete)
            if self._themes[theme_id].is_builtin:
                raise ValueError("Cannot delete built-in themes")

            # Delete
            del self._themes[theme_id]

            # Persist to disk
            await self._save_user_themes()

            _LOGGER.info(f"Deleted theme: {theme_id}")
            return True

        except Exception as err:
            _LOGGER.error(f"Error deleting theme: {err}", exc_info=True)
            raise

    async def _save_user_themes(self) -> None:
        """Save user themes to disk."""
        try:
            # Collect user themes
            user_themes = {
                theme_id: theme.to_dict()
                for theme_id, theme in self._themes.items()
                if theme.user_created
            }

            # Write to file
            themes_file = os.path.join(self.theme_storage_dir, "themes.json")
            with open(themes_file, "w") as f:
                json.dump(user_themes, f, indent=2)

            _LOGGER.debug(f"Saved {len(user_themes)} user themes")

        except Exception as err:
            _LOGGER.error(f"Error saving user themes: {err}", exc_info=True)
            raise

    def _validate_theme(self, theme: AutomationTheme) -> bool:
        """
        Validate theme colors and structure.

        Args:
            theme: AutomationTheme to validate

        Returns:
            True if valid
        """
        try:
            # Check required fields
            if not theme.name or not theme.description:
                return False

            # Check colors are valid hex
            colors = [
                theme.trigger_color,
                theme.condition_color,
                theme.action_color,
                theme.metadata_color,
                theme.edge_color,
                theme.highlight_color,
                theme.disabled_color,
                theme.card_background,
                theme.card_border,
                theme.text_color,
                theme.accent_color,
            ]

            for color in colors:
                if not self._is_valid_hex_color(color):
                    return False

            return True

        except Exception:
            return False

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Check if color is valid hex format."""
        if not color.startswith("#"):
            return False

        hex_part = color[1:]
        if len(hex_part) not in (3, 6):
            return False

        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False

    def get_theme(self, theme_id: str) -> Optional[AutomationTheme]:
        """
        Get a theme by ID.

        Args:
            theme_id: Theme identifier

        Returns:
            AutomationTheme or None if not found
        """
        return self._themes.get(theme_id)

    def list_themes(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available themes.

        Returns:
            Dictionary of theme info
        """
        return {
            theme_id: {
                "name": theme.name,
                "description": theme.description,
                "is_builtin": theme.is_builtin,
                "user_created": theme.user_created,
                "trigger_color": theme.trigger_color,
                "condition_color": theme.condition_color,
                "action_color": theme.action_color,
            }
            for theme_id, theme in self._themes.items()
        }

    def apply_theme(self, theme_id: str) -> bool:
        """
        Apply a theme.

        Args:
            theme_id: Theme to apply

        Returns:
            True if successful
        """
        if theme_id not in self._themes:
            _LOGGER.warning(f"Theme '{theme_id}' not found")
            return False

        self._current_theme = theme_id
        self._user_preference = theme_id
        _LOGGER.info(f"Applied theme: {theme_id}")
        return True

    def get_current_theme(self) -> AutomationTheme:
        """Get the currently applied theme."""
        return self._themes.get(self._current_theme, self._themes["default"])


# Example usage in integration:
"""
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    theme_manager = ThemeManager(hass)
    await theme_manager.initialize()
    hass.data[DOMAIN]['theme_manager'] = theme_manager
    
    # Register API endpoints
    async def handle_list_themes(request):
        return web.json_response(theme_manager.list_themes())
    
    async def handle_apply_theme(request):
        data = await request.json()
        success = theme_manager.apply_theme(data.get('theme_id'))
        return web.json_response({'success': success})
    
    hass.http.app.router.add_get('/api/visualautoview/themes', handle_list_themes)
    hass.http.app.router.add_post('/api/visualautoview/themes/apply', handle_apply_theme)
"""
