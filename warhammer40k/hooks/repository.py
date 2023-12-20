from typing import Optional

import requests
from cement import App

from db.schemas import Repository
from db.tables import Repositories


def fetch_repositories(app: App):
    app.log.debug("Updating repositories")

    feed_url = app.config.get("warhammer40k", "feed")["repositories_url"]

    response = requests.get(feed_url)
    try:
        response.raise_for_status()
        assert "tree" in response.json()
    except (requests.exceptions.HTTPError, AssertionError) as exc:
        app.log.error(
            f"Unable to update feed, running with known repositories (error: {exc})"
        )
        return

    dict_repositories = [
        Repository(
            name=entry["path"][:-4],
            url=f'{Repository.URL_BASE}{entry["path"]}',
            sha=entry["sha"],
        )
        for entry in response.json()["tree"]
        if entry["path"].endswith(".cat")
    ]

    updated = []
    table: Repositories = app.repositories
    for repository in dict_repositories:
        db_repository: Optional[Repository] = table.get(doc_id=repository.doc_id)
        if not db_repository or db_repository.sha != repository.sha:
            try:
                inserted = table.upsert(repository.load("write").to_document())
                updated.append(inserted)
            except requests.exceptions.HTTPError as exc:
                app.log.warning(
                    f"Unable to fetch {repository.name} repository (reason: {str(exc)})"
                )

    app.log.debug(f"{len(updated)} repositories fetched")
