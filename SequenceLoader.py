
#-------------------------------------------------------------------------------
#-Module Import
#-------------------------------------------------------------------------------

import nuke, os
from Qt import QtWidgets, QtGui, QtCore

#-------------------------------------------------------------------------------
#-Global Variables
#-------------------------------------------------------------------------------

DATA_AOV = ['P', 'N', 'Z', 'crypto_object', 'crypto_material', 'crypto_asset']

#-------------------------------------------------------------------------------
#-Supporting Function
#-------------------------------------------------------------------------------

def joinPath(*paths):
    '''joining path to fix windows and OSX symlink to '/' uniformly'''
    try:
        p = os.path.join(*paths).replace('\\', '/')
        return p
    except ValueError:
        pass

def createRead(path):
	'''create read from path
	@path: full path for AOV, (str)
	return: aov read node, (obj)
	'''

	for ls in nuke.getFileNameList(path):

		if '_lgroups' in ls:
			frames, range = ls.split(' ')
			first, last = range.split('-')
			first = int(first)
			last = int(last)
			aov = nuke.nodes.Read(
				file=joinPath(path, frames),
				name=os.path.basename(path) + '_lgroups',
				first=first,
				last=last,
				label=os.path.basename(path) + '_lgroups'
				)
		else:
			exrs = nuke.getFileNameList(path)[0]
			if ' ' in exrs:
				frames, range = exrs.split(' ')
				first, last = range.split('-')
				first = int(first)
				last = int(last)
				aov = nuke.nodes.Read(
					file=joinPath(path, frames),
					name=os.path.basename(path),
					first=first,
					last=last,
					label=os.path.basename(path)
					)
			else:
				aov = nuke.nodes.Read(
					file=joinPath(path, exrs),
					name=os.path.basename(path),
					label=os.path.basename(path)
					)
			isData = True if aov.name() in DATA_AOV else False
			aov['raw'].setValue(isData)


def createDeepRead(path):
	for ls in nuke.getFileNameList(path):
		exrs = nuke.getFileNameList(path)[0]
		frames, range = exrs.split(' ')
		first, last = range.split('-')
		first = int(first)
		last = int(last)
		Deep = nuke.createNode('DeepRead', 'tile_color 0x20202000')
		Deep['file'].setValue(joinPath(path, frames))
		Deep['first'].setValue(first)
		Deep['last'].setValue(last)
		Deep['label'].setValue('<b><font color=white>[knob first]-[knob last]([expr [knob last]-[knob first]+1])</font></b>\n\n<b><font color=white>[lrange [file split [regexp -inline "show.*" [value [topnode].file]]] 5 5]</font></b>\n<small><font color=#999>Resolution:</font> [value width] x [value height]</font></small>\n<small><font color=#999>Modified:</font> [clock format [file mtime [file dirname [value file]]] -format {%Y/%m/%d %H:%M:%S}]</font></small>\n<b><font color=orange>[if {[value disable]} {return} else {return [metadata input/timecode]}]</font></b>')


def getAOVs(dir_renderVersion):
	'''get renderLayer, then passes
	@path: Render root path (ie. '/TIO_orbit_1k_v001'), str
	return: {<renderLayer>: [<renderPasses>]}
	'''
	ls_aov = {}
	for l in nuke.getFileNameList(dir_renderVersion):
		thisLayer = [p for p in nuke.getFileNameList(joinPath(dir_renderVersion, l))]
		ls_aov[l] = thisLayer

	return ls_aov


def shuffling(node_B, aov_rest):
	'''create ShuffleCopy with changing nodes, then connects output
	@node_B: node on B pipe (obj), changes per interation
	@aov_rest: list of nodes except the beauty node (list of objs)
	'''
	curB = node_B
	for n in aov_rest:
		if 'crypto_' in n.name():
			thisB = nuke.nodes.Copy(
						inputs=[curB, n],
						name='in_%s' % n.name(),
						channels='all',
						metainput='All',
						from0='-none',
						to0='-none'
						)
		elif '_lgroups' in n.name():
			thisB = nuke.nodes.Copy(
						inputs=[curB, n],
						name='in_%s' % n.name(),
						channels='all',
						from0='-none',
						to0='-none'
						)
		elif n.name() == 'Z':
			thisB = nuke.nodes.ShuffleCopy(
						inputs=[curB, n],
						name='in_%s' % n.name(),
						out = 'depth',
						red = 'red'
						)
		else:
			thisB = nuke.nodes.ShuffleCopy(
						inputs=[curB, n],
						name='in_%s' % n.name(),
						out = n.name(),
						red = 'red',
						green = 'green',
						blue = 'blue',
						alpha = 'alpha2'
						)
		curB = thisB
	nuke.nodes.Output(inputs=[curB])


