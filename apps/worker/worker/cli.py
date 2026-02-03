import argparse
from worker.tasks.ingest_jira import ingest_jira
from worker.tasks.ingest_k8s import ingest_k8s
from worker.tasks.run_detectors import run_detectors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["ingest-jira", "ingest-k8s", "run-detectors"])
    args = p.parse_args()

    if args.cmd == "ingest-jira":
        print(ingest_jira.run())
    elif args.cmd == "ingest-k8s":
        print(ingest_k8s.run())
    elif args.cmd == "run-detectors":
        print(run_detectors.run())

if __name__ == "__main__":
    main()
