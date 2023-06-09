import os.path
from typing import List, Optional
from dataset_generation.src.metrics.edit_similarity import Metric
from dataset_generation.src.utils.utils import Version, clean_title


class Filter:
    def __init__(
        self,
        metric: Metric,
        similarity_threshold: float,
        report_path: Optional[str] = None,
    ):
        self.metric = metric
        self.similarity_threshold = similarity_threshold
        self.report_path = report_path
        if self.report_path is not None:
            mode = "w" if not os.path.exists(self.report_path) else "a"
            self.report_file = open(self.report_path, mode)

    def filter_versions(
        self,
        title: str,
        versions: List[Version],
    ):
        cleaned_title = clean_title(title, remove_parenthesis_content=True)
        scores = [self.metric.compute(v.title, cleaned_title) for v in versions]
        filtered_versions = [
            (i, version)
            for i, version in enumerate(versions)
            if version.title != "" and scores[i] > self.similarity_threshold
        ]
        sorted_filtered_versions = sorted(
            filtered_versions,
            key=lambda x: scores[x[0]],
            reverse=True,
        )
        sorted_filtered_versions = [v[1] for v in sorted_filtered_versions]
        if self.report_path is not None:
            discarded = [
                (title, v.title, score)
                for v, score in zip(versions, scores)
                if v not in sorted_filtered_versions
            ]
            if discarded:
                discarded_dump = "\n".join(
                    [f"{t[0]}\t{t[1]}\t{t[2]}" for t in discarded]
                )
                self.report_file.write(discarded_dump + "\n")
        return sorted_filtered_versions
