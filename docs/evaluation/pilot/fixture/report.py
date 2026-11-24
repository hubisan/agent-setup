"""Small synthetic report example for the ACS pilot."""


def total(rows):
    return sum(row["amount"] for row in rows)


def can_read(row, viewer):
    return row.get("public") or row.get("owner") == viewer
