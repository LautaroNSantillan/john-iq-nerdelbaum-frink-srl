class Company:
    def __init__(self,name, img, location, id=None):
        self.id = id
        self.name = name
        self.img = img
        self.location = location