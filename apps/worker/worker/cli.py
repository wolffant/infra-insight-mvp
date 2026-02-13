import argparse
from worker.tasks.ingest_jira import ingest_jira
from worker.tasks.ingest_k8s import ingest_k8s
from worker.tasks.run_detectors import run_detectors
from worker.tasks.execute_actions import execute_approved_actions

def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["ingest-jira", "ingest-k8s", "run-detectors", "execute-actions"])
    args = p.parse_args()

    if args.cmd == "ingest-jira":
        print(ingest_jira.run())
    elif args.cmd == "ingest-k8s":
        print(ingest_k8s.run())
    elif args.cmd == "run-detectors":
        print(run_detectors.run())
    elif args.cmd == "execute-actions":
        print(execute_approved_actions.run())

if __name__ == "__main__":
    main()
