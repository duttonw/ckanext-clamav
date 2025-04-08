from typing import Any, Optional

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig

from . import utils, config
from .job import job_virus_scan


class ClamavPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)
    p.implements(p.IResourceController, inherit=True)

    # IConfigurer

    def update_config(self, config: 'CKANConfig'):
        toolkit.add_template_directory(config, "templates")
        toolkit.add_public_directory(config, "public")
        toolkit.add_resource("fanstatic", "clamav")

    # IUploader

    def get_resource_uploader(self, data_dict: dict[str, Any]):
        if not config.is_async():
            return
        if not data_dict.get("upload"):
            return

        utils.scan_file_for_viruses(data_dict)

    def get_uploader(self, upload_to: str,
                     old_filename: Optional[str]):
        return

    # IResourceController
    def after_resource_create(self, context, resource):
        self._enqueue_if_file(resource)

    def after_resource_update(self, context, resource):
        self._enqueue_if_file(resource)

    def _enqueue_if_file(self, resource):
        if config.is_async() and resource.get('url_type') == 'upload':
            # Enqueue the task
            toolkit.enqueue_job(fn=job_virus_scan,
                                title=u"Clamav upload - Virus scan id: {}, name: {}".format(resource.id, resource.name),
                                queue=config.job_queue(),
                                args=[resource.id])
