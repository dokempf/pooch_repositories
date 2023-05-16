import json
import os
import requests
import tqdm
import xmltodict


def scrape_re3data():
    # Get the full list of data repositories from RE3DATA
    repodata = requests.get(
        "https://www.re3data.org/api/v1/repositories"
    ).content.decode()
    repolist = xmltodict.parse(repodata)["list"]["repository"]

    # Scrape the repo information from RE3DATA
    data = []
    for repo in tqdm.tqdm(repolist):
        repodata = requests.get(
            f"https://www.re3data.org/api/v1/repository/{repo['id']}"
        ).content.decode()
        data.append(xmltodict.parse(repodata))

    # Distill the software information from the raw data
    softwaredb = {}
    for sample in data:
        if "r3d:software" in sample["r3d:re3data"]["r3d:repository"]:
            software = sample["r3d:re3data"]["r3d:repository"]["r3d:software"]
            if not isinstance(software, list):
                software = [software]
                if software != "unknown":
                    if not isinstance(software, list):
                        software = software

                for sw in software:
                    name = sw["r3d:softwareName"]
                    if name in ["unknown", "other"]:
                        continue

                    softwaredb.setdefault(name, [])
                    softwaredb[name].append(
                        sample["r3d:re3data"]["r3d:repository"]["r3d:repositoryURL"]
                    )

    # Dump softwaredb into a JSON file
    with open(
        os.path.join(os.path.dirname(__file__), "data", "re3data_software.json"), "w"
    ) as f:
        json.dump(softwaredb, f)


if __name__ == "__main__":
    scrape_re3data()
