# -*- coding: UTF-8 -*-

"""
Original author：
    Author: Arttu Rautio (aturtur)
    Website: http://aturtur.com/
    Github: https://github.com/aturtur
    
Plug-in version：
    Plugin-in：youdiaozi
    Github：https://github.com/youdiaozi
    Chinese version main page：http://live.c4d.cn/home.php?mod=space&uid=32217&do=index
"""

import c4d
import os
import sys
from c4d import gui, plugins, bitmaps
from abc import abstractmethod
from operator import attrgetter

try:
    import redshift
except:
    pass
    

# PLUGIN_ID
PLUGIN_ID_AR_ADDRSTEXTURECONTROLLERS        = 1054258
PLUGIN_ID_AR_ALIGNNODESHORIZONTALLY         = 1054259
PLUGIN_ID_AR_ALIGNNODESVERTICALLY           = 1054260
PLUGIN_ID_AR_CONNECTNODES                   = 1054261
PLUGIN_ID_AR_DISTRIBUTENODESHORIZONTALLY    = 1054262
PLUGIN_ID_AR_DISTRIBUTENODESVERTICALLY      = 1054263
PLUGIN_ID_AR_LINEUPNODESHORIZONTALLY        = 1054264
PLUGIN_ID_AR_LINEUPNODESVERTICALLY          = 1054265

# IDS
IDS_AR_ADDRSTEXTURECONTROLLERS_NAME                 = 50001
IDS_AR_ADDRSTEXTURECONTROLLERS_BMPNAME              = 50002
IDS_AR_ADDRSTEXTURECONTROLLERS_HELP                 = 50003

IDS_AR_ALIGNNODESHORIZONTALLY_NAME                  = 50011
IDS_AR_ALIGNNODESHORIZONTALLY_BMPNAME               = 50012
IDS_AR_ALIGNNODESHORIZONTALLY_HELP                  = 50013

IDS_AR_ALIGNNODESVERTICALLY_NAME                    = 50021
IDS_AR_ALIGNNODESVERTICALLY_BMPNAME                 = 50022
IDS_AR_ALIGNNODESVERTICALLY_HELP                    = 50023

IDS_AR_CONNECTNODES_NAME                            = 50031
IDS_AR_CONNECTNODES_BMPNAME                         = 50032
IDS_AR_CONNECTNODES_HELP                            = 50033

IDS_AR_DISTRIBUTENODESHORIZONTALLY_NAME             = 50041
IDS_AR_DISTRIBUTENODESHORIZONTALLY_BMPNAME          = 50042
IDS_AR_DISTRIBUTENODESHORIZONTALLY_HELP             = 50043

IDS_AR_DISTRIBUTENODESVERTICALLY_NAME               = 50051
IDS_AR_DISTRIBUTENODESVERTICALLY_BMPNAME            = 50052
IDS_AR_DISTRIBUTENODESVERTICALLY_HELP               = 50053

IDS_AR_LINEUPNODESHORIZONTALLY_NAME                 = 50061
IDS_AR_LINEUPNODESHORIZONTALLY_BMPNAME              = 50062
IDS_AR_LINEUPNODESHORIZONTALLY_HELP                 = 50063

IDS_AR_LINEUPNODESVERTICALLY_NAME                   = 50071
IDS_AR_LINEUPNODESVERTICALLY_BMPNAME                = 50072
IDS_AR_LINEUPNODESVERTICALLY_HELP                   = 50073

# spacing for AR_LineUpNodesHorizontally and AR_LineUpNodesVertically, hold Shift to customize
GAP_SIZE = 40

class NodeObject(object):
    def __init__(self, obj, px, py, sx, sy):
        self.node = obj # Node object
        self.px = px # X position
        self.py = py # Y position
        self.sx = sx # X scale
        self.sy = sy # Y scale

