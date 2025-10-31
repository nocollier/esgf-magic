import importlib
import json
from typing import Literal, Optional

import typer
import yaml

import esgf_magic as esm

app = typer.Typer(
    name="esm",
    no_args_is_help=True,
    add_completion=False,
)


@app.command(
    help="Build an ESGF faceted search by specifying terms in the control vocabular universe.",
)
def query(
    terms: list[str],
    project: Optional[str] = None,
    regen_database: bool = False,
    format: Literal["pandas", "json", "yaml"] = "pandas",
):
    database_file = importlib.resources.files("esgf_magic.data") / "esgf_cv_universe.db"
    if regen_database and database_file.is_file():
        database_file.unlink()
    if not database_file.is_file():
        yaml_file = (
            importlib.resources.files("esgf_magic.data") / "database_facets.yaml"
        )
        with open(yaml_file) as fin:
            facets_by_project = yaml.safe_load(fin)
        esm.ingest_by_facet_query(database_file, facets_by_project)
    out = esm.query_cv_universe(database_file, terms, project)
    if format == "pandas":
        print(out.to_string())
    else:
        out = esm.query_df_to_dict(out)
        if format == "json":
            print(json.dumps(out))
        elif format == "yaml":
            print(yaml.dump(out))
        else:
            raise ValueError("Unknown output format.")


if __name__ == "__main__":
    app()
