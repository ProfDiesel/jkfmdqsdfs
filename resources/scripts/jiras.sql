        # connection.execute(f"""CREATE INDEX {table}_version ON {table} semvercollation(json_extract(payload, '$.fix_version'));""")
        # connection.execute(f"""CREATE INDEX {table}_kind ON {table} json_extract(payload, '$.kind'));""")