class AR_NodeToolBase(plugins.CommandData):
    
    def Execute(self, doc):
        c4d.CallCommand(13957) # Clear Console
        
        #doc = c4d.documents.GetActiveDocument() # Get active document
        keyMod = self.GetKeyMod()
                
        doc.StartUndo() # Start recording undos
        materials = doc.GetMaterials() # Get materials
        selection = doc.GetSelection() # Get active selection
        
        try: # Try to execute following script
            # Xpresso
            for s in selection: # Iterate through selection
                if type(s).__name__ == "XPressoTag": # If operator is xpresso tag
                    xpnm = s.GetNodeMaster() # Get node master
                    self.ExecuteSpecCommand(xpnm, keyMod) # Run the main function
            # Redshift
            for m in materials: # Iterate through materials
                if m.GetBit(c4d.BIT_ACTIVE): # If material is selected
                    rsnm = redshift.GetRSMaterialNodeMaster(m) # Get Redshift material node master
                    self.ExecuteSpecCommand(rsnm, keyMod) # Run the main function
        except: # Otherwise
            pass # Do nothing
        doc.EndUndo() # Stop recording undos
        c4d.EventAdd() # Refresh Cinema 4D
        
        return True
        
    def GetSelectedNodes(self, nodeMaster):
        nodes = [] # Initialize a list for collecting nodes
        root = nodeMaster.GetRoot() # Get xpresso root
        for node in root.GetChildren(): # Iterate through nodes
            if node.GetBit(c4d.BIT_ACTIVE): # If node is selected
                bc = node.GetData() # Get copy of base container
                bsc = bc.GetContainer(c4d.ID_SHAPECONTAINER) # Get copy of shape container
                bcd = bsc.GetContainer(c4d.ID_OPERATORCONTAINER) # Get copy of operator container
                px  = bcd.GetReal(100) # Get x position
                py  = bcd.GetReal(101) # Get y position
                sx  = bcd.GetReal(108) # Get x scale
                sy  = bcd.GetReal(109) # Get y scale
                nodes.append(NodeObject(node, px, py, sx, sy)) # Create NodeObject and add it to a list
                
        return nodes
        
    def GetKeyMod(self):
        bc = c4d.BaseContainer() # Initialize a base container
        keyMod = "None" # Initialize a keyboard modifier status
        # Button is pressed
        if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.BFM_INPUT_CHANNEL,bc):
            if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QSHIFT:
                if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL: # Ctrl + Shift
                    if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Ctrl + Shift
                        keyMod = 'Alt+Ctrl+Shift'
                    else: # Shift + Ctrl
                        keyMod = 'Ctrl+Shift'
                elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Shift
                    keyMod = 'Alt+Shift'
                else: # Shift
                    keyMod = 'Shift'
            elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL:
                if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Ctrl
                    keyMod = 'Alt+Ctrl'
                else: # Ctrl
                    keyMod = 'Ctrl'
            elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt
                keyMod = 'Alt'
            else: # No keyboard modifiers used
                keyMod = 'None'
                
        return keyMod
    
    """
    for child
    """
    @abstractmethod
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        pass
        
