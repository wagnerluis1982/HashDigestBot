import re


def hashtags(text):
    tags = set()
    for s in text.split():
        if "#" in s:
            s = re.sub(r"^[^\w#_]+", "", s)
            if s.startswith("#"):
                s = re.sub(r"^#+", "", s)
                if "#" not in s:
                    m = re.match(r"\w+", s)
                    if m:
                        tags.add(m.group(0))
    return tags
