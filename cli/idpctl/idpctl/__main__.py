import argparse
import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_API_URL = os.getenv("IDP_API_URL", "http://127.0.0.1:8000/api/v1")


def _request(method: str, path: str, payload: dict | None = None, api_url: str = DEFAULT_API_URL):
    body = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{api_url.rstrip('/')}{path}", data=body, method=method, headers=headers)

    try:
        with urlopen(request, timeout=10) as response:
            response_body = response.read().decode("utf-8")
            return json.loads(response_body) if response_body else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise SystemExit(f"API request failed ({exc.code}): {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach control plane at {api_url}: {exc.reason}") from exc


def _print_json(data: dict | list):
    print(json.dumps(data, indent=2))


def create_service(args):
    payload = {
        "service_name": args.name,
        "team": args.team,
        "environment": args.env,
    }
    result = _request("POST", "/services/", payload, args.api_url)
    _print_json(result)

    if args.wait:
        job_id = result["job"]["job_id"]
        wait_for_job(args.api_url, job_id, args.timeout)


def list_services(args):
    _print_json(_request("GET", "/services/", api_url=args.api_url))


def list_jobs(args):
    _print_json(_request("GET", "/jobs/", api_url=args.api_url))


def get_job(args):
    _print_json(_request("GET", f"/jobs/{args.job_id}", api_url=args.api_url))


def wait_for_job(api_url: str, job_id: str, timeout: int):
    deadline = time.time() + timeout

    while time.time() < deadline:
        job = _request("GET", f"/jobs/{job_id}", api_url=api_url)
        state = job["state"]

        if state in {"SUCCEEDED", "FAILED"}:
            _print_json(job)
            if state == "FAILED":
                raise SystemExit(1)
            return

        time.sleep(2)

    raise SystemExit(f"Timed out waiting for job {job_id}")


def build_parser():
    parser = argparse.ArgumentParser(prog="idpctl")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)

    subcommands = parser.add_subparsers(dest="command", required=True)

    create_parser = subcommands.add_parser("create-service")
    create_parser.add_argument("name")
    create_parser.add_argument("--team", required=True)
    create_parser.add_argument("--env", default="dev")
    create_parser.add_argument("--wait", action="store_true")
    create_parser.add_argument("--timeout", type=int, default=60)
    create_parser.set_defaults(func=create_service)

    services_parser = subcommands.add_parser("list-services")
    services_parser.set_defaults(func=list_services)

    jobs_parser = subcommands.add_parser("list-jobs")
    jobs_parser.set_defaults(func=list_jobs)

    job_parser = subcommands.add_parser("get-job")
    job_parser.add_argument("job_id")
    job_parser.set_defaults(func=get_job)

    return parser


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