class AR_AddRSTextureControllers(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.AddControllers(nodeMaster, keyMod)

    # only works for RedShift
    def AddControllers(self, nodeMaster, keyMod):
        nodes = self.GetSelectedNodes(nodeMaster)

        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('py')) # Get the node with the minimum y position value

            # Node generation
            scaleNode = nodeMaster.CreateNode(root, 400001120, firstNode.node, x = -1, y = -1) # Crete a constant node (RS)
            offsetNode = nodeMaster.CreateNode(root, 400001120, firstNode.node, x = -1, y = -1)
            rotateNode = nodeMaster.CreateNode(root, 400001120, firstNode.node, x = -1, y = -1)
            newNodes = [scaleNode, offsetNode, rotateNode]

            scaleNode.SetBit(c4d.BIT_ACTIVE) # Select node
            offsetNode.SetBit(c4d.BIT_ACTIVE) # Select node
            rotateNode.SetBit(c4d.BIT_ACTIVE) # Select node

            # Node settings and ports
            for i in range(0, len(nodes)): # Iterate through collected nodes
                node = nodes[i].node # Get node
                node.DelBit(c4d.BIT_ACTIVE)
                if node.GetOperatorID() == 1036227:
                    if node[c4d.GV_REDSHIFT_SHADER_META_CLASSNAME] == "TextureSampler":
                        scaleID = 10011
                        offsetID = 10012
                        rotateID = 10013

                        scaleNode[c4d.ID_BASELIST_NAME] = "SCALE" # Set name
                        scaleNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.325, 0.51, 0.357) # Set color
                        scaleNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set data type to vector
                        scaleNode[c4d.GV_CONST_VALUE] = c4d.Vector(1, 1, 1) # Set default values
                        offsetNode[c4d.ID_BASELIST_NAME] = "OFFSET" # Set name
                        offsetNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.325, 0.51, 0.357) # Set color
                        offsetNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set data type to vector
                        rotateNode[c4d.ID_BASELIST_NAME] = "ROTATE" # Set name
                        rotateNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.537, 0.71, 0.569) # Set color

                    elif node[c4d.GV_REDSHIFT_SHADER_META_CLASSNAME] == "TriPlanar":
                        scaleID = 10005
                        offsetID = 10006
                        rotateID = 10007

                        scaleNode[c4d.ID_BASELIST_NAME] = "SCALE" # Set name
                        scaleNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.325, 0.51, 0.357) # Set color
                        scaleNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set data type to vector
                        scaleNode[c4d.GV_CONST_VALUE] = c4d.Vector(0.01, 0.01, 0.01) # Set default values
                        scaleNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set values
                        offsetNode[c4d.ID_BASELIST_NAME] = "OFFSET" # Set name
                        offsetNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.325, 0.51, 0.357) # Set color
                        offsetNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set data type to vector
                        rotateNode[c4d.ID_BASELIST_NAME] = "ROTATE" # Set name
                        rotateNode[c4d.GV_DYNAMIC_DATATYPE] = 23 # Set data type to vector
                        rotateNode[c4d.ID_GVBASE_COLOR]  = c4d.Vector(0.325, 0.51, 0.357) # Set color

                if node.AddPortIsOK(c4d.GV_PORT_INPUT, scaleID):
                    scaleInPort = node.AddPort(c4d.GV_PORT_INPUT, scaleID) # Scale port
                else:
                    scaleInPort = node.GetInPort(self.GetPortIndex(node, scaleID))

                if node.AddPortIsOK(c4d.GV_PORT_INPUT, offsetID):
                    offsetInPort = node.AddPort(c4d.GV_PORT_INPUT, offsetID) # Offset port
                else:
                    offsetInPort = node.GetInPort(self.GetPortIndex(node, offsetID))

                if node.AddPortIsOK(c4d.GV_PORT_INPUT, rotateID):
                    rotateInPort = node.AddPort(c4d.GV_PORT_INPUT, rotateID) # Rotate port
                else:
                    rotateInPort = node.GetInPort(self.GetPortIndex(node, rotateID))

                #scaleNode
                scaleOutPort = scaleNode.GetOutPort(0)
                offsetOutPort = offsetNode.GetOutPort(0)
                rotateOutPort = rotateNode.GetOutPort(0)

                # Connect nodes
                scaleOutPort.Connect(scaleInPort)
                offsetOutPort.Connect(offsetInPort)
                rotateOutPort.Connect(rotateInPort)

            for i in range(0, len(newNodes)):
                bc  = newNodes[i].GetDataInstance() # Get base container
                bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
                bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
                px = firstNode.px - 200
                py = firstNode.py + (50 * i)
                bcd.SetReal(100, px) # Set x position
                bcd.SetReal(101, py) # Set y position
                
    def GetPortIndex(node, portId):
        inPorts = node.GetInPorts()
        for i, port in enumerate(inPorts):
            if port.GetMainID() == portId:
                return i

