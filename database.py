import sqlite3
from pathlib import Path

import pandas as pd
from intake_esgf import ESGFCatalog


def create_cv_universe(path: Path, ingest_data: list[tuple[str, str, str]]) -> None:
    """Create a SQLite database."""
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    if not path.is_file():
        cur.execute("""
    CREATE TABLE Collections(
    CollectionId   INTEGER PRIMARY KEY, 
    CollectionName TEXT NOT NULL,
    ProjectName    TEXT NOT NULL,
    UNIQUE(CollectionName, ProjectName)
    );""")
        cur.execute("""
    CREATE TABLE Terms(
    TermId    INTEGER PRIMARY KEY, 
    TermName  TEXT NOT NULL,
    CollectionId INTEGER NOT NULL,
    FOREIGN KEY(CollectionId) REFERENCES Collections(CollectionId),
    UNIQUE(TermName, CollectionId) 
    );""")
    for term, collection, project in ingest_data:
        # Try to insert a new category, ignore if already present
        cur.execute(
            f"INSERT INTO Collections (CollectionId,CollectionName,ProjectName) VALUES (NULL,'{collection}','{project}') ON CONFLICT DO NOTHING"
        )
        # Get the collection id so we can insert the term
        collection_id = cur.execute(
            f"SELECT CollectionId FROM Collections WHERE CollectionName='{collection}' AND ProjectName='{project}'"
        ).fetchone()
        assert len(collection_id) == 1
        # Now insert the term
        cur.execute(
            f"INSERT INTO Terms (TermId,TermName,CollectionId) VALUES (NULL,'{term}','{collection_id[0]}') ON CONFLICT DO NOTHING"
        )
        con.commit()

    df = pd.read_sql_query(
        """
SELECT TermName, CollectionName, ProjectName
FROM Terms 
  INNER JOIN Collections 
  ON Terms.CollectionId = Collections.CollectionId
ORDER BY ProjectName;""",
        con,
    )
    print(df)
    cur.close()
    con.close()


# just an incomplete test
for search in [
    dict(
        project="CMIP6",
        member_id="r1i1p1f1",
        experiment_id="ssp585",
        frequency="mon",
    ),
]:
    cat = ESGFCatalog().search(**search)
    create_cv_universe(
        Path("test.db"),
        [
            (term, collection, search["project"])
            for collection, terms in cat.unique().to_dict().items()
            for term in terms
        ],
    )
