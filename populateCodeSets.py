import os
import sys
import requests
from datetime import datetime
import time
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

def update_csets_file(
        all_csets: list,
        n3c_recommended_codeset_ids: list,
        csets_items_fields: list,
        csets_concept_fields: list,
        csets_details_fields: list
    ) -> None:
    for cset in all_csets:
        print("Updating details for codeset_id: ", cset["codeset_id"], end=" ")
        codeset_id = cset["codeset_id"]
        if codeset_id not in n3c_recommended_codeset_ids:
            cset["n3c_recommended"] = "false"
        else:
            cset["n3c_recommended"] = "true"
        cset_details = get_csets_details(codeset_id)
        for field in csets_details_fields:
            cset[field] = str(cset_details[field]).replace('\n', '').replace('\t', '')
        print("...", end=" ")
        time.sleep(1)
        csets_items = get_csets_items(codeset_id)
        with open("all_csets_items.csv", "a", newline='') as f:
            writer = csv.writer(f)
            for item in csets_items['items']:
                item['exclude'] = item['isExcluded']
                row = [codeset_id, cset["n3c_recommended"]] + [item[field] for field in csets_items_fields] + [item['concept'][field] for field in csets_concept_fields]
                writer.writerow(row)
    with open("all_csets.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["codeset_id", "n3c_recommended"] + csets_details_fields)
        for cset in all_csets:
            row = [cset["codeset_id"], cset["n3c_recommended"]] + [cset[field] for field in csets_details_fields]
            writer.writerow(row)
    print("Updated all_csets.csv")

def main():

    # Create if nto exists a run metadata csv file that records the date and time of the run
    # if not os.path.exists("run_metadata.csv"):
    #     with open("run_metadata.csv", "w") as f:
    #         f.write("date, time\n")

    # # Get the date and time of the run
    # now = datetime.now()
    # date = now.strftime("%Y-%m-%d")
    # time = now.strftime("%H:%M:%S")

    # # Write the date and time to the run metadata file
    # with open("run_metadata.csv", "a") as f:
    #     f.write(f"{date}, {time}\n")

    # ######
        
    # # Get the N3C recommended codeset ids
    n3c_codeset_ids = get_n3c_recommended_codeset_ids()

    codesets = get_all_csets()[1000:1010]

    csets_items_fields = [
        "includeDescendants", "includeMapped", "exclude"
    ]
    csets_concept_fields = [
        "CONCEPT_ID", "CONCEPT_CLASS_ID", "CONCEPT_CODE", "CONCEPT_NAME", "DOMAIN_ID", "INVALID_REASON", "STANDARD_CONCEPT", "VOCABULARY_ID", "VALID_START_DATE", "VALID_END_DATE"
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
            "container_rid"
        ]

    with open("all_csets_items.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["codeset_id", "n3c_recommended"] + csets_items_fields + [field.lower() for field in csets_concept_fields])

    # Update the all_csets.csv file
    update_csets_file(codesets, n3c_codeset_ids, csets_items_fields, csets_concept_fields, csets_details_fields)


if __name__ == "__main__":
    main()