import nuke


def RGBtoTILE(R,G,B):
    '''
    RGBtoTILE(R, G, B) -> int      ( cut from backdropTools.py of Ivan Busquets - 2011 )
    
    Returns a 32 bit int ready to feed into a "tile_color" knob, from
    Red, Green and Blue values in the 0-1 range.
    '''
    return int('%02x%02x%02x%02x' % (R*255,G*255,B*255,255), 16 )

def ShuffleOutAllChannels():
    nodes = [node for node in nuke.selectedNodes()]
    
    if not nodes:
        nuke.message('ShuffleOutAllChannels\n- No node selected')
        return

    # options
    # this list have to matching with the last list
    options = ['Cryptomatte', 'Diffuse Lgroup', 'Specular Lgroup\n(Reflect Lgroup)', 'Refract Lgroup\n(Transmission Lgroup)',
               'SSS Lgroup', 'Coat Lgroup', 'Volume Lgroup', 'AOV[Arnold]', 'AOV2[Houdini]', 'Utilities', 'Depth', 'Others...']
    
    # build UI 
    p = nuke.Panel('Select Channels')
    for opt in options:
        if 'Cryptomatte' in opt:
            p.addBooleanCheckBox(opt, False)
        else:
            p.addBooleanCheckBox(opt, True)
    p.show()
    
    # create True/False list to select channels
    result = []
    for opt in options:
        result.append(p.value(opt))

    for node in nodes:
        # initialize empty groups
        diffuselitG = []
        cryptoG = []
        specularlitG = []
        refractG = []
        sssG = []
        coatG = []
        volumeG = []
        aovG = []
        aov2G = []
        utilG = []
        depthG = []
        otherG = []


        layers = sorted(list(set([channel.split('.')[0] for channel in node.channels()])))

        if 'rgba' in layers:
            layers.remove('rgba')

        # collect layer groups
        for n in layers:
            # Cryptomatte list
            if n.startswith('crypto'):
                cryptoG.append(n)

            # Diffuse Light group list
            elif n.endswith('_diffuse') == True and n.startswith('all_') == False:
                diffuselitG.append(n)
            elif n.startswith('diffuse_'):
                diffuselitG.append(n)

            # Specular Light group list
            elif n.endswith('_reflect') == True and n.startswith('all_') == False:
                specularlitG.append(n)
            elif n.startswith('specular_'):
                specularlitG.append(n)

            # Refract Light group list
            elif n.endswith('_refract') == True and n.startswith('all_') == False:
                refractG.append(n)
            elif n.startswith('transmission_'):
                refractG.append(n)

            # SSS Light group list
            elif n.endswith('_sss') == True and n.startswith('all_') == False:
                sssG.append(n)
            elif n.startswith('sss_'):
                sssG.append(n)

            # Coat Light group list
            elif n.endswith('_coat') == True and n.startswith('all_') == False:
                coatG.append(n)
            elif n.startswith('coat_'):
                coatG.append(n)

            # Volume Light group list
            elif n.endswith('_volume') == True and n.startswith('all_') == False:
                volumeG.append(n)
            elif n.startswith('volume'):
                volumeG.append(n)

            # AOV1 list
            elif n in ['GI','SSS','lighting','reflect','refract','specular','coat','emission','occ','sss','transmission','diffuse']:
                aovG.append(n)
            elif n in ['direct','indirect']:
                aovG.append(n)

            # AOV2 list
            elif n.startswith('all_'):
                aov2G.append(n)

            # Util list
            elif n in ['fresnel', 'pointCamera', 'pointWorld', 'normals', 'P', 'N']:
                utilG.append(n)
            elif n.startswith('utility_') or n.startswith('world_'):
                utilG.append(n)

            # Depth list
            elif n.startswith('depth'):
                depthG.append(n)
            elif n in ['Z']:
                depthG.append(n)

        # collect rest of layers
        for n in layers:
            if n not in cryptoG+specularlitG+diffuselitG+refractG+sssG+coatG+volumeG+aovG+aov2G+utilG+depthG:
                otherG.append(n)

        selectnode = nuke.selectedNode()
        dot = selectnode
        group_positionX = 50
        backdrop_positionX = 0

        for row, o in enumerate([cryptoG, diffuselitG, specularlitG, refractG, sssG, coatG, volumeG, aovG, aov2G, utilG, depthG, otherG]):
            if result[row]:

                backdrop_nodes = []

                for layer in o:

                    # Make Dot Node
                    dot_xpos = 0 if dot == selectnode else 150
                    if layer in diffuselitG:
                        if layer == diffuselitG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in specularlitG:
                        if layer == specularlitG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in refractG:
                        if layer == refractG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in sssG:
                        if layer == sssG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in coatG:
                        if layer == coatG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in volumeG:
                        if layer == volumeG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in aovG:
                        if layer == aovG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in aov2G:
                        if layer == aov2G[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in utilG:
                        if layer == utilG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in depthG:
                        if layer == depthG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in cryptoG:
                        if layer == cryptoG[0] and dot != selectnode:
                            dot_xpos += group_positionX
                    elif layer in otherG:
                        if layer == otherG[0] and dot != selectnode:
                            dot_xpos += group_positionX

                    dot = nuke.nodes.Dot(inputs=[dot])
                    dot.setXYpos(dot.xpos() + dot_xpos, selectnode.ypos() + 200)

                    # Make Suffle Node
                    shuffleNode = nuke.nodes.Shuffle(label=layer, inputs=[dot])
                    shuffleNode['in'].setValue( layer )
                    shuffleNode['postage_stamp'].setValue(True)
                    shuffleNode.setYpos(shuffleNode.ypos() + 150)

                    # Make Backdrop Node
                    backdrop_node = nuke.nodes.BackdropNode()
                    backdrop_node.knob('bdwidth').setValue(150)
                    backdrop_node.knob('bdheight').setValue(220)
                    backdrop_nodes.append(backdrop_node)
                    backdrop_node.knob('label').setValue(layer)
                    backdrop_node.knob('note_font_size').setValue(18)
                    backdrop_node.setXpos(selectnode.xpos() + backdrop_positionX - 35)
                    backdrop_node.setYpos(dot.ypos() + 70)
                    backdrop_positionX += 150

                    if layer in cryptoG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(1, 0, 0))
                        backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.9, 0, 0))

                    elif layer in diffuselitG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.443, 0.443, 0.776))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.5, 0.5, 0.8))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.4, 0.4, 0.7))
                        if layer == diffuselitG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in specularlitG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.859, 1, 0.145))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.8, 0.98, 0.3))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.7, 0.82, 0.2))
                        if layer == specularlitG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in refractG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.522, 0.82, 0.33))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.6, 0.9, 0.4))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.5, 0.8, 0.3))
                        if layer == refractG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in sssG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(1, 0.729, 0.443))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(1, 0.788, 0.667))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.78, 0.573, 0.447))
                        if layer == sssG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in coatG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.498, 0.894, 1))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.444, 0.88, 0.782))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.345, 0.78, 0.678))
                        if layer == coatG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in volumeG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.12, 0.25, 1))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(.45, 0.65, 1))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.3, 0.5, 0.85))
                        if layer == volumeG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in aovG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(1, 0.373, 0))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(1, 0.45, 0.1))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.9, 0.385, 0))
                        if layer == aovG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in aov2G:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(1, 1, 0))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(1, 0.905, 0.56))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.915, 0.785, 0.55))
                        if layer == aov2G[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in utilG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0, 0.625, 1))
                        for backdrop_node in backdrop_nodes[::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.1, 0.7, 1))
                        for backdrop_node in backdrop_nodes[1::2]:
                            backdrop_node.knob('tile_color').setValue(RGBtoTILE(0, 0.6, 0.9))
                        if layer == utilG[-1] and dot != selectnode:
                            backdrop_positionX += group_positionX

                    elif layer in depthG:
                        shuffleNode.knob('tile_color').setValue(RGBtoTILE(0.5, 0, 1))
                        backdrop_node.knob('tile_color').setValue(RGBtoTILE(0.6, 0.1, 1))
                        backdrop_positionX += group_positionX

