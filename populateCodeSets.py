import os
import requests
from datetime import datetime
from time import sleep
import csv

def get_n3c_recommended_codeset_ids() -> list:
    url = "https://termhub.azurewebsites.net/get-n3c-recommended-codeset_ids"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve N3C recommended codeset ids. Status code: {response.status_code}")
        return
    return response.json()

def get_all_csets() -> list:
    url = "https://termhub.azurewebsites.net/get-all-csets"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve code sets. Status code: {response.status_code}")
        # Get list of all csets
    return response.json()

def get_csets_details(codeset_id: int) -> list:
    url = f"https://termhub.azurewebsites.net/get-csets?codeset_ids={codeset_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve concept set details for codeset_id: {codeset_id}. Status code: {response.status_code}")
        return
    return response.json()[0]

def get_csets_items(codeset_id: int) -> list:
    url = f"https://termhub.azurewebsites.net/cset-download?codeset_id={codeset_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve concept set items for codeset_id: {codeset_id}. Status code: {response.status_code}")
        return
    return response.json()

def get_researcher_details(researcher_query_fragment: str) -> list:
    url = f"https://termhub-dev.azurewebsites.net/researchers?ids={researcher_query_fragment}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve researcher details. Status code: {response.status_code}")
        return
    return response.json()

def write_codeset_items(
        detailed_codeset: dict,
        csets_items_fields: list,
        csets_concept_fields: list
    ) -> None:
    cset = detailed_codeset
    csets_items = get_csets_items(cset['codeset_id'])
    with open("codeset_item.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if not csets_items:
            print(f"Unable to retrieve csets_items for codeset_id: {cset['codeset_id']}")
            row = [cset['codeset_id'], "Access Error"] + [""] * (len(csets_items_fields) + len(csets_concept_fields))
            writer.writerow(row)
            return
        for item in csets_items['items']:
            row = [cset['codeset_id'], cset["n3c_recommended"]] + [item[field] for field in csets_items_fields] + [item['concept'][field] for field in csets_concept_fields]
            writer.writerow(row)

def add_csets_details(
        cset: dict,
        n3c_recommended_codeset_ids: list,
        csets_details_fields: list
    ) -> list:
    codeset_id = cset["codeset_id"]
    if codeset_id not in n3c_recommended_codeset_ids:
        cset["n3c_recommended"] = "false"
    else:
        cset["n3c_recommended"] = "true"
    cset_details = get_csets_details(codeset_id)
    for field in csets_details_fields:
        cset[field] = str(cset_details[field]).replace('\n', '').replace('\t', '')
    return cset

def write_run_metadata_entry() -> None:
    if not os.path.exists("run_metadata.csv"):
        with open("run_metadata.csv", "w") as f:
            f.write("run_start_datetime\n")

    # Get the date and time of the run
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Write the date and time to the run metadata file
    with open("run_metadata.csv", "a") as f:
        f.write(f"{date} {time}\n")

def get_codeset_ids_with_existing_items() -> list:
    if not os.path.exists("codeset_item.csv"):
        return []
    with open("codeset_item.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        codeset_id_index = header.index("codeset_id")
        codeset_ids = [row[codeset_id_index] for row in reader]
    return list(set(codeset_ids))

def main():

    write_run_metadata_entry()
    n3c_codeset_ids = get_n3c_recommended_codeset_ids()
    codesets = get_all_csets()
    has_items = get_codeset_ids_with_existing_items()
    overwrite = False

    csets_items_fields = [
        "includeDescendants", "includeMapped", "isExcluded"
    ]
    csets_concept_fields = [
        "CONCEPT_ID"
    ]
    csets_details_fields = [
            "concept_set_version_title",
            "project",
            "concept_set_name",
            "alias",
            "source_application",
            "source_application_version",
            "codeset_created_at",
            "is_most_recent_version",
            "version",
            "comments",
            "codeset_intention",
            "limitations",
            "issues",
            "update_message",
            "codeset_status",
            "has_review",
            "reviewed_by",
            "codeset_created_by",
            "provenance",
            "atlas_json_resource_url",
            "parent_version_id",
            "authoritative_source",
            "is_draft",
            "codeset_rid",
            "project_id",
            "assigned_informatician",
            "assigned_sme",
            "container_status",
            "stage",
            "container_intention",
            "n3c_reviewer",
            "archived",
            "container_created_by",
            "container_created_at",
            "omop_vocab_version",
            "container_rid",
            "distinct_person_cnt",
            "total_cnt",
            "total_cnt_from_term_usage",
            "concepts",
            "container_creator",
            "codeset_creator"
        ]
    csets_researchers_fields = [
        "emailAddress",
        "institution",
        "name",
        "orcidId",
        "signedDua",
        "institutionsId",
        "citizenScientist",
        "multipassId",
        "unaPath",
        "internationalScientistWithDua",
        "rid",
    ]

    if (overwrite or not has_items):
        with open("codeset_item.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["codeset_id", "n3c_recommended"] + csets_items_fields + csets_concept_fields)
        with open("codeset.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["codeset_id", "n3c_recommended"] + csets_details_fields)

    for i, cset in enumerate(codesets):
        print("Updating details for codeset_id: ", cset["codeset_id"], "(", i + 1, "of", len(codesets),  ")", end=" ")
        detailed_cset = add_csets_details(cset, n3c_codeset_ids, csets_details_fields)
        sleep(.5)
        if (str(cset["codeset_id"]) not in has_items):
            write_codeset_items(detailed_cset, csets_items_fields, csets_concept_fields)
            sleep(1)
        else:
            print("Skipping items for codeset_id: ", cset["codeset_id"])
        with open("codeset.csv", "a", newline='') as f:
            writer = csv.writer(f)
            row = [cset["codeset_id"], cset["n3c_recommended"]] + [cset[field] for field in csets_details_fields]
            writer.writerow(row)
        print("...", end=" ")
        print("Done")

    # Get researcher information
    
    with open("codeset.csv", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        codeset_created_by_index = header.index("codeset_created_by")
        container_created_by_index = header.index("container_created_by")
        researchers = set()
        for row in reader:
            codeset_created_by = row[codeset_created_by_index]
            container_created_by = row[container_created_by_index]
            if codeset_created_by:
                researchers.add(codeset_created_by)
            if container_created_by:
                researchers.add(container_created_by)
    researcher_query_fragment = '&ids='.join(researchers)
    researcher_details = get_researcher_details(researcher_query_fragment)
    with open("researcher.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["researcher_id"] + csets_researchers_fields)
        for researcher in researchers:
            writer.writerow([researcher] + [researcher_details[researcher][field] if field in researcher_details[researcher].keys() else None for field in csets_researchers_fields])
            
if __name__ == "__main__":
    main()