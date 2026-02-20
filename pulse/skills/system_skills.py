"""
System-related skills for Pulse.
"""
import datetime
import platform
try:
    import psutil
except ImportError:
    psutil = None

from pulse.core.skill import Skill

class TimeSkill(Skill):
    @property
    def name(self) -> str:
        return "time"
        
    @property
    def description(self) -> str:
        return "Tells the current date and time."
        
    @property
    def commands(self) -> list:
        return [
            "what time is it",
            "what is the time",
            "current time",
            "time now",
            "tell me the time",
            "what time it is",
            "what date is it",
            "what is the date",
            "today date",
            "todays date",
            "what day is it",
            "today",
        ]

    def execute(self, context: dict) -> str:
        now = datetime.datetime.now()
        return f"It is currently {now.strftime('%A, %B %d, %I:%M %p')}."


class SystemInfoSkill(Skill):
    @property
    def name(self) -> str:
        return "system_info"
        
    @property
    def description(self) -> str:
        return "Provides system status information (CPU, RAM)."
        
    @property
    def commands(self) -> list:
        return [
            "system status",
            "system info",
            "system information",
            "how is the system",
            "cpu usage",
            "ram usage",
            "memory usage",
            "performance",
            "device status",
        ]

    def execute(self, context: dict) -> str:
        info = []
        info.append(f"OS: {platform.system()} {platform.release()}")
        
        if psutil:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            info.append(f"CPU Usage: {cpu_percent}%")
            info.append(f"Memory Usage: {mem.percent}% ({round(mem.used/1024**3, 1)}GB / {round(mem.total/1024**3, 1)}GB)")
        else:
            info.append("(Install 'psutil' for detailed hardware stats)")
            
        return " | ".join(info)
