from click import argument, command, option


@command()
@argument("rootdir")
@option("--link", is_flag=True)
def dupes(rootdir, link):
    if link:
        print(f'I will link files in {rootdir}')
