# Permissions used by Poi

from Products.CMFCore import permissions as CMFCorePermissions

View                      = CMFCorePermissions.View
ModifyPortalContent       = CMFCorePermissions.ModifyPortalContent
AccessContentsInformation = CMFCorePermissions.AccessContentsInformation

EditResponse              = "izug.ticketbox: Edit response"

CMFCorePermissions.setDefaultRoles(EditResponse, ['Manager'])
