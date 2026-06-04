"""
Selenium-based captcha handler for VK ID Captcha.
"""

import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


_INTERCEPT_SCRIPT = """
// Intercept fetch
const _originalFetch = window.fetch;
window.fetch = async function(...args) {
    const response = await _originalFetch(...args);
    const clone = response.clone();
    clone.json().then(data => {
        if (data && data.response && data.response.success_token) {
            window.__vkSuccessToken = data.response.success_token;
        }
    }).catch(() => {});
    return response;
};

// Intercept XMLHttpRequest
const _originalOpen = XMLHttpRequest.prototype.open;
const _originalSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    this.__url = url;
    return _originalOpen.call(this, method, url, ...rest);
};
XMLHttpRequest.prototype.send = function(...args) {
    this.addEventListener('load', function() {
        try {
            const data = JSON.parse(this.responseText);
            if (data && data.response && data.response.success_token) {
                window.__vkSuccessToken = data.response.success_token;
            }
        } catch(e) {}
    });
    return _originalSend.apply(this, args);
};
"""


def handle_captcha_selenium(redirect_uri: str) -> Optional[str]:
    """
    Opens VK captcha page in a browser, waits for the user to solve it,
    and returns the success_token from the captchaNotRobot.check response.

    Args:
        redirect_uri (str): The redirect_uri from the VK captcha error response.

    Returns:
        Optional[str]: The success_token, or None if not received.
    """
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    # Inject before page loads so fetch/XHR are intercepted from the start
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": _INTERCEPT_SCRIPT
    })

    driver.get(redirect_uri)

    print("Waiting for captcha to be solved...")
    success_token: Optional[str] = None
    while not success_token:
        success_token = driver.execute_script("return window.__vkSuccessToken || null")
        time.sleep(0.5)

    driver.quit()
    return success_token