class AR_AlignNodesHorizontally(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.AlignNodesHor(nodeMaster, keyMod)
        
    def AlignNodesHor(self, nodeMaster, keyMod):
        nodes = self.GetSelectedNodes(nodeMaster)
        
        if nodes:
            theNode = min(nodes, key=attrgetter('px'))
            nodes.sort(key=attrgetter('px')) # Sort nodes by x position
            
        nodeMaster.AddUndo() # Add undo for changing nodes
        for i in range(0, len(nodes)): # Iterate through collected nodes
            node =  nodes[i].node # Get node
            bc = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
            p = theNode.py
            if keyMod == "Shift":
                if i != 0:
                    tAnchor = nodes[i].sy / 2.0
                    sAnchor = (theNode.py + (theNode.sy / 2.0))
                    p = (sAnchor - tAnchor)
            elif keyMod == "Ctrl":
                if i != 0:
                    tAnchor = nodes[i].sy
                    sAnchor = (theNode.py + theNode.sy)
                    p = (sAnchor - tAnchor)
            bcd.SetReal(101, p) # Set y position
            
class AR_AlignNodesVertically(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.AlignNodesVer(nodeMaster, keyMod)
        
    def AlignNodesVer(self, nodeMaster, keyMod):        
        nodes = self.GetSelectedNodes(nodeMaster)
        if nodes:
            theNode = min(nodes, key=attrgetter('py'))
            nodes.sort(key=attrgetter('py')) # Sort nodes by y position
            
        nodeMaster.AddUndo() # Add undo for changing nodes
        for i in range(0, len(nodes)): # Iterate through collected nodes
            node =  nodes[i].node # Get node
            bc = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
            p = theNode.px
            if keyMod == "Shift":
                if i != 0:
                    tAnchor = nodes[i].sx / 2.0
                    sAnchor = (theNode.px + (theNode.sx / 2.0))
                    p = (sAnchor - tAnchor)
            elif keyMod == "Ctrl":
                if i != 0:
                    tAnchor = nodes[i].sx
                    sAnchor = (theNode.px + theNode.sx)
                    p = (sAnchor - tAnchor)        
            bcd.SetReal(100, p) # Set x position
            
class AR_ConnectNodes(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):        
        # real action
        self.ConnectNodes(nodeMaster, keyMod)

    def ConnectNodes(self, nodeMaster, keyMod):
        nodes = [] # Initialize a list
        root = nodeMaster.GetRoot() # Get node master root
        nodeMaster.AddUndo() # Add undo for changing nodes
        
        nodes = self.GetSelectedNodes(nodeMaster)
        
        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('px')) # Get the node with the minimum x position value
            lastNode = max(nodes, key=attrgetter('px')) # Get the node with the maximum x position value
            
            if keyMod == "None":
                outPort = self.GetPort(firstNode.node.GetOutPorts()) # Get out port
                inPort = self.GetPort(lastNode.node.GetInPorts()) # Get in port
            elif keyMod == "Shift":
                outPortNr = int(c4d.gui.InputDialog("From port number", 0))
                inPortNr = int(c4d.gui.InputDialog("To port number", 0))
                outPort = firstNode.node.GetOutPort(outPortNr)
                inPort = lastNode.node.GetInPort(inPortNr)
            elif keyMod == "Ctrl":
                outPort = self.GetLastPort(firstNode.node.GetOutPorts()) # Get out port
                inPort = self.GetLastPort(lastNode.node.GetInPorts()) # Get in port
                
            outPort.Connect(inPort) # Connect ports
            
    def GetPort(self, ports):
        for i, port in enumerate(ports):
            if port.GetNrOfConnections() == 0:
                return port
        return ports[0]

    def GetLastPort(self, ports):
        for i, port in enumerate(reversed(ports)):
            if port.GetNrOfConnections() == 0:
                return port
        return ports[-1]

class AR_DistributeNodesHorizontally(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.DistributeNodesHor(nodeMaster)
        
    def DistributeNodesHor(self, nodeMaster):        
        nodes = self.GetSelectedNodes(nodeMaster)
        
        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('px')) # Get the node with the minimum x position value
            lastNode  = max(nodes, key=attrgetter('px')) # Get the node with the maximum x position value
            fpos = firstNode.px + firstNode.sx # Get first position
            lpos = lastNode.px # Get last position
            nodes.sort(key=attrgetter('px')) # Sort nodes by x position
            totalScale = 0 # Init total scale variable
            for i in range (len(nodes)): # Iterate through nodes
                if i != 0 and i != len(nodes)-1: # Not first nor last
                    totalScale = totalScale + nodes[i].sx # Calculate total scale
            distance = lpos - fpos # Calculate distance between first and last node
            count = len(nodes) # Get count of nodes
            gap = float((distance-totalScale))/float((count-1)) # Calculate gap between nodes
            r = fpos # Initialize a r variable
            
        helper = 0 # Initialize a helper variable
        nodeMaster.AddUndo() # Add undo for changing nodes
        for i in range(0, len(nodes)): # Iterate through collected nodes
            node=  nodes[i].node # Get node
            bc  = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
            if i != 0 and i != len(nodes)-1: # Not first nor last node
                s = nodes[i].sx # Get node length
                r = r + gap + helper # Calculate node position
                helper = s # Set helper
                bcd.SetReal(100, r) # Set x position
                
class AR_DistributeNodesVertically(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.DistributeNodesVer(nodeMaster)
        
    def DistributeNodesVer(self, nodeMaster):        
        nodes = self.GetSelectedNodes(nodeMaster)
        
        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('py')) # Get the node with the minimum y position value
            lastNode  = max(nodes, key=attrgetter('py')) # Get the node with the maximum y position value
            fpos = firstNode.py + firstNode.sy # Get first position
            lpos = lastNode.py # Get last position
            nodes.sort(key=attrgetter('py')) # Sort nodes by y position
            totalScale = 0 # Init total scale variable
            for i in range (len(nodes)): # Iterate through nodes
                if i != 0 and i != len(nodes)-1: # Not first nor last
                    totalScale = totalScale + nodes[i].sy # Calculate total scale
            distance = lpos - fpos # Calculate distance between first and last node
            count = len(nodes) # Get count of nodes
            gap = float((distance-totalScale))/float((count-1)) # Calculate gap between nodes
            r = fpos # Initialize a r variable
            
        helper = 0 # Initialize a helper variable
        nodeMaster.AddUndo() # Add undo for changing nodes
        for i in range(0, len(nodes)): # Iterate through collected nodes
            node=  nodes[i].node # Get node
            bc  = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
            if i != 0 and i != len(nodes)-1: # Not first nor last node
                s = nodes[i].sy # Get node length
                r = r + gap + helper # Calculate node position
                helper = s # Set helper
                bcd.SetReal(101, r) # Set y position

class AR_LineUpNodesHorizontally(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):        
        # real action
        self.LineUpNodesHor(nodeMaster, keyMod)
        
    def LineUpNodesHor(self, nodeMaster, keyMod):        
        nodes = self.GetSelectedNodes(nodeMaster)
        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('px')) # Get the node with the minimum x position value
            fpos = firstNode.px + firstNode.sx # Get first position
            nodes.sort(key=attrgetter('px')) # Sort nodes by x position
            count = len(nodes) # Get count of nodes
            r = fpos # Initialize a r variable
        helper = 0 # Initialize a helper variable
        nodeMaster.AddUndo() # Add undo for changing nodes
        
        global GAP_SIZE
        if keyMod == "None":
            gap = GAP_SIZE
        elif keyMod == "Shift":
            gap = float(c4d.gui.InputDialog("Gap size", GAP_SIZE))
            GAP_SIZE = gap

        for i in range(0, len(nodes)): # Iterate through collected nodes
            node=  nodes[i].node # Get node
            bc  = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container            
            if i != 0: # Not first node
                s = nodes[i].sx # Get node length
                r = r + gap + helper # Calculate node position
                helper = s # Set helper
                bcd.SetReal(100, r) # Set x position
                bcd.SetReal(101, firstNode.py) # Set y position
                
