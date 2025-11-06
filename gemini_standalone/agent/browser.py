"""Handle Playwright browser lifecycle and page interactions."""
import time
import asyncio
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

from .auto_tool import function_tool
from .utils import denormalize_x, denormalize_y, time_logger
from .logger import get_logger

logger = get_logger(__name__)

class BrowserManager:
    """Manages all interactions with playwright browser"""

    def __init__(self,
                 page_width: int = 1440,
                 page_height: int = 900,
                 headless: bool = True):
        
        self.width = page_width
        self.height = page_height
        self.headless_mode = headless

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.actions_map = {
            "open_web_browser": self.open_web_browser,
            "wait_5_seconds": self.wait_5_seconds,
            "go_back": self.go_back,
            "go_forward": self.go_forward,
            "search": self.search,
            "navigate": self.navigate,
            "click_at": self.click_at,
            "hover_at": self.hover_at,
            "type_text_at": self.type_text_at,
            "key_combination": self.key_combination,
            "scroll_document": self.scroll_document,
            "scroll_at": self.scroll_at,
            "drag_and_drop": self.drag_and_drop
        }
    
    def start(self):
        """Start playwright and create a browser page"""
        logger.info(
            "Starting Playwright browser in "
            f"{'headless' if self.headless_mode else 'browser'} mode..."
        )
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless_mode)
        self.context = self.browser.new_context(
            viewport={"width": self.width, "height": self.height}
        )
        self.page = self.context.new_page()
        logger.info("BrowserManager initialized successfully.")
        return self
    
    def close(self):
        """Close browser and stop playwright"""
        logger.info("Closing browser and cleaning up resources...")
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during browser close: {e}")
            raise
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            logger.info("Browser closed successfully.")
    
    def goto(self, url: str):
        """Navigates to the url"""
        self.page.goto(url=url)
    
    def capture_screen(self, path: str | None = None) -> bytes:
        """Capture the screenshot of page"""
        if path:
            return self.page.screenshot(path=path, type="png")
        return self.page.screenshot(type="png")
    
    def get_current_url(self) -> str:
        """Get the current url of page"""
        return self.page.url
    
    @function_tool
    def open_web_browser(self, **kwargs):
        """Opens the web browser"""
        # We are already doing this by default
        # Reduces additional request to llm
        pass
    
    @function_tool
    def wait_5_seconds(self, **kwargs):
        """Waits for 5 seconds to load dynamic content"""
        time.sleep(5)

    @function_tool
    def go_back(self, **kwargs):
        """Go to the previous page in history"""
        self.page.go_back()
    
    @function_tool
    def go_forward(self, **kwargs):
        """Go to the next page in history"""
        self.page.go_forward()
    
    @function_tool
    def search(self, **kwargs):
        """Go to search engine to search and start the actions"""
        # We'll default to google search for now
        # NOTE: sometimes for security reasons, google might ask to solve captcha
        # Other alternatives include duckduck go, brave search
        self.page.goto("https://www.google.com/")
    
    @function_tool
    def navigate(self, url: str, **kwargs):
        """Go to the specified url"""
        self.page.goto(url=url)
    
    @function_tool
    def click_at(self, x: int, y: int, **kwargs):
        """Click at a specific coordinates on the webpage"""
        self.page.mouse.click(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )

    @function_tool
    def hover_at(self, x: int, y: int, **kwargs):
        """Hover the mouse at a specific coordinate on the webpage"""
        self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )

    @function_tool
    def type_text_at(self,
                     text: str,
                     x: int,
                     y: int,
                     press_enter: Optional[bool] = True,
                     clear_before_typing: Optional[bool] = True,
                     **kwargs):
        """Type text at a specific coordinate"""
        px, py = denormalize_x(x, width=self.width), denormalize_y(y, height=self.height)
        self.page.mouse.click(px, py)
        if clear_before_typing:
            self.page.keyboard.press("Control+A") # Win/Linux: Control
            self.page.keyboard.press("Backspace")
        self.page.keyboard.type(text)
        if press_enter:
            self.page.keyboard.press("Enter")

    @function_tool
    def key_combination(self, keys: str, **kwargs):
        """
        Press keyboard keys or combinations, such as Control+C or Enter
        """
        self.page.keyboard.press(keys)

    @function_tool
    def scroll_document(self, direction: str = "down", **kwargs):
        """Scrolls the entire webpage up, down, left, or right."""
        direction = direction.lower()
        if direction == "down":
            self.page.keyboard.press("PageDown")
        elif direction == "up":
            self.page.keyboard.press("PageUp")
        elif direction == "left":
            # We'll keep 400 for now, inc/dec later if needed
            self.page.evaluate("window.scrollBy(-400, 0)")
        elif direction == "right":
            self.page.evaluate("window.scrollBy(400, 0)")

    @function_tool
    def scroll_at(self,
                  x: int,
                  y: int,
                  direction: str = "down",
                  magnitude: Optional[int] = 800,
                  **kwargs):
        """
        Scrolls a specific element or area at coordinate (x, y)
        in the specified direction by a certain magnitude.
        """
        self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )
        dy = magnitude if direction.lower() == "down" else -magnitude
        self.page.mouse.wheel(0, dy)

    @function_tool
    def drag_and_drop(self,
                      x: int,
                      y: int,
                      destination_x: int,
                      destination_y: int,
                      **kwargs):
        """
        Drags an element from a starting coordinate (x, y) and drops it at
        a destination coordinate (destination_x, destination_y).
        All coordinates are based on a 1000x1000 grid.

        Args:
            x: int (0-999)
            y: int (0-999)
            destination_x: int (0-999)
            destination_y: int (0-999)
        """
        self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )
        self.page.wait_for_load_state(state="networkidle")
        self.page.mouse.down()
        self.page.mouse.move(
            denormalize_x(destination_x),
            denormalize_y(destination_y)
        )
        self.page.wait_for_load_state(state="networkidle")
        self.page.mouse.up()

    def _wait_after_action(self, wait_time_s: int = 5):
        """Wait for page stability after each action"""
        try:
            self.page.wait_for_load_state(state="networkidle",
                                          timeout=wait_time_s * 1000)
        except Exception:
            pass
        # Wait for additional 500ms to settle things
        time.sleep(0.5)

    @time_logger
    def execute_action(self,
                       action_name: str,
                       action_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual action"""
        try:
            execution_method = self.actions_map.get(action_name)
            if not execution_method:
                logger.warning(f"Action not implemented: {action_name}")
                return {
                    "warning": f"Action `{action_name}` was not implemented"
                }
            
            logger.info(f"[ACTION] {action_name}: {action_args}")
            
            execution_method(**action_args)
            
            self._wait_after_action()
            return {}
        except Exception as e:
            logger.error(f"Error executing action: '{action_name}': {e}", exc_info=True)
            return {"error": str(e)}

class AsyncBrowserManager:
    """Manages all interactions with playwright browser asynchronously"""

    def __init__(self,
                 page_width: int = 1440,
                 page_height: int = 900,
                 headless: bool = True):
        
        self.width = page_width
        self.height = page_height
        self.headless_mode = headless

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        self.actions_map = {
            "open_web_browser": self.open_web_browser,
            "wait_5_seconds": self.wait_5_seconds,
            "go_back": self.go_back,
            "go_forward": self.go_forward,
            "search": self.search,
            "navigate": self.navigate,
            "click_at": self.click_at,
            "hover_at": self.hover_at,
            "type_text_at": self.type_text_at,
            "key_combination": self.key_combination,
            "scroll_document": self.scroll_document,
            "scroll_at": self.scroll_at,
            "drag_and_drop": self.drag_and_drop
        }
    
    async def start(self):
        """Start playwright and create a browser page"""
        logger.info(
            "Starting Playwright browser in "
            f"{'headless' if self.headless_mode else 'browser'} mode..."
        )
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless_mode)
        self.context = await self.browser.new_context(
            viewport={"width": self.width, "height": self.height}
        )
        self.page = await self.context.new_page()
        logger.info("BrowserManager initialized successfully.")
        return self
    
    async def close(self):
        """Close browser and stop playwright"""
        logger.info("Closing browser and cleaning up resources...")
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during browser close: {e}")
            raise
        finally:
            self.browser = None
            self.context = None
            self.page = None
            self.playwright = None
            logger.info("Browser closed successfully.")
    
    async def goto(self, url: str):
        """Navigates to the url"""
        await self.page.goto(url=url)
    
    async def capture_screen(self, path: str | None = None) -> bytes:
        """Capture the screenshot of page"""
        if path:
            return await self.page.screenshot(path=path, type="png")
        return await self.page.screenshot(type="png")
    
    async def get_current_url(self) -> str:
        """Get the current url of page"""
        return self.page.url
    
    @function_tool
    async def open_web_browser(self, **kwargs):
        """Opens the web browser"""
        # We are already doing this by default
        # Reduces additional request to llm
        pass

    @function_tool
    async def wait_5_seconds(self, **kwargs):
        """
        Pauses execution for 5 seconds to allow dynamic
        content to load or animations to complete.
        """
        await asyncio.sleep(5)

    @function_tool
    async def go_back(self, **kwargs):
        """Navigates to the previous page in the browser's history."""
        await self.page.go_back()
    
    @function_tool
    async def go_forward(self, **kwargs):
        """Navigates to the next page in the browser's history."""
        await self.page.go_forward()
    
    @function_tool
    async def search(self, **kwargs):
        """
        Navigates to the default search engine's homepage (e.g., Google).
        Useful for starting a new search task.
        """
        # We'll default to google search for now
        # NOTE: sometimes for security reasons, google might ask to solve captcha
        # Other alternatives include duckduck go, brave search
        await self.page.goto("https://www.google.com/")
    
    @function_tool
    async def navigate(self, url: str, **kwargs):
        """Navigates the browser directly to the specified URL."""
        await self.page.goto(url=url)
    
    @function_tool
    async def click_at(self, x: int, y: int, **kwargs):
        """
        Clicks at a specific coordinate on the webpage.
        The x and y values are based on a 1000x1000 grid and are scaled to the screen dimensions.
        
        Args:
            x: int (0-1000)
            y: int (0-1000)
        """
        await self.highlight_mouse(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height))
        await self.page.mouse.click(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )

    @function_tool
    async def hover_at(self, x: int, y: int, **kwargs):
        """
        Hovers the mouse at a specific coordinate on the webpage.
        Useful for revealing sub-menus. The x and y values are based on a 1000x1000 grid.

        Args:
            x: int (0-1000)
            y: int (0-1000)
        """
        await self.highlight_mouse(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height))
        await self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )

    @function_tool
    async def type_text_at(self,
                           text: str,
                           x: int,
                           y: int,
                           press_enter: Optional[bool] = True,
                           clear_before_typing: Optional[bool] = True,
                           **kwargs):
        """
        Types text at a specific coordinate, defaults to clearing the field first and
        pressing ENTER after typing, but these can be disabled.
        Use this to type text in input fields.
        Args:
            x: int (0-1000)
            y: int (0-1000)
            text: str
            press_enter: bool (Optional, default True)
            clear_before_typing: bool (Optional, default True)
        """
        px, py = denormalize_x(x, width=self.width), denormalize_y(y, height=self.height)
        await self.highlight_mouse(px, py)
        await self.page.mouse.click(px, py)
        if clear_before_typing:
            await self.page.keyboard.press("Control+A") # Win/Linux: Control
            await self.page.keyboard.press("Backspace")
        await self.page.keyboard.type(text)
        if press_enter:
            await self.page.keyboard.press("Enter")

    @function_tool
    async def key_combination(self, keys: str, **kwargs):
        """
        Press keyboard keys or combinations, such as "Control+C" or "Enter".
        Useful for triggering actions (like submitting a form with "Enter") or clipboard operations.
        Use this to execute specific keyboard actions.
        Args:
            keys: str (e.g. 'Enter', 'Control+A').
        """
        await self.page.keyboard.press(keys)

    @function_tool
    async def scroll_document(self, direction: str = "down", **kwargs):
        """
        Scrolls the entire webpage "up", "down", "left", or "right".
        
        Args:
            direction: str ("up", "down", "left", or "right")
        """
        direction = direction.lower()
        if direction == "down":
            await self.page.keyboard.press("PageDown")
        elif direction == "up":
            await self.page.keyboard.press("PageUp")
        elif direction == "left":
            # We'll keep 400 for now, inc/dec later if needed
            await self.page.evaluate("window.scrollBy(-400, 0)")
        elif direction == "right":
            await self.page.evaluate("window.scrollBy(400, 0)")

    @function_tool
    async def scroll_at(self,
                        x: int,
                        y: int,
                        direction: str = "down",
                        magnitude: Optional[int] = 800,
                        **kwargs):
        """
        Scrolls a specific element or area at coordinate (x, y) in
        the specified direction by a certain magnitude. Coordinates
        and magnitude (default 800) are based on a 1000x1000 grid.

        Args:
            x: int (0-1000)
            y: int (0-1000)
            direction: str ("up", "down", "left", "right")
            magnitude: int (0-999, Optional, default 800)
        """
        await self.highlight_mouse(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height))
        await self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )
        dy = magnitude if direction.lower() == "down" else -magnitude
        await self.page.mouse.wheel(0, dy)

    @function_tool
    async def drag_and_drop(self, 
                            x: int,
                            y: int,
                            destination_x: int,
                            destination_y: int,
                            **kwargs):
        """
        Drags an element from a starting coordinate (x, y) and drops it at
        a destination coordinate (destination_x, destination_y).
        All coordinates are based on a 1000x1000 grid.

        Args:
            x: int (0-1000)
            y: int (0-1000)
            destination_x: int (0-1000)
            destination_y: int (0-1000)
        """
        await self.page.mouse.move(
            denormalize_x(x, width=self.width),
            denormalize_y(y, height=self.height)
        )
        await self.page.wait_for_load_state(state="networkidle")
        await self.page.mouse.down()
        await self.page.mouse.move(
            denormalize_x(destination_x),
            denormalize_y(destination_y)
        )
        await self.page.wait_for_load_state(state="networkidle")
        await self.page.mouse.up()

    async def _wait_after_action(self, wait_time_s: int = 5):
        """Wait for page stability after each action"""
        try:
            await self.page.wait_for_load_state(state="networkidle",
                                                timeout=wait_time_s * 1000)
        except Exception:
            pass
        # Wait for additional 500ms to settle things
        await asyncio.sleep(1)
    
    async def highlight_mouse(self, x: int, y: int):
        await self.page.evaluate(
            f"""
        () => {{
            const element_id = "playwright-feedback-circle";
            const div = document.createElement('div');
            div.id = element_id;
            div.style.pointerEvents = 'none';
            div.style.border = '4px solid red';
            div.style.borderRadius = '50%';
            div.style.width = '20px';
            div.style.height = '20px';
            div.style.position = 'fixed';
            div.style.zIndex = '9999';
            document.body.appendChild(div);

            div.hidden = false;
            div.style.left = {x} - 10 + 'px';
            div.style.top = {y} - 10 + 'px';

            setTimeout(() => {{
                div.hidden = true;
            }}, 2000);
        }}
    """
        )
        # Wait a bit for the user to see the cursor.
        await asyncio.sleep(1)

    @time_logger
    async def execute_action(self,
                             action_name: str,
                             action_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual action"""
        try:
            execution_method = self.actions_map.get(action_name)
            if not execution_method:
                logger.warning(f"Action not implemented: {action_name}")
                return {
                    "warning": f"Action `{action_name}` was not implemented"
                }
            
            logger.info(f"[ACTION] {action_name}: {action_args}")
            
            await execution_method(**action_args)
            
            await self._wait_after_action()
            return {}
        except Exception as e:
            logger.error(f"Error executing action: '{action_name}': {e}", exc_info=True)
            return {"error": str(e)}
