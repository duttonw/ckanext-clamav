import logging
from typing import Optional

from ckan.plugins import toolkit as tk
from . import utils
log = logging.getLogger(__name__)


def job_virus_scan(resource_id):
    """
    Callback to scan the resource file previously uploaded.

    If an item is found, it will email the sysAdmin as well as package owner (if set) of the infected dataset/resource
    It will try and mark the Dataset (or resource) as Private to stop general public access (Config controlled)
    If iUploader delete function is available, it will delete the file. (Config controlled)

    """
    context = {"ignore_auth": True}
    try:
        data_dict = tk.get_action('resource_show')(context, {"id": resource_id})
    except tk.ObjectNotFound:
        log.error('Resource %s does not exist.', resource_id)
        return
    # todo: make a new entry point since the file is now not in the dict but from the url link.

    file = data_dict.get('url')  # todo: convert to file on disk or work out how to get clamav to scan it (may need api key)
    status: str
    signature: Optional[str]
    status, signature = utils._scan_filestream(file)
    # todo: check status code and signature
    #  if to big, then email sysadmin only no other action, same for disabled.
    #  if virus/malware found:
    #  email sysadmin + package owner
    #  config controlled mark dataset/resource private
    #  config controlled delete file if able to
    return