class AR_LineUpNodesVertically(AR_NodeToolBase):
    def ExecuteSpecCommand(self, nodeMaster, keyMod):
        # real action
        self.LineUpNodesVer(nodeMaster, keyMod)
        
    def LineUpNodesVer(self, nodeMaster, keyMod):
        nodes = self.GetSelectedNodes(nodeMaster)
        
        if nodes: # If there is nodes
            firstNode = min(nodes, key=attrgetter('py')) # Get the node with the minimum x position value
            fpos = firstNode.py + firstNode.sy # Get first position
            nodes.sort(key=attrgetter('py')) # Sort nodes by x position
            count = len(nodes) # Get count of nodes
            r = fpos # Initialize a r variable
        helper = 0 # Initialize a helper variable
        nodeMaster.AddUndo() # Add undo for changing nodes
        
        global GAP_SIZE
        if keyMod == "None":
            gap = GAP_SIZE
        elif keyMod == "Shift":
            gap = float(c4d.gui.InputDialog("Gap size", GAP_SIZE))
            GAP_SIZE = gap

        for i in range(0, len(nodes)): # Iterate through collected nodes
            node=  nodes[i].node # Get node
            bc  = node.GetDataInstance() # Get base container
            bsc = bc.GetContainerInstance(c4d.ID_SHAPECONTAINER) # Get shape container
            bcd = bsc.GetContainerInstance(c4d.ID_OPERATORCONTAINER) # Get operator container
            if i != 0: # Not first node
                s = nodes[i].sy # Get node length
                r = r + gap + helper # Calculate node position
                helper = s # Set helper
                bcd.SetReal(100, firstNode.px) # Set x position
                bcd.SetReal(101, r) # Set y position
    
def RegisterCommandData(id, name, bmpName, bmpPath, commmandData, help):
    bmp = bitmaps.BaseBitmap()
    bmp.InitWith(os.path.join(bmpPath, "res", bmpName + ".tif"))
    plugins.RegisterCommandPlugin(id=id, str=name, info=0, icon=bmp, help=help, dat=commmandData) # info=flag, 

def LoadPluginStrings(idsArray):
    name = UnescapeString(idsArray[0])
    bmpName = UnescapeString(idsArray[1])
    help = UnescapeString(idsArray[2])
    return name, bmpName, help

