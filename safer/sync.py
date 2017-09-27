#!/usr/bin/python3

class Sync(object):
    def __init__(self):
        super(Sync, self).__init__()

	def compare(self, local_path, external_path):
		"""
		Il faudrait une fenetre avec 3 onglets :
			- fichiers a copier : qui manquent dans la destination
			- fichiers a supprimer : qui ne sont plus dans la source
			- fichier a mettre a jour : qui sont déjà dans la destination et qui sont nouveau
				(ici attention il faut garder les fichiers les plus recents)
		... et on pourrait choisir quel fichier copier/supprimer/mettre a jour.
		Une option Garder les fichiers de la destination qui ne sont plus dans la sources.
		Une option Garder le dernier fichier (pour les fichiers presents dans la source et la destination).

		"""
		self.logger.info('Start comparing')

		self.get_to_save(path_delicate)
		local_dirs = self.dirs_to_make
		locals_files = self.list_files

		self.get_to_save(safe_path_last)
		external_dirs = self.dirs_to_make
		external_files = self.list_files

		# Get new folders
		dirs_to_make = missing_item(local_dirs, external_dirs)

		# Get new files
		to_copy = missing_item(locals_files, external_files)

		# Get existing files in safe path
		to_update = combine_list(locals_files, external_files)

		# Get old files
		to_del = missing_item(locals_files, external_files)

		# Get old folders, to be deleted
		# dirs_to_del: directories copied, deleted in delicate drectory -> to delete from safe directory
		# Get the directory tree
		dirs_to_del = missing_item(dirs_maked, dirs_to_save)

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()

		results = dict()
		results['dirs_to_make'] = dirs_to_make
		results['dirs_to_del'] = dirs_to_del
		results['to_copy'] = to_copy  # files
		results['to_update'] = to_update  # files
		results['to_del'] = to_del  #files
		return results

	def execute(self, orders, path_delicate):
		print('safer execute')
		print(path_delicate)
		print(orders)
		safe_path_last = self.safe_dirs[path_delicate]
		for dirname in orders['dirs_to_make']:
			dirpath = path.join(safe_path_last, dirname)
			self.logger.info('Make directory: ' + dirpath)
			mkdir(dirpath)
		self.save_files(orders['to_copy'], safe_path_last, path_delicate)
		self.update_files(orders['to_update'], safe_path_last, path_delicate)
		self.remove_files(orders['to_del'], safe_path_last)
		for dirname in orders['dirs_to_del']:
			dirpath = path.join(safe_path_last, dirname)
			self.logger.info('Remove tree: ' + dirpath)
			try:
				rmtree(dirpath)
			except FileNotFoundError:
				pass  # Directory already removed

		self.logger.info('Done')
		self.safe_dirs = self.get_dst_path()  # perhap update just the dst path of given path_delicate
