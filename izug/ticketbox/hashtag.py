import re

HASH_TAG_RE = re.compile(r"#(\w+)")


def create_hash_tag_links(text, base_url):
    def create_link(matchobj):
        return '<a href="%(base_url)s/@@dms/%(docid)s">%(hashtag)s</a>' % dict(
            base_url=base_url,
            hashtag=matchobj.group(0),
            docid=matchobj.group(1),
        )
    return HASH_TAG_RE.sub(create_link, text)
