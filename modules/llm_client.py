"""
Small OpenAI-compatible LLM client for optional SafeBARS responses.
"""

from dataclasses import dataclass, asdict
import os
from typing import List, Dict, Optional, Any

import requests
from requests import RequestException


@dataclass
class LLMProvider:
    id: str
    label: str
    api_key: str
    base_url: str
    model: str

    def public_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop("api_key", None)
        data["key_hint"] = self._mask_key()
        return data

    def _mask_key(self) -> str:
        if not self.api_key:
            return "not configured"
        if len(self.api_key) <= 8:
            return "***"
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"


class LLMClient:
    def __init__(self):
        self.providers = self._load_providers()
        self.active_provider_id = self._choose_active_provider()

    def is_configured(self) -> bool:
        return bool(self.providers)

    def configured_provider_summaries(self) -> List[Dict[str, Any]]:
        return [provider.public_dict() for provider in self.providers.values()]

    def _load_providers(self) -> Dict[str, LLMProvider]:
        providers: Dict[str, LLMProvider] = {}

        if os.getenv("ZHI_KEY"):
            providers["zhipu"] = LLMProvider(
                id="zhipu",
                label="Zhipu",
                api_key=os.getenv("ZHI_KEY", ""),
                base_url="https://open.bigmodel.cn/api/paas/v4",
                model=os.getenv("ZHI_MODEL", os.getenv("SAFEBARS_LLM_MODEL", "glm-4")),
            )

        bailian_key = (
            os.getenv("BAILIAN_API_KEY", "")
            or os.getenv("DASHSCOPE_API_KEY", "")
            or os.getenv("ALIYUN_API_KEY", "")
        )
        if bailian_key:
            providers["aliyun_bailian"] = LLMProvider(
                id="aliyun_bailian",
                label=os.getenv("BAILIAN_LABEL", "Aliyun Bailian"),
                api_key=bailian_key,
                base_url=os.getenv(
                    "BAILIAN_BASE_URL",
                    "https://dashscope.aliyuncs.com/compatible-mode/v1",
                ).rstrip("/"),
                model=os.getenv("BAILIAN_MODEL", os.getenv("SAFEBARS_LLM_MODEL", "qwen-plus")),
            )

        tencent_key = (
            os.getenv("TENCENT_API_KEY", "")
            or os.getenv("TENCENT_HUNYUAN_API_KEY", "")
            or os.getenv("HUNYUAN_API_KEY", "")
        )
        if tencent_key:
            providers["tencent_hunyuan"] = LLMProvider(
                id="tencent_hunyuan",
                label=os.getenv("TENCENT_LABEL", "Tencent Hunyuan"),
                api_key=tencent_key,
                base_url=os.getenv(
                    "TENCENT_BASE_URL",
                    "https://tokenhub.tencentmaas.com/v1",
                ).rstrip("/"),
                model=os.getenv("TENCENT_MODEL", os.getenv("SAFEBARS_LLM_MODEL", "hy3-preview")),
            )

        if os.getenv("XFYUN_MAAS_API_KEY"):
            providers["xfyun_maas"] = LLMProvider(
                id="xfyun_maas",
                label=os.getenv("XFYUN_MAAS_LABEL", "Xunfei MaaS DeepSeek V4 Flash"),
                api_key=os.getenv("XFYUN_MAAS_API_KEY", ""),
                base_url=os.getenv(
                    "XFYUN_MAAS_BASE_URL",
                    "https://maas-api.cn-huabei-1.xf-yun.com/v2",
                ).rstrip("/"),
                model=os.getenv("XFYUN_MAAS_MODEL", "xopdeepseekv4flash"),
            )

        if os.getenv("OPENAI_API_KEY") and os.getenv("ENABLE_OPENAI_PROVIDER") == "1":
            providers["openai_compatible"] = LLMProvider(
                id="openai_compatible",
                label=os.getenv("OPENAI_LABEL", "OpenAI"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url=os.getenv(
                    "OPENAI_BASE_URL",
                    "https://api.openai.com/v1",
                ).rstrip("/"),
                model=os.getenv("OPENAI_MODEL", os.getenv("SAFEBARS_LLM_MODEL", "gpt-4o-mini")),
            )

        for suffix in ["A", "B"]:
            api_key = os.getenv(f"LLM_{suffix}_API_KEY", "")
            base_url = os.getenv(f"LLM_{suffix}_BASE_URL", "")
            if api_key and base_url:
                provider_id = f"profile_{suffix.lower()}"
                providers[provider_id] = LLMProvider(
                    id=provider_id,
                    label=os.getenv(f"LLM_{suffix}_LABEL", f"Profile {suffix}"),
                    api_key=api_key,
                    base_url=base_url.rstrip("/"),
                    model=os.getenv(f"LLM_{suffix}_MODEL", os.getenv("SAFEBARS_LLM_MODEL", "glm-4")),
                )

        return providers

    def _choose_active_provider(self) -> Optional[str]:
        preferred = os.getenv("SAFEBARS_LLM_PROVIDER", "")
        if preferred in self.providers:
            return preferred
        for provider_id in [
            "zhipu",
            "aliyun_bailian",
            "tencent_hunyuan",
            "xfyun_maas",
            "openai_compatible",
            "profile_a",
            "profile_b",
        ]:
            if provider_id in self.providers:
                return provider_id
        return next(iter(self.providers), None)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.4) -> Optional[str]:
        if not self.active_provider_id:
            return None
        return self.chat_with_provider(self.active_provider_id, messages, temperature=temperature)

    def chat_with_provider(
        self,
        provider_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
    ) -> Optional[str]:
        result = self.chat_with_provider_detailed(provider_id, messages, temperature=temperature)
        if result.get("ok"):
            return result.get("text")
        return None

    def chat_with_provider_detailed(
        self,
        provider_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        timeout: int = 35,
    ) -> Dict[str, Any]:
        provider = self.providers.get(provider_id)
        if not provider:
            return {
                "ok": False,
                "text": "",
                "error": f"Provider '{provider_id}' is not configured.",
                "status_code": None,
                "error_type": "not_configured",
            }

        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": provider.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 700,
        }
        try:
            response = requests.post(
                f"{provider.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            if response.status_code != 200:
                return {
                    "ok": False,
                    "text": "",
                    "error": self._short_error_body(response.text),
                    "status_code": response.status_code,
                    "error_type": "http_error",
                }
            text = response.json()["choices"][0]["message"]["content"]
            return {
                "ok": True,
                "text": text,
                "error": "",
                "status_code": response.status_code,
                "error_type": "",
            }
        except requests.Timeout:
            return {
                "ok": False,
                "text": "",
                "error": f"Request timed out while contacting {provider.base_url}.",
                "status_code": None,
                "error_type": "timeout",
            }
        except RequestException as exc:
            return {
                "ok": False,
                "text": "",
                "error": str(exc)[:500],
                "status_code": None,
                "error_type": "connection_error",
            }
        except Exception as exc:
            return {
                "ok": False,
                "text": "",
                "error": str(exc)[:500],
                "status_code": None,
                "error_type": "parse_or_unknown_error",
            }

    def _short_error_body(self, text: str) -> str:
        if not text:
            return "Provider returned an error without a response body."
        return text.replace("\n", " ")[:500]
