"""Monkeypatch pooch to take into account other data repositories

This should be entirely rewritten when there is a public interface to
modify the chain of responsibility for data repository resolution.
"""

from pooch_repositories.dispatch import Re3dataDispatchRepository
from pooch.downloaders import ZenodoRepository, FigshareRepository, doi_to_url
from pooch.utils import parse_url

# The module to patch
import pooch.downloaders as pd


# This is the data
chain_of_responsibility = [
    Re3dataDispatchRepository,
    ZenodoRepository,
    FigshareRepository,
]


def patched_doi_to_repository(doi):
    """
    Instantiate a data repository instance from a given DOI.

    This function implements the chain of responsibility dispatch
    to the correct data repository class.

    Parameters
    ----------
    doi : str
        The DOI of the archive.

    Returns
    -------
    data_repository : DataRepository
        The data repository object
    """

    # This should go away in a separate issue: DOI handling should
    # not rely on the (non-)existence of trailing slashes. The issue
    # is documented in https://github.com/fatiando/pooch/issues/324
    if doi[-1] == "/":
        doi = doi[:-1]

    repositories = chain_of_responsibility

    # Extract the DOI and the repository information
    archive_url = doi_to_url(doi)

    # Try the converters one by one until one of them returned a URL
    data_repository = None
    for repo in repositories:
        if data_repository is None:
            data_repository = repo.initialize(
                archive_url=archive_url,
                doi=doi,
            )

    if data_repository is None:
        repository = parse_url(archive_url)["netloc"]
        raise ValueError(
            f"Invalid data repository '{repository}'. "
            "To request or contribute support for this repository, "
            "please open an issue at https://github.com/fatiando/pooch/issues"
        )

    return data_repository


# Do the monkeypatching
pd.doi_to_repository = patched_doi_to_repository
