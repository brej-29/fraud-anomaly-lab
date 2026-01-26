from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RequestStats:
    total_requests: int = 0
    total_errors: int = 0
    latencies_ms: List[float] = field(default_factory=list)


@dataclass
class PredictionStats:
    total_predictions: int = 0
    total_flagged_ensemble: int = 0


class Metrics:
    """
    In-memory metrics store for lightweight observability.

    This is intentionally simple and process-local. It is not a replacement for a
    full metrics system, but provides enough signal for the `/metrics` endpoint
    and the dashboard.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests = RequestStats()
        self._predictions = PredictionStats()
        # Optional per-path request counters.
        self._requests_by_path: Dict[str, int] = {}

    def record_request(self, path: str, method: str, status_code: int, latency_s: float) -> None:
        """
        Record a single HTTP request.

        Parameters
        ----------
        path:
            Request path (e.g. "/predict").
        method:
            HTTP method (GET, POST, ...). Currently not broken out separately.
        status_code:
            Response status code.
        latency_s:
            Request latency in seconds.
        """
        latency_ms = latency_s * 1000.0
        with self._lock:
            self._requests.total_requests += 1
            if status_code >= 500:
                self._requests.total_errors += 1
            self._requests.latencies_ms.append(latency_ms)
            self._requests_by_path[path] = self._requests_by_path.get(path, 0) + 1

    def record_prediction(self, n_transactions: int, n_flagged_ensemble: int) -> None:
        """
        Record prediction activity for one API call.
        """
        with self._lock:
            self._predictions.total_predictions += int(n_transactions)
            self._predictions.total_flagged_ensemble += int(n_flagged_ensemble)

    def snapshot(self) -> Dict[str, object]:
        """
        Return a snapshot of current metrics suitable for JSON serialization.
        """
        with self._lock:
            latencies = list(self._requests.latencies_ms)
            total = len(latencies)
            if total:
                sorted_lat = sorted(latencies)
                p50 = sorted_lat[int(0.5 * (total - 1))]
                p90 = sorted_lat[int(0.9 * (total - 1))]
                p99 = sorted_lat[int(0.99 * (total - 1))]
                avg = sum(sorted_lat) / total
            else:
                p50 = p90 = p99 = avg = 0.0

            return {
                "requests": {
                    "total": self._requests.total_requests,
                    "errors": self._requests.total_errors,
                    "by_path": dict(self._requests_by_path),
                    "latency_ms": {
                        "avg": avg,
                        "p50": p50,
                        "p90": p90,
                        "p99": p99,
                    },
                },
                "predictions": {
                    "total_transactions": self._predictions.total_predictions,
                    "total_flagged_ensemble": self._predictions.total_flagged_ensemble,
                },
                "timestamp": time.time(),
            }


# Global singleton used by the app.
METRICS = Metrics()