def getLightingPath():
	'''get lighting render dir from kupipeline'''
	cur_dir = nuke.script_directory()
	path = cur_dir if os.path.isdir(cur_dir) else joinPath(os.getenv('HOME'),'.nuke')
	root_split = path.split('/')
	path = '/'.join(root_split[:6])+"/lit/wip/images"
	if os.path.exists(path) == True:
		return path
	else:
		path = '/'.join(root_split[:6])
		return path


#------------------------------------------------------------------------------
#-Main function
#------------------------------------------------------------------------------


class Core_SequenceLoader(QtWidgets.QWidget):
	def __init__(self):
		super(Core_SequenceLoader, self).__init__()

		self.lgtPath_label = QtWidgets.QLabel('lighting dir: ')
		self.lgtPath = QtWidgets.QLineEdit()
		self.lgtPath.setMinimumWidth(500)
		self.lgtPath.editingFinished.connect(self.getVersions)
		self.lgtPath_btn = QtWidgets.QPushButton('Browse')
		self.lgtPath_btn.clicked.connect(self.browse)
		self.renderVersion_label = QtWidgets.QLabel("lighting ver: ")
		self.renderVersion_mu = QtWidgets.QComboBox()
		self.renderVersion_mu.setMinimumWidth(250)
		self.renderVersion_mu.setToolTip("look for dir with version number in name")
		self.renderVersion_filter_label = QtWidgets.QLabel("Filter: ")
		self.renderVersion_filter = QtWidgets.QLineEdit()
		_tip = "i.e. lgt, lookdev, anim. Seperated by commas"
		self.renderVersion_filter.setPlaceholderText(_tip)
		self.renderVersion_filter.setToolTip(_tip)
		self.renderVersion_filter.setMinimumWidth(150)
		self.renderVersion_filter.editingFinished.connect(self.getVersions)
		_completer = QtWidgets.QCompleter(['lgt', 'lookdev', 'anim'])
		self.renderVersion_filter.setCompleter(_completer)
		self.load_btn = QtWidgets.QPushButton("Load Sequence")
		self.load_btn.clicked.connect(self.SequenceLoader)
		self.file_layout = QtWidgets.QHBoxLayout()
		self.master_layout = QtWidgets.QVBoxLayout()
		self.combobox_layout = QtWidgets.QHBoxLayout()
		self.file_layout.addWidget(self.lgtPath_label)
		self.file_layout.addWidget(self.lgtPath)
		self.file_layout.addWidget(self.lgtPath_btn)
		self.combobox_layout.addWidget(self.renderVersion_label)
		self.combobox_layout.addWidget(self.renderVersion_mu)
		self.combobox_layout.addWidget(self.renderVersion_filter_label)
		self.combobox_layout.addWidget(self.renderVersion_filter)
		self.combobox_layout.addStretch(1)
		self.master_layout.addLayout(self.file_layout)
		self.master_layout.addLayout(self.combobox_layout)
		self.master_layout.addWidget(self.load_btn)
		self.master_layout.addStretch(1)
		self.setLayout(self.master_layout)
		self.setWindowTitle("Sequence Loader")

		self.setDefault()


	def setDefault(self):
		'''set default value when instancing'''
		self.lgtPath.setText(getLightingPath())
		self.getVersions()


	def run(self):
		'''run panel instance'''
		self.show()
		self.raise_()
		self.renderVersion_mu.setFocus()


	def browse(self):
		'''browse for lighting dir'''
		dir = QtWidgets.QFileDialog.getExistingDirectory(self,
			"set lighting directory",
			self.lgtPath.text(),
			QtWidgets.QFileDialog.ShowDirsOnly
		)

		if dir != None:
			self.lgtPath.setText(dir)
			self.getVersions()


	def getVersions(self):
		'''get the render versions with given lighting dir and populate combox'''
		dir_lgt = self.lgtPath.text()
		ls_excute = ['tmp', '.DS_Store']
		ls = [v for v in os.listdir(dir_lgt) if v not in ls_excute and '_v' in v]
		_filter = [f.strip() for f in self.renderVersion_filter.text().split(',')]

		ls_filtered = []
		if len(_filter)>0:
			for f in _filter:
				for i in ls:
					if f in i and i not in ls_filtered:
						ls_filtered.append(i)
		else:
			ls_filtered = ls

		self.renderVersion_mu.clear()
		if len(ls_filtered)>0:
			self.renderVersion_mu.setEnabled(True)
			self.renderVersion_mu.addItems(ls_filtered)
			self.load_btn.setEnabled(True)
			self.load_btn.setText("Load Sequence")
		else:
			self.renderVersion_mu.setEnabled(False)
			self.load_btn.setEnabled(False)
			self.load_btn.setText("NO RENDER VERSION FOUND")
			if len(ls)<=0:
				self.renderVersion_mu.addItem('NO RENDER VERSION FOUND IN DIR')
				print "\n**********\nNO RENDER VERSION FOUND IN DIR:\n%s\n**********\n" % dir_lgt
			else:
				self.renderVersion_mu.addItem("INVALID FILTER")


	def SequenceLoader(self):
		'''main function construct the image group'''

		dir_renderVersion = joinPath(self.lgtPath.text(), self.renderVersion_mu.currentText())
		dir_renderVersion = dir_renderVersion.replace("/storage/show/", "/show/")
		if dir_renderVersion == None:
			nuke.message("Import Canceled")
		else:
			name_renderVersion = os.path.basename(dir_renderVersion.rstrip('/'))
			RGBA = 'beauty'
			ls_aov = getAOVs(dir_renderVersion)
			for fp in ls_aov.keys():
				for p in ls_aov[fp]:
					nuke.Layer(p, ['%s.red' % p, '%s.green' % p, '%s.blue' % p, '%s.alpha' % p])
			for l in ls_aov.keys():
				if l == 'deep':
					aov_rest = []
					for p in ls_aov[l]:
						path = joinPath(dir_renderVersion, l, p)
						createDeepRead(path)

				else:
					imgGroup = nuke.createNode('Group', 'tile_color 0x1c2b3eff')
					imgGroup['postage_stamp'].setValue(True)
					imgGroup.setName('LitRead1')
					t_tab = nuke.Tab_Knob('tb_user', 'LitRead')
					k_pipeline = nuke.Text_Knob('kupipeline', 'LitRead', 'LitRead')
					k_renderVersion = nuke.Text_Knob('tx_version','<b>render: </b>', name_renderVersion)
					k_renderLayer = nuke.Text_Knob('tx_layer','<b>layer: </b>', l)
					k_div = nuke.Text_Knob('', "")
					k_path = nuke.Text_Knob('file','<b>path: </b>', dir_renderVersion+'/'+l+'/rm')
					mod=os.path.basename(__file__).split('.py')[0]
					k_localize = nuke.PyScript_Knob('localization', 'All Layer ReadFile Localize', '%s.Localize()' % mod)
					k_localremove = nuke.PyScript_Knob('localfile_remove', 'LocalizeFile Remove', '%s.Local_remove()' % mod)
					k_div2 = nuke.Text_Knob('', "")
					k_pulldown = nuke.Enumeration_Knob('combo_preset', 'presets', ['[Arnold] basic', '[Arnold] diffuse Lgroup', '[Arnold] specular Lgroup', '[Clarisse] basic', '[Clarisse] light group'])
					k_passout = nuke.PyScript_Knob('passout', 'Layer Comp node out', '%s.pass_out()' % mod)
					k_div3 = nuke.Text_Knob('', "")
					k_caution = nuke.Text_Knob('caution', "", '<big><b>caution!</b><big>')
					k_description = nuke.Text_Knob('description', "", '\n- normal : [Arnold] basic\n                   [Clarisse] basic\n\n- heavy : [Arnold] diffuse Lgroup / specular Lgroup\n                 [Clarisse] light group')

					k_path.setVisible(False)
					k_pipeline.setVisible(False)

					for k in [t_tab, k_pipeline, k_path, k_renderVersion, k_renderLayer, k_div, k_localize, k_localremove, k_div2, k_pulldown, k_passout, k_div3, k_caution, k_description]:
						imgGroup.addKnob(k)

					with imgGroup:
						aov_beauty = None
						aov_rest = []
						for p in ls_aov[l]:
							path = joinPath(dir_renderVersion, l, p)
							createRead(path)
						aov_beauty = nuke.toNode(RGBA)
						aov_rest = [n for n in nuke.allNodes('Read') if n != aov_beauty]
						aov_alllist = [n for n in nuke.allNodes('Read')]
						shuffling(aov_beauty, aov_rest)

					imgGroup['label'].setValue('\n'+name_renderVersion+'\n<big><b>'+l+'</b></big><small><font color=gray> / ReadNode : '+str(len(aov_alllist))+'</font></small>\n<br><b>[value first_frame]-[value last_frame]([expr [value last_frame]-[value first_frame]+1])</b><small><font color=gray> / [value width] x [value height]</font></small>')

			self.close()



