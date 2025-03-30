from collections import deque

class Song:
    def __init__(self, url, title=None, duration=None, audio_url=None):
        self.url = url
        self.title = title or "Unknown Title"
        self.duration = duration
        self.audio_url = audio_url

    def __str__(self):
        if self.duration:
            return f"{self.title} ({self.duration}s)"
        return self.title

    def format_duration(self):

        if not self.duration:
            return "Duração desconhecida"
        
        minutes, seconds = divmod(self.duration, 60)
        return f"{minutes}:{seconds:02d}"


class MusicQueue:
    def __init__(self):
        """Inicializa uma fila vazia"""
        self.queue = deque()
        self.current = None
        self.processing = False
        self.volume = 1.0 

    def add(self, song):

        self.queue.append(song)
    
    def get_next(self):

        if not self.queue:
            self.current = None
            return None
        
        self.current = self.queue.popleft()
        return self.current
    
    def clear(self):

        self.queue.clear()
        self.current = None
    
    def size(self):
        return len(self.queue)
    
    def is_empty(self):

        return len(self.queue) == 0



class QueueManager:
    def __init__(self):
        self.queues = {}
    
    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    def remove_queue(self, guild_id):
        if guild_id in self.queues:
            del self.queues[guild_id]