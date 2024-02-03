from prefect import flow

if __name__ == "__main__":
    flow.from_source(
        source="https://github.com/discdiver/demos.git",
        entrypoint="my_gh_workflow.py:repo_info",
    ).deploy(
        name="my-first-deployment",
        work_pool_name="my-managed-pool",
        cron="0 1 * * *",
    )
