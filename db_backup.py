# 0 */6 * * * /home/ubuntu/SelfLRC/selfLrc/.venv/bin/python3 /home/ubuntu/SelfLRC/selfLrc/db_backup.py

from datetime import datetime as dt
timestamp = dt.now().strftime('%Y%m%d_%H%M%S')
backup_file_name = f'db-{timestamp}.sqlite3'

import os, sys
basedir=os.path.dirname(os.path.abspath(__file__))

from dotenv import load_dotenv
load_dotenv(basedir+'/.env')

to_backup=basedir+"/self_lrc/db.sqlite3"

import hashlib
def get_file_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in 64k chunks
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

last_md5_file="/tmp/selflrc.last"
last_md5=""
if os.path.exists(last_md5_file): last_md5=open(last_md5_file).read()
current_md5= get_file_checksum(to_backup)
if current_md5==last_md5: 
    print("nth changed. skipping backup")
    sys.exit(0)
with open(last_md5_file, 'w') as f: f.write(current_md5)

from b2sdk.v1 import B2Api
b2_api = B2Api()
b2_api.authorize_account("production", os.getenv('application_key_id'), os.getenv('application_key'))
bucket = b2_api.get_bucket_by_name("selfLrc")

bucket.upload_local_file(
    local_file=to_backup,
    file_name='db/'+backup_file_name,
)

