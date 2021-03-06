PLATFORM_TOOLS_DIR = "platform-tools"


class GUIActionType:
    CLICK = "click"
    LONG_CLICK = "long-click"
    CHECK = "check"
    UNCHECK = "uncheck"
    SWIPE_UP = "swipe-up"
    SWIPE_DOWN = "swipe-down"
    SWIPE_RIGHT = "swipe-right"
    SWIPE_LEFT = "swipe-left"
    TEXT_ENTRY = "text-entry"
    HOME_NAV = "home"
    BACK_NAV = "back"
    ENTER_KEY = "enter"
    LAUNCH = "launch"


class SystemActionType:
    LAUNCH = "launch"
    RUN_IN_BACKGROUND = "run-in-background"


class TargetType:
    APP = "App"
    NAV = "Nav"
    SPINNER = "Spinner"
    EDIT_TEXT = "EditText"
    TEXT_VIEW = "TextView"
    BUTTON = "Button"
    RADIO_BUTTON = "RadioButton"
    CHECK_BOX = "CheckBox"
    IMAGE_BUTTON = "ImageButton"


class SelectorType:
    ID = "id"
    XPATH = "xpath"
    SYSTEM = "system"


class KeyCode:
    HOME = 3
    BACK = 4
    RETURN = 66


class TargetState:
    ENABLED = "enabled"
    DISABLED = "disabled"