def UnescapeString(ids):
    specSign = '-|-|'
    text = ""
    try:
        text = plugins.GeLoadString(ids).replace('\\n', '\n').replace('\\t', '\t')
        text = text.replace('\\\\', specSign).encode('utf-8').replace('\\', '').replace(specSign, '\\')
    except:
        try:
            text = plugins.GeLoadString(ids).replace('\\n', '\n')
        except:
            text = plugins.GeLoadString(ids)

    return text

if __name__ == "__main__":
    path, fn = os.path.split(__file__)
    
    # AR_AddRSTextureControllers
    name, bmpName, help = LoadPluginStrings([IDS_AR_ADDRSTEXTURECONTROLLERS_NAME, 
                                             IDS_AR_ADDRSTEXTURECONTROLLERS_BMPNAME, 
                                             IDS_AR_ADDRSTEXTURECONTROLLERS_HELP])
    RegisterCommandData(PLUGIN_ID_AR_ADDRSTEXTURECONTROLLERS, name, bmpName, path, AR_AddRSTextureControllers(), help)
    
    # AR_AlignNodesHorizontally
    name, bmpName, help = LoadPluginStrings([IDS_AR_ALIGNNODESHORIZONTALLY_NAME, 
                                             IDS_AR_ALIGNNODESHORIZONTALLY_BMPNAME, 
                                             IDS_AR_ALIGNNODESHORIZONTALLY_HELP])                                             
    RegisterCommandData(PLUGIN_ID_AR_ALIGNNODESHORIZONTALLY, name, bmpName, path, AR_AlignNodesHorizontally(), help)
    
    # AR_AlignNodesVertically
    name, bmpName, help = LoadPluginStrings([IDS_AR_ALIGNNODESVERTICALLY_NAME, 
                                             IDS_AR_ALIGNNODESVERTICALLY_BMPNAME, 
                                             IDS_AR_ALIGNNODESVERTICALLY_HELP])
    RegisterCommandData(PLUGIN_ID_AR_ALIGNNODESVERTICALLY, name, bmpName, path, AR_AlignNodesVertically(), help)
    
    # AR_ConnectNodes
    name, bmpName, help = LoadPluginStrings([IDS_AR_CONNECTNODES_NAME, 
                                             IDS_AR_CONNECTNODES_BMPNAME, 
                                             IDS_AR_CONNECTNODES_HELP])
    RegisterCommandData(PLUGIN_ID_AR_CONNECTNODES, name, bmpName, path, AR_ConnectNodes(), help)
    
    # AR_DistributeNodesHorizontally
    name, bmpName, help = LoadPluginStrings([IDS_AR_DISTRIBUTENODESHORIZONTALLY_NAME, 
                                             IDS_AR_DISTRIBUTENODESHORIZONTALLY_BMPNAME, 
                                             IDS_AR_DISTRIBUTENODESHORIZONTALLY_HELP])
    RegisterCommandData(PLUGIN_ID_AR_DISTRIBUTENODESHORIZONTALLY, name, bmpName, path, AR_DistributeNodesHorizontally(), help)
    
    # AR_DistributeNodesVertically
    name, bmpName, help = LoadPluginStrings([IDS_AR_DISTRIBUTENODESVERTICALLY_NAME, 
                                             IDS_AR_DISTRIBUTENODESVERTICALLY_BMPNAME, 
                                             IDS_AR_DISTRIBUTENODESVERTICALLY_HELP])
    RegisterCommandData(PLUGIN_ID_AR_DISTRIBUTENODESVERTICALLY, name, bmpName, path, AR_DistributeNodesVertically(), help)
    
    # AR_LineUpNodesHorizontally
    name, bmpName, help = LoadPluginStrings([IDS_AR_LINEUPNODESHORIZONTALLY_NAME, 
                                             IDS_AR_LINEUPNODESHORIZONTALLY_BMPNAME, 
                                             IDS_AR_LINEUPNODESHORIZONTALLY_HELP])
    RegisterCommandData(PLUGIN_ID_AR_LINEUPNODESHORIZONTALLY, name, bmpName, path, AR_LineUpNodesHorizontally(), help)
    
    # AR_LineUpNodesVertically
    name, bmpName, help = LoadPluginStrings([IDS_AR_LINEUPNODESVERTICALLY_NAME, 
                                             IDS_AR_LINEUPNODESVERTICALLY_BMPNAME, 
                                             IDS_AR_LINEUPNODESVERTICALLY_HELP])
    RegisterCommandData(PLUGIN_ID_AR_LINEUPNODESVERTICALLY, name, bmpName, path, AR_LineUpNodesVertically(), help)

    print("RegisterCommandData successfully")