#------------------------------------------------------------------------------
#-Button Functions
#------------------------------------------------------------------------------



import shutil
import os

def get_size(path='.'):
	total = 0
	for p in os.listdir(path):
		full_path = os.path.join(path, p)
		if os.path.isfile(full_path):
			total += os.path.getsize(full_path)
		elif os.path.isdir(full_path):
			total += get_size(full_path)
	return total

def Localize():
	readNode = nuke.allNodes('Read', recurseGroups=True)
	for i in readNode:
		if 'beauty' in i.name():
			localfolder = nuke.value('preferences.localCachePath')
			path = i["file"].getValue()
			pathsplit = path.split("/")
			srcpath = '/'.join(pathsplit[:11])
			localpath = '/_show/' + '/'.join(pathsplit[2:11])
			srcSize = get_size(srcpath)
			if not os.path.isdir(localfolder+localpath):
				asklocal = nuke.ask('LitRead "'+path.split("/")[-3]+'" file will start after clicking "yes"!\nWait for Message before continue!')
				if asklocal:
					shutil.copytree(srcpath, localfolder+localpath)
					localSize = get_size(localfolder+localpath)
					if srcSize==localSize:
						for R in readNode:
							R.forceUpdateLocalization()
					nuke.message('Copied sucsessfully!')
				else:
					nuke.message('Copy cancel.')
			else:
				nuke.message('Localize file already exists.')

