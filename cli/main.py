import threading
import asyncio


import click


from safer.safe import Safer


nb_copies_done = 0

@click.command()
@click.option('-d', '--delta', default=10, help='Number of minutes between copies.')
@click.option('-s', '--safe_dir', default=None, help='Destination folder.')
@click.option('-w', '--delicate_dirs', required=True, help='Folder to save.')
@click.option('-n', '--count', default=0, help='Number of iterations.')
@click.option('-t', '--type', help='copy or filter or update.')
@click.option('--extentions', default='', help='extention to exclude separeted by comma (pdf, txt...) (not when type is copy)')
@click.option('--dirpath', default='', help='A path to exclude (not when type is copy)')
@click.option('--dirname', default='', help='A folder name to exclude (not when type is copy)')
def scan(delta, safe_dir, delicate_dirs, count, type, extentions, dirpath, dirname):
    config = {
        'timedelta': delta,
        'safe_dir': safe_dir,
        'delicate_dirs': [delicate_dirs],
        'advanced': True, # disable MAX_DIR_SIZE limit
        # Exclusion rules:
        'dirname': [dirname],
        'dirpath': [dirpath],
        'filename': [],
        'extention': extentions.split(','),
        # other options
        'local_path': '',
        'external_path': ''
    }

    loop = asyncio.get_event_loop()

    safer = Safer(config=config)

    if type == 'filter':
        func = lambda: safer.save_with_filters(loop)
    elif type == 'copy':
        func = safer.copy_files
    elif type == 'update':
        func = lambda: safer.update(loop)
    else:
        func = lambda: safer.save_with_filters(loop)

    def perpetual_scan():
        global nb_copies_done
        func()
        nb_copies_done += 1
        if nb_copies_done < count or count == 0:
            timer = threading.Timer(delta, perpetual_scan)
            timer.start()

    delta *= 60
    perpetual_scan()
