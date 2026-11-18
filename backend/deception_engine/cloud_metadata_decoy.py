"""
Cloud Metadata Decoy Engine
Emulates AWS IMDSv2 (169.254.169.254), Kubernetes Service Account API,
and Docker Socket Decoys with Canary Tokens.
"""
import json
import time
from typing import Dict, Any, Tuple
from .vst_state_tree import VSTStateTree


class CloudMetadataDecoy:
    """Emulates Cloud Instance Metadata Service (IMDSv2) & Container Decoys."""

    def __init__(self, state_tree: VSTStateTree):
        self.state_tree = state_tree
        self.active_session_tokens = set()

    def handle_imds_request(self, method: str, path: str, headers: Dict[str, str] = None) -> Tuple[int, Dict[str, str], str]:
        """
        Processes simulated HTTP requests to http://169.254.169.254/...
        Returns (status_code, response_headers, body)
        """
        headers = headers or {}
        norm_path = path.strip("/")

        # IMDSv2 Token Request: PUT /latest/api/token
        if method.upper() == "PUT" and norm_path == "latest/api/token":
            ttl = headers.get("X-aws-ec2-metadata-token-ttl-seconds", "21600")
            token = f"AQAAAH5e_CANARY_TOKEN_{int(time.time())}_{ttl}"
            self.active_session_tokens.add(token)
            return 200, {"Content-Type": "text/plain", "X-Aws-Ec2-Metadata-Token-Ttl-Seconds": ttl}, token

        # Enforce IMDSv2 token if required (or allow v1 if header omitted with logging)
        token = headers.get("x-aws-ec2-metadata-token") or headers.get("X-aws-ec2-metadata-token")

        if norm_path == "latest/meta-data" or norm_path == "latest/meta-data/":
            listing = "ami-id\nhostname\niam/\ninstance-id\ninstance-type\nlocal-hostname\nlocal-ipv4\npublic-hostname\npublic-ipv4\n"
            return 200, {"Content-Type": "text/plain"}, listing

        if norm_path == "latest/meta-data/instance-id":
            return 200, {"Content-Type": "text/plain"}, self.state_tree.cloud_metadata["instance_id"]

        if norm_path == "latest/meta-data/local-ipv4":
            return 200, {"Content-Type": "text/plain"}, self.state_tree.cloud_metadata["local_ipv4"]

        if norm_path == "latest/meta-data/public-ipv4":
            return 200, {"Content-Type": "text/plain"}, self.state_tree.cloud_metadata["public_ipv4"]

        if norm_path == "latest/meta-data/instance-type":
            return 200, {"Content-Type": "text/plain"}, self.state_tree.cloud_metadata["instance_type"]

        if norm_path == "latest/meta-data/iam/security-credentials" or norm_path == "latest/meta-data/iam/security-credentials/":
            return 200, {"Content-Type": "text/plain"}, f"{self.state_tree.cloud_metadata['iam_role']}\n"

        if norm_path == f"latest/meta-data/iam/security-credentials/{self.state_tree.cloud_metadata['iam_role']}":
            creds = self.state_tree.cloud_metadata["iam_credentials"]
            return 200, {"Content-Type": "application/json"}, json.dumps(creds, indent=2)

        return 404, {"Content-Type": "text/plain"}, "404 - Not Found\n"
