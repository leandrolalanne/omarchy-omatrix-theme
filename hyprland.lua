-- omatrix: translucency without glass.
--
-- No blur, and that is a measurement rather than a preference. On this kind of
-- machine the live rain background already runs the integrated GPU at ~94% of
-- its maximum clock, against 47% for a static wallpaper. Blur on top saturates
-- it at 99% even at a single pass, because a blur over an animated backdrop
-- cannot be cached the way one over a still wallpaper can -- which is also why
-- `xray` buys nothing here: there is no cached wallpaper to sample.
--
-- Hyprland enables blur by default, so it has to be turned off explicitly.
--
-- Note what is NOT set: active_opacity / inactive_opacity. Window opacity fades
-- the text along with the background and throws away the contrast the palette
-- is defending. Translucency belongs to the terminal itself
-- (ghostty-extra.conf) and to the shell surfaces (shell.bar.toml), where only
-- the background goes through and glyphs stay opaque.

local active_border_color = { colors = { "rgba(89f76eee)", "rgba(61c249ee)" }, angle = 45 }
local inactive_border_color = "rgba(3d992666)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    -- Square. The film's terminals have square corners, and by the time the
    -- chat app, the bubbles, the rows and the avatars are all square, 3 px on
    -- the window frame is the one rounded thing left on screen and reads as a
    -- mistake. No rounding_power either: there is no curve left to shape.
    rounding = 0,

    blur = {
      enabled = false,
    },

    shadow = {
      enabled = true,
      range = 6,
      render_power = 3,
      color = "rgba(00000059)",
      color_inactive = "rgba(00000033)",
    },
  },
})

-- WhatsApp Web is a Chromium webapp, so it has no background-opacity of its own
-- the way a terminal does: the only way to make it translucent is the window
-- itself. That fades the text along with the background, which is the trade --
-- and the reason terminals and the bar do NOT get this treatment.
--
-- The class is the one Hyprland actually reports for the webapp window, read
-- from `hyprctl clients`, not guessed from the URL.
o.window("^chrome-web\\.whatsapp\\.com__-Default$", {
  opacity = "0.90 override 0.90 override 0.90 override",
})

-- Shell surfaces, explicitly unblurred: another theme may have left global blur
-- on, and its hook runs after this file is loaded.
hl.layer_rule({
  name = "omatrix-shell-surfaces",
  match = { namespace = "^(omarchy-bar|omarchy-menu|omarchy-notifications|omarchy-osd|omarchy-reminders|omarchy-polkit|omarchy-network-qr|omarchy-image-selector|omarchy-emojis|omarchy-clipboard|omarchy-keyboard-panel|omarchy-lock-preview)$" },
  blur = false,
})

-- The rain's own surface: never blurred, never dimmed. It is the texture.
hl.layer_rule({
  name = "omatrix-background",
  match = { namespace = "^omatrix-background$" },
  blur = false,
})
