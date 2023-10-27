"""
Requires:
    context > hostName
    context > appName
    context > appLabel
    context > comment
    context > projectName
    context > ftrackSession
    instance > ftrackIntegratedAssetVersionsData
    instance > batch_name
"""

import sys
import copy

import six
import pyblish.api
from openpype.lib import StringTemplate
import ftrack_api


class RVXIntegrateDeliveryPlaylist(pyblish.api.InstancePlugin):
    """Create delivery playlist in Ftrack."""

    # Must be after integrate asset new
    order = pyblish.api.IntegratorOrder + 0.4999
    label = "[RVX] Integrate delivery list"
    families = ["ftrack"]
    optional = True
    settings_category = "ftrack"
    only_for_families = ["delivery"]

    def create_delivery_list(self, session, instance, list_name):
        project_entity = instance.context.data.get("ftrackProject")
        list_category = session.query(
            "ListCategory where name is Deliveries"
        ).one()
        delivery_list = session.create(
            "AssetVersionList",
            {
                "project": project_entity,
                "category": list_category,
                "name": list_name
            }
        )
        session.commit()
        return delivery_list

    def process(self, instance):
        # Check if there are any integrated AssetVersion entities
        asset_versions_key = "ftrackIntegratedAssetVersionsData"
        asset_versions_data_by_id = instance.data.get(asset_versions_key)
        if not asset_versions_data_by_id:
            self.log.info("There aren't any integrated AssetVersions, aborting.")
            return

        context = instance.context
        project_entity = instance.context.data.get("ftrackProject")

        session = context.data["ftrackSession"]

        delivery_list_name = instance.data["batch_name"]

        # first try and fetch the existing delivery list
        try:
            self.log.debug('List Query: {}'.format('AssetVersionList where name is %s and project.id is %s' % (delivery_list_name, project_entity['id'])))
            delivery_list = session.query('AssetVersionList where name is %s and project.id is %s' % (delivery_list_name, project_entity['id'])).one()
        except ftrack_api.exception.NoResultFoundError:
            try:
                delivery_list = self.create_delivery_list(session, instance, delivery_list_name)
            except Exception as err:
                self.log.error(f"Could not create delivery list! {err}")
                return

        for asset_version_data in asset_versions_data_by_id.values():
            asset_version = asset_version_data["asset_version"]
            try:
                # when we have a and b versions we are referencing the same version - so we run into this
                self.log.info(f"adding version [{asset_version['id']}] to {delivery_list_name}")
                delivery_list['items'].append(asset_version)
                session.commit()
            except ftrack_api.exception.DuplicateItemInCollectionError:
                self.log.warning("Ignoring duplicate entry error for [%s]" % instance.data["name"])
