#!/usr/bin/env python3
'''
Use lbrytools to download data from the specified channel.

NOTE: You need to install lbrytools from here:
    https://github.com/belikor/lbrytools

You can create a virtual env and then just copy the whole git dir
inside lib/python3.X/site-packages

This abuses the default sort order of the results from
lbrytools.ch_download_latest(), which sorts on the timestamps.
So just find the number of entries with a timestamp later than the ts
you want using lbrytools.ch_search_n_claims(), then call
lbrytools.ch_download_latest() for that many entries.
'''
from datetime import datetime
from typing import Optional
import lbrytools as lt
import os, sys, argparse, shutil, patoolib

cwd = "C:\\Users\\HostsServer\\Downloads\\p2aup"

channels_list = ['@AreWeCoolYet:7']

# Globals:
MAX_SEARCH_CLAIMS = 10000
SERVER = 'http://localhost:5279'
TS_FORMAT = '%Y-%m-%d'


def find_num_downloads(channel: str, dt: datetime) -> int:
    '''
    Search a channel for the number of claims since a specified datetime.
    '''
    def _filter_claims_by_date(x):
        '''
        Filter the claims by their date.
        Compare with dt.
        '''
        return datetime.fromtimestamp(
                int(x['meta']['creation_timestamp']), # Unix ts
            ) > dt
    try:
        all_claims = lt.ch_search_n_claims(channel,
                                           number=MAX_SEARCH_CLAIMS,
                                           server=SERVER).get('claims')
        return len(list(filter(_filter_claims_by_date, all_claims)))
    except (TypeError, KeyError, ValueError):
        # Our search fucked up. We can potentially try
        # to handle it here, but for now just immediately raise it.
        raise



def _download(channel: str,
              max_downloads: int,
              download_path: Optional[str] = None) -> None:
    '''
    Download a channel, grabbing all claims newer than download_date,
    that aren't in the dowload_path already.
    '''
    lt.ch_download_latest(
        channel=channel,
        number=max_downloads,
        ddir=download_path,
        save_file=True,
        server=SERVER
    )


def download_channel(channel: str,
                     download_date: datetime,
                     download_path: Optional[str] = None) -> None:
    '''
    Download a channel. First fetch info on the number of downloads we should
    be doing using find_num_downloads(), then run the download process
    with _download().
    '''
    num_downloads = find_num_downloads(channel, download_date)
    print(f'Found {num_downloads} uploads from {channel}')
    _download(channel, num_downloads, download_path)

def remove_dup_folders(rm_folder):
    dirs = [ name for name in os.listdir(rm_folder) if os.path.isdir(os.path.join(rm_folder, name)) ]

    # detect if the subdirectory has same name as parent directory if it does move it to the parent directory
    for dir in dirs:
        folder = os.path.join(rm_folder, dir)
        folders = [ name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name)) ]
        for subfolder in folders:
            if subfolder == os.path.basename(folder):
                shutil.move(os.path.join(folder, subfolder), folder+'_p2aup1')
                shutil.rmtree(folder,ignore_errors=True)
                os.rename(folder+'_p2aup1', folder)


def extract_archives(root_path):
    for file in os.listdir(root_path):
        name, ext = os.path.splitext(file)
        out_path = f'{root_path}{os.path.sep}{name}'
        if ext == 'rar':
            print(file)
            patoolib.extract_archive(os.path.join(root_path, file), outdir=out_path)
            #remove_dup_folders(out_path)
            #os.remove(os.path.join(root_path, file))


def main() -> None:
    '''
    Argument parser and main function.
    '''
    parser = argparse.ArgumentParser(description='Run a fetch of a LBRY channel')
    parser.add_argument('-p', '--path', dest='path',
                        type=str, required=False)
    parser.add_argument('-d', '--after-date', dest='after_date',
                        type=str, required=False)
    args = parser.parse_args()
    if not args.path:
        download_path = cwd
    else:
        download_path = args.path
    if not args.after_date:
        dt = datetime.fromtimestamp(0)  # First unix timestamp
    else:
        try:
            dt = datetime.strptime(args.after_date, TS_FORMAT)
        except (TypeError, ValueError) as err:
            print(f'INVALID date: {args.after_date}')
            print(f'Use timestamp format: {TS_FORMAT}')
            print(f'Exception caught: {repr(err)}')
            sys.exit(1)
    print(f'Downloading from {dt} to current time')
    print(f'Downloading to {download_path}')
    print(f'Downloading from a total of {len(channels_list)} channels')
    for channel_name in channels_list:
        try:
            print(f'Downloading from {channel_name}...')
            download_channel(channel_name, dt, download_path)
        except (TypeError, ValueError, KeyError) as err:
            print(f'Caught exception while downloading channel {channel_name}')
            print(f'Exception caught: {repr(err)}')
            sys.exit(1)
    print(f"Extracting Archives...")
    #extract_archives(download_path)
    print('done')
    sys.exit(0)


if __name__ == '__main__':
    main()
