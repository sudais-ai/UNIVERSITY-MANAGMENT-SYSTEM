from collections import defaultdict, deque
class RecognitionRegistry:
    def __init__(self, required_consecutive: int = 7):
        self.required = required_consecutive
        self.buffers = defaultdict(lambda: deque(maxlen=16))
    def push_candidate(self, camera_id: str, student_id: int):
        self.buffers[camera_id].append(student_id)
    def get_confirmed(self, camera_id: str):
        buf = list(self.buffers[camera_id])
        if len(buf) < self.required:
            return None
        recent = buf[-self.required:]
        return recent[0] if all(sid == recent[0] for sid in recent) else None
