from Products.Five import BrowserView


class Create(BrowserView):
    def __call__(self):
        """
        This view redirects to the subticket form and has been inspired by the
        `createObject` script which was used before this view was in place.
        """
        type_name = 'SubTicket'
        subticket_id = self.context.generateUniqueId(type_name)
        new_url = 'portal_factory/{0}/{1}/edit?ticket={2}'.format(
            type_name,
            subticket_id,
            self.request.get('ticket'),
        )
        self.request.response.redirect(new_url)