def Local_remove():
	readNode = nuke.allNodes('Read', recurseGroups=True)
	for i in readNode:
		if 'beauty' in i.name():
			localfolder = nuke.value('preferences.localCachePath')
			path = i["file"].getValue()
			pathsplit = path.split("/")
			localpath = '/_show/' + '/'.join(pathsplit[2:11])
			if os.path.isdir(localfolder+localpath):
				asklocal = nuke.ask('Do you want to delete localize files?\n'+path.split("/")[-3])
				if asklocal:
					shutil.rmtree(localfolder+localpath)
					nuke.message('Remove sucsessfully!')
			else:
				nuke.message('File not found.')

def get_panel_options(data):
	"""
	select channel options
	"""
	p = nuke.Panel('Select AOVs')
	for opt in data:
		p.addBooleanCheckBox(opt, True)
	p.show()

	return [opt for opt in data if p.value(opt)]


# define global variables
PRESETS = {
	'[Arnold] basic': [
		'diffuse_direct', 'diffuse_indirect', 'specular',
		'coat', 'emission', 'sss', 'transmission'
	],
	'[Arnold] diffuse Lgroup': [
		['startswith', 'diffuse_LIT_{0}', 'diffuse_lit_{0}'], 'diffuse_default'
	],
	'[Arnold] specular Lgroup': [
		['startswith', 'specular_LIT_{0}', 'specular_lit_{0}'], 'specular_default'
	],
	'[Clarisse] basic': [
		'pbr_diffuse', 'pbr_emission', 'pbr_spec_gloss_reflection', 'pbr_spec_gloss_transmission', 'pbr_subsurface'
	],
	'[Clarisse] light group': [
		['startswith', 'lit_{0}']
	]
}
PRESETS_SELECTION_MODE = ['[Arnold] diffuse Lgroup', '[Arnold] specular Lgroup', '[Clarisse] light group']

