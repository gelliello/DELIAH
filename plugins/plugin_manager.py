from abc import ABC, abstractmethod
from typing import Any, Optional
import importlib
import json
from pathlib import Path


class Plugin(ABC):
    def __init__(self, name: str, version: str = "0.1.0"):
        self.name = name
        self.version = version
        self.enabled = False

    @abstractmethod
    async def activate(self):
        pass

    @abstractmethod
    async def deactivate(self):
        pass

    @abstractmethod
    async def handle_command(self, command: str, args: dict) -> Any:
        pass

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
        }


class PluginManager:
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins: dict[str, Plugin] = {}
        self.plugins_dir = plugins_dir or Path(__file__).parent

    async def load_plugin(self, plugin: Plugin):
        self.plugins[plugin.name] = plugin
        await plugin.activate()
        plugin.enabled = True

    async def unload_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin:
            await plugin.deactivate()
            plugin.enabled = False
            del self.plugins[name]

    async def execute_command(
        self, plugin_name: str, command: str, args: Optional[dict] = None
    ) -> Any:
        plugin = self.plugins.get(plugin_name)
        if not plugin or not plugin.enabled:
            return {"error": f"Plugin {plugin_name} not found or disabled"}
        return await plugin.handle_command(command, args or {})

    def list_plugins(self) -> list[dict]:
        return [p.get_info() for p in self.plugins.values()]

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self.plugins.get(name)


class ExamplePlugin(Plugin):
    def __init__(self):
        super().__init__("example", "0.1.0")

    async def activate(self):
        print(f"Plugin {self.name} activated")

    async def deactivate(self):
        print(f"Plugin {self.name} deactivated")

    async def handle_command(self, command: str, args: dict) -> Any:
        if command == "hello":
            return {"message": f"Hello from {self.name}!"}
        return {"error": f"Unknown command: {command}"}
