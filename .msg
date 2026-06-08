## What's Changed
- **Simpler GUID handling**: Switched to `uuid` module for better performance and reliability.
- **Enhanced Battery Info**: Added detection for charging and full charge status in the results subtitle.
- **New Shortcut**: Added 'Open Power Settings' (4th item) to quickly access system settings (`ms-settings:powersleep`).
- **Instant UI Reactivity**: Implemented `WM_SETTINGCHANGE` broadcast to ensure system-wide UI updates (like the taskbar battery icon) immediately after switching plans.
- **Cleanup**: Removed unused dependencies and updated internal documentation.