def pass_out():
	thisnode = nuke.thisNode()
	preset_name = thisnode['combo_preset'].value()
	preset_role = PRESETS.get(preset_name)

	# invalid preset role or no exists input
	if not preset_role or not thisnode:
		nuke.message('Please check the preset or input.\nOtherwise, contact the TD.')
		preset_role = []
	else:
		layers = sorted(list(set([channel.split('.')[0] for channel in thisnode.channels()])))

	# group search
	if preset_name in PRESETS_SELECTION_MODE:
		condition = preset_role[0][0]
		lights = set()
		channels = thisnode.channels()
		layers = [c.split('.')[0] for c in channels]
		layers = sorted(list(set([c.split('.')[0] for c in channels])))

		if '[Arnold]' in preset_name:
			keyword1 = preset_role[0][1]
			keyword2 = preset_role[0][2]
			keyword3 = preset_role[1]
			position_keyword = -1 if preset_name == '[Arnold] diffuse Lgroup' or '[Arnold] specular Lgroup'  else 0

			# get layer name
			for layer in layers:
				if '_LIT_' in layer:
					lights.add('LIT_'+layer.split('_LIT_')[position_keyword])
				elif '_lit_' in layer:
					lights.add('lit_'+layer.split('_lit_')[position_keyword])
				lights.add(keyword3.split('_')[position_keyword])

		elif '[Clarisse]' in preset_name:
			keyword = preset_role[0][1]
			for layer in layers:
				if not layer.startswith('lit_'):
					continue
				lights.add(layer.split('_')[1])    

		preset_role = []

		if not lights:
			nuke.message('Channel does not exist.')
		else:
			for opt in get_panel_options(sorted(list(lights), key=str.lower)):
				OPT = opt.split('_')[-1]
				if 'default' in opt:
					preset_role.append(keyword3)
				elif 'LIT_' in opt:
					preset_role.append([condition, keyword1.format(OPT)])
				elif 'lit_' in opt:
					preset_role.append([condition, keyword2.format(OPT)])
				else:
					preset_role.append([condition, keyword.format(opt)])

	layers_to_query = []
	missing = []
	for role in preset_role:
		if isinstance(role, list):
			condition = role[0]
			condition_value = role[1]

		else:
			# role: matched value
			if role in layers:
				layers_to_query.append(role)
			else:
				missing.append(role)
            
			continue

		# role: condition mode
		for layer in layers:
			matched_layer = None
			if condition == 'startswith':
				if layer.startswith(condition_value):
					matched_layer = layer

			elif condition == 'endswith':
				if layer.endswith(condition_value):
					matched_layer = layer

			if not matched_layer:
				continue

			layers_to_query.append(matched_layer)

	# feedback the missing channels
	if missing:
		nuke.message('Required layer(s) is missing: \n{0}'.format(', '.join(missing)))

	thisnode = nuke.thisNode()
	dot = thisnode
	latest_node = None
	shuffle_list = []
	unpremult_list = []
	merge_list = []

	thisnode.end()

	for layer in layers_to_query:
		print '>>' + layer
		dot_xpos = 0 if dot == thisnode else 220
		dot = nuke.nodes.Dot(inputs=[dot])
		dot.setXYpos(dot.xpos()+dot_xpos, thisnode.ypos()+200)
		sf = nuke.nodes.Shuffle(label='[value in]')
		sf.setInput(0, dot)
		sf['in'].setValue(layer)
		sf['in2'].setValue('alpha')
		sf['alpha'].setValue('red2')
		sf.setYpos(sf.ypos()+100)
		shuffle_list.append(sf)

		unpremult = nuke.nodes.Unpremult()
		unpremult.setInput(0, sf)
		unpremult.setYpos(unpremult.ypos()+50)
		unpremult_list.append(unpremult)

		if latest_node:
			merge = nuke.nodes.Merge2(operation='plus', inputs=[latest_node, unpremult])
			merge_list.append(merge)
			latest_node = merge
		else:
			dot2 = nuke.nodes.Dot(inputs=[unpremult])
			dot2.setYpos(dot2.ypos()+250)
			latest_node = dot2

	if latest_node:
		if '_LIT_' in layer:
			pass
		elif '_lit_' in layer:
			pass
		else:
			# copy alpha
			dot3 = nuke.nodes.Dot(inputs=[dot])
			dot3.setXYpos(dot3.xpos()+250, thisnode.ypos()+200)
			shufflecopy = nuke.nodes.ShuffleCopy(inputs=[latest_node, dot3])
			shufflecopy['in'].setValue('alpha')
			shufflecopy['in2'].setValue('rgb')
			shufflecopy['alpha'].setValue('alpha1')
			premult = nuke.nodes.Premult()
			premult.setInput(0, shufflecopy)
			premult.setYpos(premult.ypos()+50)
			Remove = nuke.nodes.Remove()
			Remove.setInput(0, premult)
			Remove.setYpos(Remove.ypos()+50)
			Remove['operation'].setValue('keep')
			Remove['channels'].setValue('rgba')


#------------------------------------------------------------------------------
#-Instancing
#------------------------------------------------------------------------------



def runSequenceLoader():
	runSequenceLoader.Panel = Core_SequenceLoader()
	runSequenceLoader.Panel.show()
