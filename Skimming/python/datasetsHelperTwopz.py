## This class tries to simplify the functionality of the dataset helpler class which comses with a lot of scripts and becomes very static. 
## Idea is to replace the json file by standard dicts and write every functionality into this class. 

# -*- coding: UTF-8 -*-
import json,os
import re
import FWCore.ParameterSet.Config as cms

class datasetsHelperTwopz:
	def __init__(self, in_json_file ) :
		"""At the moment the in_json_file is absolut mentory, maybe lower this requierment later """
		self.base_dict = {} # start with empty dict
		self.keep_input_json = True ## Later one can overwrite the input json 
		self.json_file_name = os.path.basename(in_json_file) 
		self.json_file_path = os.path.dirname(os.path.abspath(in_json_file)) 
		self.convert_object_type = False
		if os.path.isfile(os.path.join(self.json_file_path,self.json_file_name)):
			self.read_from_jsonfile(os.path.join(self.json_file_path,self.json_file_name))
		self.convert_dict_to_nickorder() ## do this as default for now (works fine also for already converted dicts)
	def __setitem__(self, key, sub_dict):    
		if type(sub_dict) is dict:
			self.base_dict.setdefault(key, {}).update(sub_dict)
		else:
			print "you only can fill dicts into this dataset"
	def __getitem__(self, key):
		return self.base_dict.setdefault(key, {})
	def nicks(self):
		return self.base_dict.keys()

	def merge(self,new):
		newdict = new.base_dict
		self.base_dict.update(newdict)
		
	def read_from_jsonfile(self, in_json_file):
		"""Read the base_dict from input file """
		self.base_dict = json.load(open(in_json_file))  ## Maybe also add functionality to have two input files
	def write_to_jsonfile(self, out_json_file = None):
		"""Save the base_dict to a json file"""
		if not out_json_file:
			out_json_file = self.json_file_name
			if self.keep_input_json:
				out_json_file = out_json_file[:-5]+"_new.json"
		if self.json_file_path and not '/' in out_json_file:
			out_json_file =  os.path.join(self.json_file_path, out_json_file)
		if os.path.exists(out_json_file) and self.keep_input_json:
			print "I do not overwrite ",out_json_file
			return
		if not os.path.exists(out_json_file) and self.keep_input_json:
			print "Created "+out_json_file
		#~ else: 
			#~ print "Overwritten "+out_json_file
		out_json = open(out_json_file, 'w')
		out_json.write(json.dumps(self.base_dict, sort_keys=True, indent=2))
		out_json.close()
	def make_nickname(self, sample_dict):
		"""Gives the (old) structure of the nicknames """
		nick = ""
		nick += sample_dict["process"].replace("_", "")  + "_"
		nick += sample_dict["campaign"].replace("_", "") + "_"
		nick += sample_dict["scenario"].replace("_", "") + "_"
		nick += sample_dict["energy"].replace("_", "")   + "TeV_"
		nick += sample_dict["format"].replace("_", "") + ("" if (sample_dict["data"]) else "_")
		nick += sample_dict["generator"].replace("_", "")
		nick += ("_" + sample_dict["extension"] if sample_dict["extension"] != "" else "")
		return nick
	def convert_dict_to_nickorder(self): 
		"""Use the Nickname as key identifier,since all later analyse steps do so (artus, harryplotter) """
		new_dict = {}
		for akt_key in self.base_dict:
			akt_nick = self.make_nickname(self.base_dict[akt_key])
			add_sample = True
			if akt_nick in new_dict.keys():
				raise Exception('Nick: '+akt_nick+' is not unique !!!!! Breaking logic of hole analysis code\n Clean up the key:\n'+akt_key)
			new_dict[akt_nick] = self.base_dict[akt_key]
			if 'dbs' not in new_dict[akt_nick].keys(): ##In the olde convention the key was the dbs name. 
				new_dict[akt_nick]['dbs'] = akt_key ## New convention is to keep it dbs name as a subitem
		self.base_dict = new_dict
	def isSignal(self, nick):
		"""Define here what is used as Signal sample """
		if 'HToTauTau' in self.base_dict[nick]["process"] or 'H2JetsToTauTau' in self.base_dict[nick]["process"]:
			return True
		return False
	def isData(self, nick):
		"""Check if sample is data or not.  It must be given, raise an Exception is not"""
		if "data" not in self.base_dict[nick].keys():
			raise Exception('Sample with nick: '+akt_nick+' is missing the data key. ')
		return self.base_dict[nick]["data"]
	def isEmbedded(self, nick):
		"""Chekc if sample has the embedded flag and return if not. Use False als defult"""
		sub_dict = self.base_dict.get(nick) 
		return sub_dict.get("embedded", False)
	def isMiniaod(self,nick):
		"""check if inupt sample is in MINIAOD format"""   
		if "format" in self.base_dict.get(nick , {}).keys():
			return self.base_dict[nick]["format"] in ["MINIAODSIM", "MINIAOD"]
		return True ## Take it as default now

	def isreHLT(self, nick):
		"""Check if input is from reHLT campain"""
		if "campaign" in self.base_dict.get(nick , {}).keys():
			return "reHLT"  in self.base_dict[nick]["campaign"]
		return False

	def getTreeInfo(self,nick, globaltag, kappaTag):
		""" returns the Tree info which is stored in the kappa File"""    
		## not sure why all of this is needed inside of the kappa files, 
		## but to keep things consitent just add it 
		sub_dict = self.base_dict.get(nick, {}) ## now it is also posibble to run with unkown nick
		import FWCore.ParameterSet.Config as cms
		return cms.PSet(
		dataset               = cms.string(str(sub_dict.get("dbs", ''))),
		generator             = cms.string(str(sub_dict.get("generator", ''))),
		productionProcess     = cms.string(str(sub_dict.get("process", ''))),
		globalTag             = cms.string(globaltag),
		scenario              = cms.string(str(sub_dict.get("scenario", ''))),
		campaign              = cms.string(str(sub_dict.get("campaign", ''))),
		kappaTag              = cms.string(kappaTag),
		isEmbedded            = cms.bool(sub_dict.get("embedded", False)),
		centerOfMassEnergy    = cms.int32(int(sub_dict.get("energy", 13))),   
		isData                = cms.bool(sub_dict.get("data", False))
		)
	def get_nicks_with_query(self, query, pre_selected_nicks=None):
		"""match a query on the dataset which hast to be fullfilled"""
		if type(query) is not dict:
			try:
				query = json.loads(query)
			except:
				raise Exception("Can not convert ",query," into a dict")
	
		nick_list = []
		if not pre_selected_nicks:
			pre_selected_nicks = self.base_dict.keys()
		
		for akt_nick in pre_selected_nicks:
			take_nick = True
			for test_key in query.keys():
				if type(query[test_key]) in [str,unicode]:
					if not re.match( query[test_key], self.base_dict[akt_nick].get(test_key, "allways_false")):
					#if query[test_key] != self.base_dict[akt_nick].get(test_key, None):
						take_nick = False
					elif test_key not in self.base_dict[akt_nick].keys():
						take_nick = False
				else:
					if query[test_key] != self.base_dict[akt_nick][test_key]:
						take_nick = False
			if take_nick:
				nick_list.append(akt_nick)
		return nick_list

	def get_nicks_with_regex(self, nick_regex, pre_selected_nicks=None):
		""" returns all nicks (keys) which matches the nick_regex"""
		nick_list = []
		if not pre_selected_nicks:
			pre_selected_nicks = self.base_dict.keys()
		
		for akt_nick in pre_selected_nicks:
				if re.match( nick_regex, akt_nick):
					nick_list.append(akt_nick)
		return nick_list
	def get_nicks_with_tag(self, tag, tag_values=None, pre_selected_nicks=None):
		nick_list = []
		if not pre_selected_nicks:
			pre_selected_nicks = self.base_dict.keys()
		for akt_nick in pre_selected_nicks:
			take_nick = False
			if not tag_values:
				if tag in self.base_dict[akt_nick].keys():
					take_nick = True
			else:
				for test_tag_value in tag_values:
					for test_tag_vaule_dict in self.base_dict[akt_nick].get(tag, []):
						if re.match( test_tag_value, test_tag_vaule_dict):
							take_nick = True
			if take_nick:
				nick_list.append(akt_nick)
		return nick_list
	def get_nick_list(self, tag_key = None, tag_values = None,  query = None, nick_regex = None):
		nick_list = None
		if tag_key:
			nick_list = self.get_nicks_with_tag(tag=tag_key, tag_values=tag_values)
		if query:
			nick_list = self.get_nicks_with_query(query=query, pre_selected_nicks=nick_list)
		if nick_regex:
			nick_list = self.get_nicks_with_regex(nick_regex=nick_regex, pre_selected_nicks=nick_list)
		return nick_list
		
			
	def addEntry(self, entry, nick_list =[] ):
		for nick in nick_list:
			for key in entry:
				if key in self.base_dict[nick]:
					if self.base_dict[nick][key] != entry[key]:
						print "--------------WARNING--------------"
						print str(key)+' is already in Dataset.'
						print "{"+str(key)+' : '+str(self.base_dict[nick][key])+"}"+' will be overwritten by new entry '+"{"+str(key)+' : '+str(entry[key])+"}"
						print "-----------------------------------"
			self.base_dict[nick].update(entry)
		
	def addTags(self, tag_key, tag_values, nick_list =[] ):
		"""Later this tags can be used for skimming and analysis
		
		the idea is to give the samples a tag. e.g {Morriong17 : ["Skim_base","onlyDY"]}
		this means that if i want to do a base Morriong17 skim i only have to ask 
		for this tag """
		for nick in nick_list:
			#print nick,tag_values
			#self.base_dict[nick].setdefault(tag_key, []).extend(tag_values)
			self.base_dict[nick].setdefault(tag_key, []).extend(x for x in tag_values if x not in self.base_dict[nick].get(tag_key, []))
	def rmTags(self, tag_key, tag_values, nick_list =[] ):
		"""Later this tags can be used for skimming and analysis"""
		for nick in nick_list:
			if not tag_values:
				self.base_dict[nick].pop(tag_key)
			else:
				for rm_value in tag_values:
					if rm_value in self.base_dict[nick].get(tag_key,[]):
						self.base_dict[nick].setdefault(tag_key,[]).remove(rm_value)
				if len(self.base_dict[nick].get(tag_key,[])) == 0 and tag_key in self.base_dict[nick].keys():
					self.base_dict[nick].pop(tag_key)

			
	def dataset_diff_base(self, obj_A, obj_B, global_diff = {}, depth = [], test_key = None):
		""" gives the differnces of two dict conntaing subdicts 
		Not the nicest function so far, but at least it seems to work now. The idea is also to push the depth of the (sub)dict , and only fill the global diff when there is a differnces
		between a missing key, a differnces in a list or differnent values in of str,int,float,bool or unicode if you have a more elegant solution feel free to add them"""
	 # print global_diff
		#~ if type(obj_A) == unicode:
			#~ obj_A = str(obj_A)
		#~ if type(obj_B) == unicode:
			#~ obj_B = str(obj_B)
		if type(obj_A) != type(obj_B):
			if not self.convert_object_type:
				print 'Different file types detected when comparing dicts:'
				print str(obj_A)+' in new source is '+str(type(obj_A))
				print str(obj_B)+' in old source is '+str(type(obj_B))
				print 'Convert everything to <type \'str\'> for file merge? [Y/n]'
				self.wait_for_user_confirmation()
				self.convert_object_type = True		
			obj_A = str(obj_A)
			obj_B = str(obj_B)
		elif type(obj_A) == dict:
			for key in obj_A.keys():
				if key not in obj_B.keys(): ## if the key is not in b take the hole key as differnces
					local_diff = global_diff
					for akt_depth in depth:
						local_diff = local_diff.setdefault(akt_depth,{})
					local_diff.setdefault(test_key,{})[key]  = obj_A[key]
						#local_diff[test_key]  = obj_A
				else: ## prepare to check the subitem
					adddepth = list(depth)
					if test_key:
						adddepth.append(test_key)
					self.dataset_diff_base(obj_A[key],obj_B[key],global_diff,adddepth,key)
		elif type(obj_A) == list:
			diff_list = []
			for akt_element in obj_A:
				if akt_element not in obj_B:
					diff_list.append(akt_element)
					if len(diff_list)>0:
						local_diff = global_diff
						for akt_depth in depth:
							local_diff = local_diff.setdefault(akt_depth,{})
						local_diff[test_key] = diff_list
		
		elif type(obj_A) in [str,int,float,bool,unicode]:
				if obj_A != obj_B:
					local_diff = global_diff
					for akt_depth in depth:
						local_diff = local_diff.setdefault(akt_depth,{})
					local_diff[test_key] = obj_A
		else:
			print "something else ",type(obj_A)," ",obj_A
	def dataset_diff_onlyinthis(self, dataset):
		diff_dict = {}
		self.dataset_diff_base(self.base_dict,dataset.base_dict,diff_dict)
		return json.dumps(diff_dict, sort_keys=True, indent=2)
	def dataset_diff_notinthis(self, dataset):
		diff_dict = {}
		self.dataset_diff_base(dataset.base_dict,self.base_dict,diff_dict)
		return json.dumps(diff_dict, sort_keys=True, indent=3)		

	@classmethod
	def wait_for_user_confirmation(self,true_false=False):
		choice = raw_input().lower()
		if choice in set(['yes','y','ye', '']):
			if true_false:
				return True
			pass
		elif choice in set(['no','n']):
			if true_false:
				return False
			exit()
		else:
			sys.stdout.write("Please respond with 'yes' or 'no'")

