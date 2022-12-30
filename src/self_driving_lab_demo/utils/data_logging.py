import requests


def log_to_mongodb(
    document: dict,
    url: str,
    api_key: str,
    cluster_name: str,
    database_name: str,
    collection_name: str,
    verbose: bool = True,
    retries: int = 2,
):
    # based on
    # https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394 # noqa: E501
    headers = {"api-key": api_key}

    insertPayload = {
        "dataSource": cluster_name,
        "database": database_name,
        "collection": collection_name,
        "document": document,
    }

    if verbose:
        print(f"sending document to {cluster_name}:{database_name}:{collection_name}")

    for _ in range(retries):
        response = None
        if _ > 0:
            print(f"retrying... ({_} of {retries})")

        try:
            response = requests.request(
                "POST", url, headers=headers, data=insertPayload
            )

            if verbose:
                print(
                    f"Response: ({str(response.status_code)}), msg = {str(response.text)}"  # noqa: E501
                )
                if response.status_code == 201:
                    print("Added Successfully")
                    break
                else:
                    print("Error")

            # Always close response objects so we don't leak memory
            response.close()
        except Exception as e:
            if response is not None:
                response.close()
            if _ == retries - 1:
                raise e
            else:
                print(e)
