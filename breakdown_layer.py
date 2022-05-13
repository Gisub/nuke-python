import nuke
from PySide.QtCore import QTimer

def breakdown_layer_tab(read):

    path = read['file'].value()
    FileExtension = path.split('.')[-1]

    # Create knobs
    if FileExtension == 'psd':
        tab = nuke.Tab_Knob('M83', 'M83')
        read.addKnob(tab)

        pyknob = nuke.PyScript_Knob('breakdown',
                                    'Breakdown Layer',
                                    'breakdown_layer.Mattebreakout()'
                                    )
        pyknob.setFlag(nuke.STARTLINE)
        read.addKnob(pyknob)

def onReadNodeCreated():
    read = nuke.thisNode()
    QTimer.singleShot(0, lambda: breakdown_layer_tab(read))

nuke.addOnUserCreate(lambda: onReadNodeCreated(), nodeClass='Read')


class Layer():
  def __init__(self):
    self.attrs = {}


def getLayers(metadata):
    layers = []

    for key in metadata:
        if key.startswith( 'input/psd/layers/' ):
            splitKey = key.split( '/' )
            num = int( splitKey[3] )
            attr = splitKey[4]
            try:
                attr += '/' + splitKey[5]
            except:
                pass

            while ( len(layers) <= num ):
                layers.append( Layer() )
            layers[num].attrs[ attr ] = metadata[key]

    return layers


def Mattebreakout():

    thisnode = nuke.thisNode()

    metaData = thisnode.metadata()
    layers = getLayers(metaData)
    shuffle_xpos = 0
    shuffle_ypos = 0
    shuffleNode = thisnode
    latest_node = None

    for l in layers:
        name = l.attrs['nukeName']

        if shuffleNode == thisnode:
            shuffle_xpos = 0
            shuffle_ypos += 50
        else:
            shuffle_xpos = -200
            shuffle_ypos += 300

        shuffleNode = nuke.nodes.Shuffle()
        shuffleNode.setInput(0, thisnode)
        shuffleNode.setXpos(shuffleNode.xpos() + shuffle_xpos)
        shuffleNode.setYpos(shuffleNode.ypos() + shuffle_ypos)
        shuffleNode['in'].setValue(name)
        shuffleNode['hide_input'].setValue(True)
        shuffleNode['postage_stamp'].setValue(True)
        shuffleNode['label'].setValue("[value in]")

        cropNode = nuke.nodes.Crop()
        cropNode.setInput(0, shuffleNode)
        cropNode.setYpos(cropNode.ypos() + 50)
        cropNode['box'].setValue(l.attrs['x'], 0)
        cropNode['box'].setValue(l.attrs['y'], 1)
        cropNode['box'].setValue(l.attrs['r'], 2)
        cropNode['box'].setValue(l.attrs['t'], 3)

        if latest_node:
            PremultNode = nuke.nodes.Premult(inputs=[cropNode])
            PremultNode.setYpos(PremultNode.ypos() + 50)
            MergeNode = nuke.nodes.Merge2(operation='over', inputs=[latest_node, PremultNode])
            latest_node = MergeNode
        else:
            PremultNode = nuke.nodes.Premult(inputs=[cropNode])
            PremultNode.setYpos(PremultNode.ypos() + 50)
            latest_node = PremultNode


# Mattebreakout()
