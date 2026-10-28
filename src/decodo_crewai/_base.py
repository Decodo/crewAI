from __future__ import annotations

import os
from typing import Any

import httpx
from crewai.tools import BaseTool, EnvVar
from crewai.tools.tool_failure import ToolFailure
from decodo import (
    AuthenticationError,
    DecodoClient,
    DecodoConfig,
    DecodoError,
    RateLimitError,
    ScrapeRequest,
    ValidationError,
    WebScrapingApiConfig,
)
from decodo import TimeoutError as DecodoTimeoutError
from pydantic import Field, PrivateAttr

API_KEY_ENV_VAR = "DECODO_API_KEY"
INTEGRATION_HEADER = "crewai-python"


class DecodoBaseTool(BaseTool):
    """Shared Decodo client and error handling for the Decodo tools.

    Get an API key from your Web Scraping API subscription on the Decodo dashboard:
    https://dashboard.decodo.com/web-data/playground
    """

    package_dependencies: list[str] = Field(default_factory=lambda: ["decodo-sdk"])
    env_vars: list[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name=API_KEY_ENV_VAR,
                description="API key for the Decodo Web Scraping API",
                required=True,
            )
        ]
    )

    _client: DecodoClient = PrivateAttr()

    def __init__(self, api_key: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        api_key = (api_key or os.environ.get(API_KEY_ENV_VAR) or "").strip()
        if not api_key:
            raise ValueError(f"Pass api_key or set the {API_KEY_ENV_VAR} environment variable.")
        self._client = DecodoClient(
            DecodoConfig(
                web_scraping_api=WebScrapingApiConfig(api_key=api_key, integration_header=INTEGRATION_HEADER),
            )
        )

    def _scrape(self, params: ScrapeRequest) -> Any:
        """Return the first result's content, or a ToolFailure the agent can act on."""
        try:
            response = self._client.web_scraping_api.scrape(params)
        except AuthenticationError as e:
            return ToolFailure(
                message=f"Decodo rejected the API key ({e}). Check {API_KEY_ENV_VAR}.",
                code="authentication_failed",
            )
        except RateLimitError as e:
            return ToolFailure(message=f"Decodo rate limit reached: {e}", code="rate_limited", retryable=True)
        except ValidationError as e:
            return ToolFailure(message=f"Decodo rejected the request parameters: {e}", code="invalid_params")
        except DecodoTimeoutError as e:
            return ToolFailure(message=f"Decodo request timed out: {e}", code="timeout", retryable=True)
        except DecodoError as e:
            return ToolFailure(
                message=f"Decodo request failed: {e}",
                code=str(e.status_code),
                retryable=e.status_code >= 500,
            )
        except (httpx.LocalProtocolError, UnicodeEncodeError):
            return ToolFailure(
                message=f"The request to Decodo could not be sent. Check {API_KEY_ENV_VAR} for invalid characters.",
                code="invalid_request",
            )
        except httpx.TransportError as e:
            return ToolFailure(message=f"Could not reach Decodo: {e}", code="network_error", retryable=True)

        results = response.get("results") or []
        if not results:
            failed: dict[str, Any] = dict(response)
            if failed.get("message"):
                return ToolFailure(
                    message=f"Decodo could not scrape the target: {failed['message']}",
                    code=str(failed.get("status_code", "scrape_failed")),
                    retryable=True,
                )
            return ToolFailure(message="Decodo returned no results.", code="empty_response")

        result = results[0]
        status_code = result.get("status_code")
        if isinstance(status_code, int) and not 200 <= status_code < 300:
            return ToolFailure(
                message=f"Decodo could not retrieve the page: the target responded with status {status_code}.",
                code=str(status_code),
                retryable=status_code == 429 or status_code >= 500,
            )

        content = result.get("content")
        if content is None or content == "":
            return ToolFailure(message="Decodo returned a result with no content.", code="empty_content")
        return content
