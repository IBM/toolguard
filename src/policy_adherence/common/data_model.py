from collections import deque
from typing import Optional


def find_ref(doc: dict, ref: str):
    q = deque(ref.split('/'))
    cur = doc
    while q:
        field = q.popleft()
        if field == '#':
            cur = doc
            continue
        if field in cur:
            cur = cur[field]
        else:
            return None
    if '$ref' in cur:
        return find_ref(doc, cur.get('$ref'))  # recursive. infinte loops?
    return cur


class DataModel:
    def __init__(self, data: dict, parent: Optional['DataModel'] = None):
        self.data = data
        self.parent = parent

    def __eq__(self, other: 'DataModel'):
        return isinstance(other, DataModel) and self.data == other.data
    
    #used for debugging purposes
    def __repr__(self):
        return f"DM: {str(self.data)}"

    @property
    def owner(self):
        if self.parent is None:
            return self
        return self.parent.owner

    def find_ref(self, ref: str):
        return find_ref(self.owner.data, ref)
    

class ElementWithDescription(DataModel):

    @property
    def description(self) -> str | None:
        return self.data.get("description")


    def set_description(self, value: str | None):
        if value is None:
            if "description" in self.data:
                del self.data["description"]  # should never be null
        else:
            self.data["description"] = value

class ElementWithSummary(DataModel):

    @property
    def summary(self) -> str:
        return self.data.get("summary")

    def set_summary(self, value: str):
        if value is None:
            if "summary" in self.data:
                del self.data["summary"] # should never be null
        else:
            self.data["summary"] = value
