class Airline(object):
    name = ""
    partners = []
    def __init__(self, data):
        assert (data != None and len(data) > 0), 'Failed precondition'
        self.name = data[0]
        self.partners=data[1:]   
    def getPartners(self):
        return self.partners
    def isPartner(self, name):
        return (name in self.partners)
    def getName(self):
        return self.name
    def toString(self):
        return str(self.name)+", partners: "+str(self.partners)
