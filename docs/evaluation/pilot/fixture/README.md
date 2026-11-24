# Report summmary

A small synthetic report module. No external services or data are involved.

`total(rows)` returns the sum of integer amounts in the supplied rows.

`can_read(row, viewer)` permits public rows (the flag must be literally true). All other rows require the viewer and owner to be non-empty string identifiers that match exactly. An absent owner does not grant access.
