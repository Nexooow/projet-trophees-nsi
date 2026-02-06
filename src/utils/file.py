class File:
    
    def __init__ (self, content = None):
        if content is None:
            content = []
        self.content = content
        
    def enfiler (self, data):
        self.content.append(data)
        
    def defiler (self):
        return self.content.pop(0)
    
    def sommet (self):
        return self.content[0]
    
    def est_vide (self):
        return self.content == []