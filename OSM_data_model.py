#!/bin/python

class MapLayer():
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.edges = {}

    def asXML(self):
        xml = '''<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.6' upload='false' generator='Python script'>'''
        for n in self.nodes:
            xml += self.nodes[n].asXML()
        for w in self.ways:
            xml += self.ways[w].asXML()
        for r in self.relations:
            xml += self.relations[r].asXML()

        xml += '''</osm>'''
        return xml

class OSM_Primitive():
    counter = -10000

    def __init__(self, ml, primitive, attributes = None, tags=None):
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if tags:
            self.tags = tags
        else:
            self.tags = {}
        self.primitive = primitive
        print('attr: ', attributes, self.attributes)
        if not(self.attributes) or not('id' in self.attributes):
            print(OSM_Primitive.counter)
            self.attributes['action'] = 'modify'
            self.attributes['visible'] = 'true'
            self.attributes['id'] = str(OSM_Primitive.counter)
            OSM_Primitive.counter -= 1
    
    def addTags(self, tags):
        if tags:
            for key in tags:
                self.addTag(key, tags[key])

    def addTag(self, key, value):
        self.tags[key] = value

    def asXML(self, body=''):
        self.xml = '<{} '.format(self.primitive)
        for attr in ['id', 'lat', 'lon', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']:
            if attr in self.attributes:
                self.xml += "{}='{}' ".format(attr, self.attributes[attr])
        self.xml += '>'
        if body: self.xml += body
        for key in self.tags:
            self.xml += "\n  <tag k='{key}' v='{tag}' />".format(key=key, tag=self.tags[key])
        self.xml += '\n</{}>'.format(self.primitive)
        return self.xml
    def getParents(self, ml):
       parents = []
       for way in ml.ways:
           if self['id'] in way.getNodes():
               parents.append(way)
       for relation in ml.relations:
           if self['id'] in relation.getMembers():
               parents.append(relation)
       return parents
#    def __repr__(self):
#        return self.asXML()        
class Node(OSM_Primitive):
    def __init__(self, ml, attributes = None, tags = None):
        if not(attributes):
            attributes={'lon': '0.0', 'lat': '0.0'}

        super().__init__(ml, primitive='node', attributes = attributes, tags=tags)
        ml.nodes[self.attributes['id']] = self

class Way(OSM_Primitive):
    def __init__(self, ml, attributes = None, nodes = None, tags = None):
        '''Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details'''
        super().__init__(ml, primitive='way', attributes = attributes, tags=tags)
        self.nodes = []
        self.addNodes(nodes)
        ml.ways[self.attributes['id']] = self

    def addNodes(self,nodes):
        if nodes:        
            for n in nodes:
                self.addNode(n)

    def addNode(self,node):
        try:
            ''' did we receive an object instance to work with? '''
            n = node.attributes['id']
        except KeyError:
            ''' we received a string '''
            n = node
        self.nodes.append(str(n))

    def asXML(self):
        body = ''
        for node in self.nodes:
            body += "\n  <nd ref='{node_id}' />".format(node_id=node)
        return super().asXML(body=body)

class RelationMember():
    def __init__(self, role='', primtype='', member = None):
        self.primtype = primtype
        self.role = role
        try:
            m = member.strip()
        except:
            try:
                ''' did we receive an object instance to work with? '''
                m = member.attributes['id']
                self.primtype = member.primitive
            except (KeyError, NameError) as e:
                ''' the member id was passed as a string or an integer '''
                m = member
        self.memberid = str(m)

    def asXML(self):
        return "\n  <member type='{primtype}' ref='{ref}' role='{role}' />".format(
                                   primtype=self.primtype, ref=self.memberid, role=self.role) 

class Relation(OSM_Primitive):
    def __init__(self, ml, members = None, tags = None, attributes = None):
        super().__init__(ml, primitive='relation', attributes = attributes, tags=tags)

        self.members = []
        self.addMembers(members)
        ml.relations[self.attributes['id']] = self
        print (ml.relations)
    def addMembers(self,members):
        if members:
            for m in members:
                self.addMember(m)

    def addMember(self,member):
        self.members.append(member)

    def asXML(self):
        body = ''
        for member in self.members:
            body += member.asXML()

        return super().asXML(body=body)

class PT_Stop(Node):
    '''In this model a public transport stop is always mapped on a node with public_transport=platform tag
       This is a simplification, which makes sure there are always coordinates. In most cases this node
       represents the pole to which the flag with all details for the stop is mounted'''

    def __init__(self, ml, lon=0.0, lat=0.0, tags = None):
        super().__init__(ml, lon, lat, tags)
        self.tags['highway'] = 'bus_stop'
        self.tags['public_transport'] = 'platform'

class PT_StopArea(Relation):
    pass

class PT_Route(Relation):
    '''This is what we think of as a variation of a line'''
    def __init__(self, ml, members = None, tags = None, attributes = None):
        tags['type'] = 'route'
        print('attr PT: ', attributes)
        super().__init__(ml, attributes = attributes, tags = tags)

class PT_RouteMaster(Relation):
    '''This is what we think of as a publick transport line
       It contains route relations for each variation of an itinerary'''
    def __init__(self, ml, members = None, tags = None, attributes = None):
        tags['type'] = 'route_master'
        super().__init__(ml, attributes = attributes, tags = tags)

    def addRoute(self, route):
        m = RelationMember(primtype = 'relation', role = '', member = route)
        super().addMember(m)

class Edge():
    '''An edge is a sequence of ways that form a whole, they can either be between where highways fork,
       or where PT routes fork. An edge can contain shorter edges'''
    def __init__(self, ml, parts = None):
        self.parts = []
        if parts:
            self.parts = self.addParts(parts)
        #ml.edges[self.attributes['id']] = self
    def addParts(self, parts):
        for p in parts:
            self.addPart(p) 
    def addPart(self, part):
        self.parts.append(part)
    def getWays(self):
        ways = []
        if self.parts:
            for p in self.parts:
                try:
                    p.getNodes()
                    ways.append(p)
                except:
                    try:
                        ways.extend(p.getWays())
                    except:
                        pass
        return ways
'''
ml = MapLayer()
n1 = Node(ml)
n2 = Node(ml)
n3 = Node(ml)
n4 = Node(ml)
n5 = Node(ml)
n6 = Node(ml)
n7 = Node(ml)
n8 = Node(ml)

w1 = Way(ml, nodes = [n1, n2])
print(w1.asXML())
w2 = Way(ml, nodes = [n2, n3, n4])
w3 = Way(ml, nodes = [n4, n5])
w4 = Way(ml, nodes = [n5, n6])
w5 = Way(ml, nodes = [n6, n7])
w6 = Way(ml, nodes = [n7, n8])
print(w6.asXML())

e1 = Edge(ml, parts = [w1, w2])
e2 = Edge(ml, parts = [w3])
e3 = Edge(ml, parts = [w4, w5])
e4 = Edge(ml, parts = [w6])

print(e1.getWays())
print(e2.getWays())
print(e3.getWays())
print(e4.getWays())
'''
