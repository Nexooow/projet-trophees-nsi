class File:
    """
    Classe représentant une file (FIFO) avec système de priorité.
    """
    
    def __init__ (self, content = None):
        if content is None:
            content = []
        self.content = [
            (data, 0) for data in content
        ]
        
    def enfiler (self, data, priority = 0):
        for i, (_, p) in enumerate(self.content):
            if priority > p:
                self.content.insert(i, (data, priority))
                return
        self.content.append((data, priority))
        
    def defiler (self):
        return self.content.pop(0)[0]
    
    def sommet (self):
        return self.content[0][0]
    
    def est_vide (self):
        return self.content == []