import click
from virtual_hospital import app, db


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create tables after dropping existing ones.')
def dbinit(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')
