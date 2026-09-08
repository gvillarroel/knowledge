"""Supervise the frozen ordered campaign; stop immediately on any failed phase."""
import json
import subprocess
import sys
import time

from prepare import HERE, WORK, write


def main():
    phases = [('launch.py','development'),('launch.py','joint'),('finalize.py','freeze'),
              ('launch.py','recalculation'),('finalize.py','release'),
              ('launch.py','validation'),('finalize.py','close')]
    write(WORK/'pipeline-start.json',{'phases':phases,'automatic_retries':0})
    for number,(script,phase) in enumerate(phases):
        start = time.monotonic()
        result = subprocess.run([sys.executable,'-B',str(HERE/script),phase],check=False)
        record = {'phase':phase,'script':script,'exit_code':result.returncode,
                  'seconds':time.monotonic()-start}
        write(WORK/'pipeline'/(f'{number:02d}-'+phase+'.json'),record)
        print(json.dumps(record),flush=True)
        if result.returncode:
            raise RuntimeError('Campaign stopped; preserve failed phase before recovery review')
    write(WORK/'pipeline-complete.json',{'status':'native-campaign-complete-publication-pending'})


if __name__ == '__main__':
    main()
